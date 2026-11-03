import json
from pathlib import Path
P=Path(__file__).resolve().parent.parent
D=json.loads((P/'partition_03.json').read_text(encoding='utf-8'))
O=P/'partition_03.decisions.json'
R=json.loads(O.read_text(encoding='utf-8')) if O.exists() else []
M={r['recipe_id']:r for r in R}
def add(i,scope='in',why='',status='ok',issues=[],over=[],deps=[],notes=[]):
 r=D[i]
 lookup={(l['line_number'],x['ingredient_id']):x for l in r['lines'] for x in l['roles']}
 os=[]
 for line,id,role,basis in over:
  assert (line,id) in lookup,(i,line,id)
  os.append(dict(line_number=line,ingredient_id=id,role=role,basis=basis))
 M[r['id']]=dict(recipe_id=r['id'],cuisine_scope=dict(decision={'in':'proposed_in_scope','out':'proposed_out_of_scope','?':'needs_review'}[scope],basis=why),internal_completeness=dict(status={'ok':'no_obvious_gap','gap':'gap_identified','?':'needs_review'}[status],basis=('Ingredient list and complete supplied method agree for this '+r['name']+' preparation; no material unexplained item identified.' if status=='ok' else 'Dataset-internal comparison identifies the issue(s) recorded below; original source comparison remains pending.'),issues=[dict(item=x[0],evidence=x[1],kind=x[2]) for x in issues]),role_overrides=os,dependency_notes=deps,notes=notes,annotation_type='ai_recipe_semantic_review',reviewer='Codex AI-assisted recipe review; not independent human approval')
def save():
 O.write_text(json.dumps([M[r['id']] for r in D if r['id'] in M],ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def ov(line,id,role='supporting',basis='Used as a supporting seasoning, aromatic or garnish in this method; availability still requires confirmation.'):
 return (line,id,role,basis)
def missing(item,evidence): return (item,evidence,'missing_ingredient')
def dep(item,evidence): return (item,evidence,'subrecipe_dependency')
def term(item,evidence): return (item,evidence,'terminology')
def state(item,evidence): return (item,evidence,'state_or_quantity')
