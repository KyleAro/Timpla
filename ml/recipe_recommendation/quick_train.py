"""CPU training and testing using explicitly synthetic, rule-supervised inventories."""
import argparse
import hashlib
import json
from pathlib import Path
import random
import re
from functools import lru_cache

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT/'data/recipe_review/v1/recipes.draft.json'
FEATURES = ['inventory_use', 'supporting_coverage', 'missing_supporting', 'essential_count']
ALIASES = {'itlog':'egg','eggs':'egg','talong':'eggplant','chinese_eggplant':'eggplant',
           'kamatis':'tomato','tomatoes':'tomato','bawang':'garlic','sibuyas':'onion',
           'kanin':'cooked_rice','oil':'cooking_oil','mantika':'cooking_oil',
           'asin':'salt','toyo':'soy_sauce','suka':'vinegar','repolyo':'cabbage',
           'sayote':'chayote','upo':'bottle_gourd','patola':'sponge_gourd',
           'taro_root':'taro','ampalaya':'bitter_gourd'}


def norm(value):
    value = re.sub(r'\s+', '_', value.strip().lower())
    return ALIASES.get(value, value)


def ids(tree):
    if not tree:
        return set()
    if 'ingredient_id' in tree:
        return {norm(tree['ingredient_id'])}
    return set().union(*(ids(child) for key in ('all_of','any_of') for child in tree.get(key, [])))


def project(tree, roles, path=()):
    if not tree or 'equipment_id' in tree:
        return None
    if 'ingredient_id' in tree:
        return {'ingredient_id':norm(tree['ingredient_id'])} if roles.get(tuple(path)) == 'essential' else None
    key = next(iter(tree))
    children = [project(child, roles, path+(key,i)) for i,child in enumerate(tree[key])]
    # A nonessential alternative permits that branch; do not turn OR into AND.
    if key == 'any_of' and any(child is None for child in children):
        return None
    children = [child for child in children if child is not None]
    return {key:children} if children else None


def matches(tree, available):
    if tree is None:
        return True
    if 'ingredient_id' in tree:
        return norm(tree['ingredient_id']) in available
    if 'equipment_id' in tree:
        return True
    if 'any_of' in tree:
        return any(matches(child,available) for child in tree['any_of'])
    return all(matches(child,available) for child in tree.get('all_of',[]))


def catalog():
    recipes = json.loads(SOURCE.read_text(encoding='utf-8'))
    result = []
    for recipe in recipes:
        requirements, supporting, all_food = [], set(), set()
        for line in recipe['lines']:
            roles = {tuple(r['path']):r['proposed_role'] for r in line['roles']}
            tree = project(line['requirement'],roles)
            if tree:
                requirements.append(tree)
            supporting.update(norm(r['ingredient_id']) for r in line['roles'] if r['proposed_role']=='supporting')
            all_food.update(ids(line['requirement']))
        if not requirements:
            continue
        result.append({'id':recipe['id'],'name':recipe['name'], 'essential':{'all_of':requirements},
                       'supporting':sorted(supporting),'all_food':sorted(all_food),
                       'source_urls':recipe['source_urls'],
                       'scope_status':'unverified_candidate_from_Filipino_recipe_datasets'})
    return result


def vector(recipe, available):
    supporting = set(recipe['supporting'])
    return [len(set(recipe['all_food']) & available)/max(1,len(available)),
            len(supporting & available)/max(1,len(supporting)),
            len(supporting-available), len(ids(recipe['essential']))]


def synthetic_rating(x):
    score = .65*x[0]+.35*x[1]
    return min(3,int(score*4))


def metric(groups, predict):
    import math
    values=[]
    for rows in groups:
        scores=predict([x for x,y in rows])
        order=sorted(range(len(rows)),key=lambda i:-float(scores[i]))[:5]
        dcg=lambda ys:sum((2**y-1)/math.log2(i+2) for i,y in enumerate(ys))
        ideal=dcg(sorted([y for x,y in rows],reverse=True)[:5])
        values.append(dcg([rows[i][1] for i in order])/ideal if ideal else 0)
    return sum(values)/max(1,len(values))


