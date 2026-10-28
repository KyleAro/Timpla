"""Ingredient-constrained recipe ranking. No image detection or app fallbacks."""
import csv
import hashlib
import json
import math
from pathlib import Path
import re

FEATURES = ['inventory_utilization', 'major_count', 'supporting_available_fraction',
            'missing_supporting_count', 'optional_available_fraction', 'use_first_coverage',
            'minutes', 'minutes_unknown', 'within_time_preference', 'region_match']
VERSION = 1


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def normalize(value, aliases):
    if not isinstance(value, str) or not value.strip():
        raise ValueError('Ingredient names must be nonempty strings')
    text = re.sub(r'\s+', ' ', value.strip().lower().replace('_', ' '))
    mapped = aliases.get(text, text)
    return re.sub(r'\s+', '_', mapped.strip().lower())


def ingredient_set(values, aliases):
    if not isinstance(values, list):
        raise ValueError('Ingredients must be a list')
    return {normalize(value, aliases) for value in values}


def validate_recipes(recipes, aliases, require_review=True):
    if not isinstance(recipes, list) or not recipes:
        raise ValueError('Provide a nonempty recipe collection')
    ids = set()
    for recipe in recipes:
        rid = recipe.get('id')
        if not isinstance(rid, str) or not rid.strip() or rid in ids:
            raise ValueError('Recipe IDs must be unique nonempty strings')
        ids.add(rid)
        if not recipe.get('name') or not str(recipe.get('source_url', '')).startswith('https://'):
            raise ValueError(f'{rid}: name and HTTPS source URL required')
        roles = [ingredient_set(recipe.get(role), aliases) for role in ('major', 'supporting', 'optional')]
        if not roles[0] or any(roles[i] & roles[j] for i in range(3) for j in range(i + 1, 3)):
            raise ValueError(f'{rid}: major ingredients required; roles must not overlap')
        minutes = recipe.get('minutes')
        if minutes is not None and (isinstance(minutes, bool) or not isinstance(minutes, (int, float)) or not math.isfinite(minutes) or minutes <= 0):
            raise ValueError(f'{rid}: minutes must be positive or null')
        if require_review and (not str(recipe.get('reviewed_by', '')).strip() or not str(recipe.get('reviewed_at', '')).strip()):
            raise ValueError(f'{rid}: ingredient roles need human review (reviewed_by and reviewed_at)')
    return recipes


def validate_query(query, aliases):
    available = ingredient_set(query.get('available'), aliases)
    urgent = ingredient_set(query.get('use_first', []), aliases)
    excluded = ingredient_set(query.get('excluded', []), aliases)
    if not urgent <= available:
        raise ValueError('use_first must be a subset of confirmed available ingredients')
    if available & excluded:
        raise ValueError('An ingredient cannot be both available and excluded')
    minutes = query.get('max_minutes')
    if minutes is not None and (isinstance(minutes, bool) or not isinstance(minutes, (float, int)) or not math.isfinite(minutes) or minutes <= 0):
        raise ValueError('max_minutes must be positive or null')
    return available, urgent, excluded


def eligible(recipe, query, aliases):
    available, _, excluded = validate_query(query, aliases)
    major, supporting, optional = [ingredient_set(recipe[role], aliases) for role in ('major', 'supporting', 'optional')]
    # Exact canonical membership; no automatic substitutions, raw/cooked conversion or meat-cut inference.
    return major <= available and not (major | supporting | optional) & excluded


def features(recipe, query, aliases):
    available, urgent, _ = validate_query(query, aliases)
    major, supporting, optional = [ingredient_set(recipe[role], aliases) for role in ('major', 'supporting', 'optional')]
    used = available & (major | supporting | optional)
    minutes = recipe.get('minutes')
    limit = query.get('max_minutes')
    preferred = query.get('preferred_region', '').strip().lower()
    return [len(used) / max(1, len(available)), len(major),
            len(supporting & available) / max(1, len(supporting)), len(supporting - available),
            len(optional & available) / max(1, len(optional)), len(urgent & used) / max(1, len(urgent)),
            minutes or 0, int(minutes is None), int(limit is not None and minutes is not None and minutes <= limit),
            int(bool(preferred) and preferred == recipe.get('region', '').strip().lower())]


def candidate_result(recipe, query, aliases):
    available, urgent, _ = validate_query(query, aliases)
    major = ingredient_set(recipe['major'], aliases)
    supporting = ingredient_set(recipe['supporting'], aliases)
    optional = ingredient_set(recipe['optional'], aliases)
    missing = sorted(supporting - available)
    return {'recipe_id': recipe['id'], 'name': recipe['name'], 'source_url': recipe['source_url'],
            'major_ingredients_available': sorted(major), 'missing_supporting': missing,
            'optional_available': sorted(optional & available),
            'uses_first': sorted(urgent & (major | supporting | optional)),
            'supporting_confirmation_needed': bool(missing), 'quantity_check_needed': True,
            'status': 'all_major_ingredients_available',
            'note': 'Check supporting ingredients and quantities; eligibility does not guarantee a complete meal or zero cost.'}


