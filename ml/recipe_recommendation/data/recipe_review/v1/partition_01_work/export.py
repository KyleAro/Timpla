import json
from pathlib import Path
D=Path(__file__).resolve().parent.parent
P=json.loads((D/'partition_01.json').read_text(encoding='utf-8')); A=json.loads((D/'partition_01_work'/'annotations.json').read_text(encoding='utf-8'))
S={'paprika','dry_white_wine','parsley','cilantro','cilantro_leaf','fresh_parsley','fresh_cilantro','nonstick_cooking_spray','garlic_powder','onion_powder','dried_thyme','dried_oregano','dried_basil','ground_cumin','rosemary_leaf','maggi_magic_sarap','monosodium_glutamate','shortening','lightly_toasted_sesame_seed','sesame_seed','scallion','toasted_garlic','crispy_fried_garlic','fried_garlic','lemon','orange_zest','lemon_zest','honey','maple_syrup','brandy','fresh_oregano','sweet_basil_leaf','cilantro_root','shallot','sweet_onion'}
O=[]
for ik in sorted(A,key=int):
 i=int(ik);r=P[i];a=A[ik];over=[]
 owner=r['preserved_owner_roles'] or {}; ownerids=set(sum([v for v in owner.values() if isinstance(v,list)],[]))
 for l in r['lines']:
  for leaf in l['roles']:
   iid=leaf['ingredient_id']; existing=leaf['proposed_role'];change=a.get('line_roles',{}).get(str(l['line_number'])+':'+iid,a['roles'].get(iid))
   if change is None and iid in S and existing=='essential':change=['supporting','In '+r['name']+', this ingredient functions as seasoning, aromatic, cooking medium or finishing garnish; availability must still be confirmed.']
   if iid in ownerids:continue
   if change and change[0]!=existing:
    x={'line_number':l['line_number'],'ingredient_id':iid,'role':change[0],'basis':change[1]}
    if x not in over:over.append(x)
 O.append({'recipe_id':r['id'],'cuisine_scope':{'decision':{'in':'proposed_in_scope','out':'proposed_out_of_scope','needs':'needs_review'}[a['scope']],'basis':a['scope_basis']},'internal_completeness':{'status':a['status'],'basis':a['basis'],'issues':a['issues']},'role_overrides':over,'dependency_notes':a['deps'],'notes':a['notes'],'annotation_type':'ai_recipe_semantic_review','reviewer':'Codex AI-assisted recipe review; not independent human approval'})
(D/'partition_01.decisions.json').write_text(json.dumps(O,ensure_ascii=False,indent=2),encoding='utf-8')
nexti=next((i for i in range(len(P)) if str(i) not in A),len(P))
(D/'partition_01_work'/'progress.json').write_text(json.dumps({'verified_records':len(O),'next_index':nexti,'total':len(P),'complete':len(O)==len(P),'method':'Individual full ingredient and deduplicated instruction text inspected; output contains inspected records only.'},indent=2))
print('Exported',len(O),'next_index',nexti)
