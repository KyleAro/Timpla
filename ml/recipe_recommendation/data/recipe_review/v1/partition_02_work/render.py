import json
from collections import Counter
from pathlib import Path
p=Path(__file__).resolve().parent;d=json.loads((p.parent/'partition_02.json').read_text(encoding='utf-8'));a=json.loads((p/'annotations.json').read_text(encoding='utf-8'))
assert set(a)==set(map(str,range(len(d))))
out=[];owner_count=0
for i,r in enumerate(d):
 x=a[str(i)];byline={l['line_number']:l for l in r['lines']};ov={}
 for tag,entries in x['roles'].items():
  role={'E':'essential','S':'supporting','O':'optional'}[tag]
  for spec in entries:
   ln=spec if isinstance(spec,int) else spec[0];l=byline[ln]
   ids={rr['ingredient_id'] for rr in l['roles']} if isinstance(spec,int) else {spec[1]}
   assert ids.issubset({rr['ingredient_id'] for rr in l['roles']}),(i,spec)
   for iid in ids:
    draft=next(rr['proposed_role'] for rr in l['roles'] if rr['ingredient_id']==iid)
    if draft==role:continue
    key=(ln,iid);assert key not in ov or ov[key]['role']==role,(i,key)
    if role=='essential':basis=f'Defining or substantive component of {r["name"]}: {l["original_line"]}. Required for the listed variant.'
    elif role=='supporting':basis=f'Used as a supporting aromatic, seasoning, cooking medium or finishing garnish in {r["name"]}: {l["original_line"]}. Availability must still be disclosed and confirmed.'
    else:basis=f'Source explicitly makes this component conditional/optional in the ingredient line or method for {r["name"]}: {l["original_line"]}. This applies to this component, not a required base amount of another line.'
    ov[key]={'line_number':ln,'ingredient_id':iid,'role':role,'basis':basis}
 if r.get('preserved_owner_roles'):
  owner_count+=1
  assert not ov,(i,'Owner record must not be overridden')
 issues=[{'item':v[0],'evidence':v[1],'kind':v[2]} for v in x['issues']]
 status='gap_identified' if any(v['kind']=='missing_ingredient' for v in issues) else ('needs_review' if issues else 'no_obvious_gap')
 scope={'I':'proposed_in_scope','O':'proposed_out_of_scope','U':'needs_review'}[x['scope']]
 sb=x['scope_basis']
 if sb=='Recognizable Filipino preparation in the supplied dish and method.':sb=f'Supplied dish is {r["name"]}; the listed preparation is a recognizable Filipino/local dish or established local adaptation. '+x['summary']
 out.append({'recipe_id':r['id'],'cuisine_scope':{'decision':scope,'basis':sb},'internal_completeness':{'status':status,'basis':x['summary']+' Assessment is dataset-internal; original-source verification remains pending.','issues':issues},'role_overrides':sorted(ov.values(),key=lambda v:(v['line_number'],v['ingredient_id'])),'dependency_notes':x['deps'],'notes':x['notes'],'annotation_type':'ai_recipe_semantic_review','reviewer':'Codex AI-assisted recipe review; not independent human approval'})
f=p.parent/'partition_02.decisions.json';f.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
assert len(out)==len(d)==691;assert len({x['recipe_id'] for x in out})==691;assert {x['recipe_id'] for x in out}=={r['id'] for r in d}
print('Wrote',f.name,len(out),'records; owner role records preserved:',owner_count)
print('Scope',dict(Counter(x['cuisine_scope']['decision'] for x in out)))
print('Completeness',dict(Counter(x['internal_completeness']['status'] for x in out)))
print('Overrides',sum(len(x['role_overrides']) for x in out))
print('Normalization concerns',sum(any(n.startswith('Normalization concern:') for n in x['notes']) for x in out))