def train(output, count, seed):
    import lightgbm as lgb
    import numpy as np
    if output.exists():
        raise ValueError('Output exists. Choose a new model folder.')
    recipes=catalog()
    print(f'Preparing automatic inventories from {len(recipes)} draft recipes...',flush=True)
    rng=random.Random(seed)
    pools=[];seen=set()
    for attempt in range(count*20):
        anchor=rng.choice(recipes)
        available=set(anchor['all_food'])
        # Vary supporting availability; never manufacture labels as human judgments.
        available -= {x for x in anchor['supporting'] if rng.random()<.5 and x not in ids(anchor['essential'])}
        if rng.random()<.5:
            available.update(rng.choice(recipes)['all_food'])
        key=tuple(sorted(available))
        if key in seen:
            continue
        seen.add(key)
        rows=[(vector(r,available),0) for r in recipes if matches(r['essential'],available)]
        rows=[(x,synthetic_rating(x)) for x,y in rows]
        if len(rows)<2 or len({y for x,y in rows})<2:
            continue
        pools.append((key,rows))
        if len(pools)%50==0:
            print(f'Prepared {len(pools)}/{count} informative inventories',flush=True)
        if len(pools)>=count:
            break
    if len(pools)<20:
        raise ValueError('Too few informative inventories; increase --inventories or improve recipe roles.')
    # Split broad ingredient-overlap families together, not individual candidates.
    families={}
    for key,rows in pools:
        signature=tuple(sorted(x for x in key if x not in {'salt','water','cooking_oil','black_pepper','garlic','onion'}))
        families.setdefault(signature,[]).append((key,rows))
    buckets=[[],[],[]]
    for signature,items in families.items():
        n=int(hashlib.sha256(json.dumps(signature).encode()).hexdigest()[:8],16)%100
        buckets[0 if n<70 else 1 if n<85 else 2].extend(items)
    if any(not b for b in buckets):
        raise ValueError('A split is empty. Increase inventories or change seed.')
    def flatten(bucket):
        return np.array([x for key,rows in bucket for x,y in rows]),np.array([y for key,rows in bucket for x,y in rows]),[len(rows) for key,rows in bucket]
    x,y,g=flatten(buckets[0]);vx,vy,vg=flatten(buckets[1])
    model=lgb.LGBMRanker(objective='lambdarank',n_estimators=150,num_leaves=7,
        min_child_samples=5,learning_rate=.05,n_jobs=2,random_state=seed,verbosity=-1)
    print('Training LightGBM on CPU...',flush=True)
    model.fit(x,y,group=g,eval_set=[(vx,vy)],eval_group=[vg],eval_at=[5],
              callbacks=[lgb.early_stopping(15,verbose=False)])
    if not any(model.booster_.feature_importance()):
        raise ValueError('Model learned no splits; improve scenario diversity.')
    output.mkdir(parents=True)
    model.booster_.save_model(str(output/'ranker.txt'))
    (output/'catalog.json').write_text(json.dumps(recipes,ensure_ascii=False,indent=2),encoding='utf-8')
    source_records=json.loads(SOURCE.read_text(encoding='utf-8'))
    included={r['id'] for r in recipes}
    report={'supervision':'synthetic rule-generated relevance; no human labels',
            'held_out_no_essential_requirement':[{'id':r['id'],'name':r['name']} for r in source_records if r['id'] not in included],
            'recipes':len(recipes),'inventory_groups':dict(zip(['train','validation','test'],map(len,buckets))),
            'features':FEATURES,'seed':seed,'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            'limitations':['Draft ingredient roles and cuisine scope need review.',
              'Exact inventories and nonpantry signatures stay together; similar inventories may still cross splits.',
              'Metrics measure reproduction of automatic rules, not real-user recommendation quality.',
              'No quantity, dependency, transformation or food-safety validation.']}
    for name,bucket in zip(['validation','test'],buckets[1:]):
        groups=[rows for key,rows in bucket]
        report[name]={'synthetic_ndcg_at_5':metric(groups,model.booster_.predict),
                      'rule_teacher_ndcg_at_5':metric(groups,lambda xs:[.65*x[0]+.35*x[1] for x in xs])}
    (output/'metadata.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    (output/'inventories.synthetic.json').write_text(json.dumps([
        {'available':list(key),'split':name} for name,b in zip(['train','validation','test'],buckets) for key,rows in b],indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2));print('Model saved:',output)


@lru_cache(maxsize=2)
def load_model(model_dir):
    import lightgbm as lgb
    return (json.loads((model_dir/'catalog.json').read_text(encoding='utf-8')),
            lgb.Booster(model_file=str(model_dir/'ranker.txt')))


def recommend(model_dir, ingredients, limit=5, excluded=()):
    display_by_id={}
    for value in ingredients:
        if isinstance(value,str) and value.strip():
            display_by_id.setdefault(norm(value),value.strip())
    available=set(display_by_id)
    if not available:
        return []
    excluded_ids = {norm(value) for value in excluded if isinstance(value, str) and value.strip()}
    recipes,booster=load_model(model_dir)
    selected=[r for r in recipes if not (set(r['all_food']) & excluded_ids) and matches(r['essential'],available)]
    if not selected:
        return []
    scores=booster.predict([vector(r,available) for r in selected])
    family_path = ROOT/'data/recipe_families.json'
    families = json.loads(family_path.read_text(encoding='utf-8')) if family_path.exists() else {}
    result=[]
    seen=set()
    ranked=sorted(zip(selected,scores),key=lambda pair:(-float(pair[1]),len(set(pair[0]['supporting'])-available),pair[0]['id']))
    for r,score in ranked:
        family=families.get(r['id'],r['id'])
        if family in seen:
            continue
        seen.add(family)
        missing=sorted(set(r['supporting'])-available)
        result.append({'id':r['id'],'name':r['name'],'ranking_score':float(score),
                       'used_ingredients':[display_by_id.get(x,x.replace('_',' ')) for x in sorted(available & set(r['all_food']))],
                       'missing_supporting':missing,'supporting_confirmation_needed':bool(missing),
                       'quantity_and_preparation_check_needed':True,'source_urls':r['source_urls'],
                       'note':'Experimental model trained on automatic labels; score is not a probability.'})
        if len(result)>=limit:
            break
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    fit=sub.add_parser('train');fit.add_argument('--output',type=Path,required=True)
    fit.add_argument('--inventories',type=int,default=300);fit.add_argument('--seed',type=int,default=42)
    test=sub.add_parser('recommend');test.add_argument('--model',type=Path,required=True)
    test.add_argument('--ingredients',nargs='+',required=True);test.add_argument('--limit',type=int,default=5)
    args=parser.parse_args()
    if args.command=='train':
        if args.inventories<20:parser.error('Use at least20 inventories.')
        train(args.output,args.inventories,args.seed)
    else:
        if args.limit<1:parser.error('limit must be positive')
        print(json.dumps(recommend(args.model,args.ingredients,args.limit),indent=2))


if __name__=='__main__':
    main()