def candidates(recipes, query, aliases):
    validate_query(query, aliases)
    return [recipe for recipe in recipes if eligible(recipe, query, aliases)]


def judgment_context(recipe, query, aliases):
    # Reviewer identity and split assignment do not change the question being judged.
    available, urgent, excluded = validate_query(query, aliases)
    data = {'recipe':{key:value for key,value in recipe.items() if key not in ('reviewed_by','reviewed_at')},
            'query':{'available':sorted(available),'use_first':sorted(urgent),'excluded':sorted(excluded),
                     'max_minutes':query.get('max_minutes'),'preferred_region':query.get('preferred_region','')}}
    return hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()


def review_queue(recipes, queries, aliases, output):
    validate_recipes(recipes, aliases, require_review=False)
    # Queue is a draft for human review, never automatic relevance labels.
    seen = set()
    rows = []
    for query in queries:
        qid = query.get('id')
        if not isinstance(qid, str) or not qid.strip() or qid in seen:
            raise ValueError('Query IDs must be unique')
        seen.add(qid)
        for recipe in candidates(recipes, query, aliases):
            rows.append({'query_id': qid, 'recipe_id': recipe['id'], 'recipe_name': recipe['name'],
                         'available': '|'.join(query['available']), 'use_first': '|'.join(query.get('use_first', [])),
                         'missing_supporting': '|'.join(candidate_result(recipe, query, aliases)['missing_supporting']),
                         'source_url': recipe['source_url'], 'context_sha256':judgment_context(recipe,query,aliases), 'relevance': '', 'reviewer': '', 'notes': ''})
    path = Path(output)
    if path.exists():
        raise ValueError(f'Refusing to overwrite reviewer work: {path}')
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=['query_id','recipe_id','recipe_name','available','use_first','missing_supporting','source_url','context_sha256','relevance','reviewer','notes'])
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def fingerprint(recipes, aliases):
    data = json.dumps({'recipes': recipes, 'aliases': aliases}, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(data.encode()).hexdigest()


def training_groups(recipes, queries, labels_path, aliases):
    validate_recipes(recipes, aliases)
    labels = {}
    with Path(labels_path).open(encoding='utf-8-sig', newline='') as stream:
        for row in csv.DictReader(stream):
            key = row['query_id'], row['recipe_id']
            if key in labels or row.get('relevance') not in ('0','1','2','3') or not row.get('reviewer','').strip():
                raise ValueError(f'{key}: unique pair, human relevance 0-3 and reviewer required')
            labels[key] = (int(row['relevance']), row.get('context_sha256'))
    splits = {name: [] for name in ('train','validation','test')}
    seen_queries, family_splits, inventory_splits = set(), {}, {}
    used_labels = set()
    for query in queries:
        qid, split = query.get('id'), query.get('split')
        family = str(query.get('leakage_group','')).strip()
        if not isinstance(qid, str) or not qid.strip() or qid in seen_queries:
            raise ValueError('Unique query IDs required')
        seen_queries.add(qid)
        if split not in splits or not family or not str(query.get('reviewed_by','')).strip():
            raise ValueError(f'{qid}: assign split, leakage_group and reviewed_by')
        available, _, _ = validate_query(query, aliases)
        inventory = tuple(sorted(available))
        for bucket, key in ((family_splits, family), (inventory_splits, inventory)):
            if key in bucket and bucket[key] != split:
                raise ValueError(f'{qid}: related or identical inventories cross dataset splits')
            bucket[key] = split
        group = []
        for recipe in candidates(recipes, query, aliases):
            key = qid, recipe['id']
            if key not in labels:
                raise ValueError(f'Missing reviewed label for {key}')
            if labels[key][1] != judgment_context(recipe,query,aliases):
                raise ValueError(f'{key}: recipe/query changed since review queue; regenerate and review labels')
            used_labels.add(key)
            group.append({'x': features(recipe, query, aliases), 'y': labels[key][0], 'recipe_id': recipe['id']})
        if len(group) < 2 or len({row['y'] for row in group}) < 2 or not any(row['y'] >= 2 for row in group):
            raise ValueError(f'{qid}: need at least two eligible candidates, different ratings, and a relevant recipe (2 or 3)')
        splits[split].append({'query_id': qid, 'rows': group})
    if set(labels) != used_labels:
        raise ValueError('Labels contain unknown queries or recipes ineligible under current reviewed ingredient roles; regenerate and review the queue')
    if not all(splits.values()):
        raise ValueError('Separate nonempty train, validation and test query groups required')
    return splits


def ranking_metrics(groups, predict, k=5):
    ndcg, precision = [], []
    for group in groups:
        rows = group['rows']
        scores = predict([row['x'] for row in rows])
        order = sorted(range(len(rows)), key=lambda i: (-float(scores[i]), rows[i]['recipe_id']))[:k]
        actual = [rows[i]['y'] for i in order]
        ideal = sorted((row['y'] for row in rows), reverse=True)[:k]
        dcg = lambda values: sum((2 ** value - 1) / math.log2(index + 2) for index,value in enumerate(values))
        ndcg.append(dcg(actual) / dcg(ideal) if dcg(ideal) else 0)
        precision.append(sum(value >= 2 for value in actual) / len(actual))
    return {'ndcg_at_5': sum(ndcg)/len(ndcg), 'precision_at_up_to_5': sum(precision)/len(precision), 'query_count': len(groups)}


def train(recipes, queries, labels, aliases, output, input_paths):
    groups = training_groups(recipes, queries, labels, aliases)
    # Validate real reviewed inputs before importing optional training dependencies.
    import lightgbm as lgb
    import numpy as np
    def flatten(name):
        batches = groups[name]
        return (np.array([row['x'] for group in batches for row in group['rows']], dtype=float),
                np.array([row['y'] for group in batches for row in group['rows']]),
                [len(group['rows']) for group in batches])
    x,y,sizes = flatten('train')
    vx,vy,vsizes = flatten('validation')
    model = lgb.LGBMRanker(objective='lambdarank', n_estimators=200, num_leaves=7,
                          max_depth=3, min_child_samples=5, learning_rate=0.05,
                          reg_lambda=1.0, random_state=42, n_jobs=2,
                          deterministic=True, force_col_wise=True, verbosity=-1)
    model.fit(x,y,group=sizes,feature_name=FEATURES,eval_X=vx,eval_y=vy,eval_group=[vsizes],
              eval_at=[5],callbacks=[lgb.early_stopping(20,verbose=False)])
    if not any(model.booster_.feature_importance()):
        raise ValueError('No ranking splits learned; add more varied reviewed examples before exporting a model')
    target = Path(output)
    if target.exists():
        raise ValueError('Use a new versioned output directory; existing model artifacts will not be overwritten')
    target.mkdir(parents=True)
    model.booster_.save_model(str(target/'ranker.txt'))
    report = {split: ranking_metrics(groups[split], model.booster_.predict) for split in ('validation','test')}
    report['inventory_utilization_baseline'] = {split: ranking_metrics(groups[split],lambda xs:[x[0] for x in xs]) for split in ('validation','test')}
    metadata = {'version':VERSION,'algorithm':'LightGBM LambdaRank','features':FEATURES,
                'catalog_fingerprint':fingerprint(recipes,aliases),'lightgbm_version':lgb.__version__,
                'numpy_version':np.__version__,'parameters':model.get_params(),'best_iteration':model.best_iteration_,
                'relevance_scale':{'0':'unsuitable','1':'weak','2':'useful','3':'highly useful'},
                'input_sha256':{str(path):hashlib.sha256(Path(path).read_bytes()).hexdigest() for path in input_paths},
                'query_counts':{split:len(value) for split,value in groups.items()},
                'limitations':['Small datasets can overfit; metrics describe only the reviewed evaluation queries.',
                               'Major availability is enforced; supporting ingredients and quantities still need confirmation.',
                               'No automatic substitutions or food-safety/quantity assessment.']}
    (target/'metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
    (target/'evaluation.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


def recommend(recipes, query, aliases, model_dir, limit=5):
    validate_recipes(recipes, aliases)
    if not isinstance(limit,int) or isinstance(limit,bool) or limit <= 0:
        raise ValueError('limit must be a positive integer')
    metadata = read_json(Path(model_dir)/'metadata.json')
    if metadata.get('version') != VERSION or metadata.get('features') != FEATURES or metadata.get('catalog_fingerprint') != fingerprint(recipes,aliases):
        raise ValueError('Model metadata does not match the reviewed recipe collection/aliases; retrain before use')
    selected = candidates(recipes, query, aliases)
    if not selected:
        return []
    import lightgbm as lgb
    model = lgb.Booster(model_file=str(Path(model_dir)/'ranker.txt'))
    scores = model.predict([features(recipe,query,aliases) for recipe in selected])
    ranked = sorted(zip(selected,scores),key=lambda pair:(-float(pair[1]),pair[0]['id']))[:limit]
    return [{**candidate_result(recipe,query,aliases),'ranking_score':float(score),
             'score_note':'Relative learned ranking score; not a probability or accuracy percentage.'} for recipe,score in ranked]
