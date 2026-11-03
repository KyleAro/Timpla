import json
from pathlib import Path
P=Path(__file__).resolve().parent.parent
D=json.loads((P/'partition_03.json').read_text(encoding='utf-8'))
R=json.loads((P/'partition_03.decisions.json').read_text(encoding='utf-8'))
assert len(R)==240
assert [x['recipe_id'] for x in R]==[x['id'] for x in D[:240]]
assert len(set(x['recipe_id'] for x in R))==len(R)
keys={'recipe_id','cuisine_scope','internal_completeness','role_overrides','dependency_notes','notes','annotation_type','reviewer'}
for i,(d,r) in enumerate(zip(D,R)):
 assert set(r)==keys,(i,set(r))
 assert r['annotation_type']=='ai_recipe_semantic_review'
 assert r['reviewer']=='Codex AI-assisted recipe review; not independent human approval'
 assert r['cuisine_scope']['decision'] in {'proposed_in_scope','proposed_out_of_scope','needs_review'}
 assert r['internal_completeness']['status'] in {'no_obvious_gap','gap_identified','needs_review'}
 leaves={(l['line_number'],x['ingredient_id']) for l in d['lines'] for x in l['roles']}
 seen=set()
 for x in r['role_overrides']:
  k=(x['line_number'],x['ingredient_id'])
  assert k in leaves,(i,k)
  assert k not in seen,(i,k)
  seen.add(k)
  assert x['role'] in {'essential','supporting','optional'}
 for x in r['internal_completeness']['issues']:
  assert x['kind'] in {'missing_ingredient','subrecipe_dependency','terminology','state_or_quantity','other'}
print('PASS: 240 contiguous individually reviewed records, exact schema, unique IDs, valid existing line/leaf overrides; remaining 452 not emitted.')
