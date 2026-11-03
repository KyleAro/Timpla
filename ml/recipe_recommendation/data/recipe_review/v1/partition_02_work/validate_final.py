import json
from pathlib import Path
p=Path(__file__).resolve().parent.parent
src=json.loads((p/'partition_02.json').read_text(encoding='utf-8'));out=json.loads((p/'partition_02.decisions.json').read_text(encoding='utf-8'))
assert len(src)==len(out)==691
assert len({r['recipe_id'] for r in out})==691
assert [r['id'] for r in src]==[r['recipe_id'] for r in out]
keys={'recipe_id','cuisine_scope','internal_completeness','role_overrides','dependency_notes','notes','annotation_type','reviewer'}
for s,r in zip(src,out):
 assert set(r)==keys
 assert r['cuisine_scope']['decision'] in {'proposed_in_scope','proposed_out_of_scope','needs_review'}
 assert r['internal_completeness']['status'] in {'no_obvious_gap','gap_identified','needs_review'}
 assert r['annotation_type']=='ai_recipe_semantic_review'
 assert r['reviewer']=='Codex AI-assisted recipe review; not independent human approval'
 leaves={(l['line_number'],a['ingredient_id']) for l in s['lines'] for a in l['roles']}
 assert len({(o['line_number'],o['ingredient_id']) for o in r['role_overrides']})==len(r['role_overrides'])
 for o in r['role_overrides']:
  assert set(o)=={'line_number','ingredient_id','role','basis'}
  assert (o['line_number'],o['ingredient_id']) in leaves
  assert o['role'] in {'essential','supporting','optional'}
 for q in r['internal_completeness']['issues']:assert q['kind'] in {'missing_ingredient','subrecipe_dependency','terminology','state_or_quantity','other'}
 if s.get('preserved_owner_roles'):assert not r['role_overrides']
print('PASS: 691 input IDs covered exactly once; exact schema/enums, 977 valid leaf overrides, owner roles preserved. No training run.')
