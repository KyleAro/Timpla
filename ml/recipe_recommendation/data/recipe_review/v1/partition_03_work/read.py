import json,sys
from pathlib import Path
P=Path(__file__).resolve().parent.parent
D=json.loads((P/'partition_03.json').read_text(encoding='utf-8'))
if len(sys.argv)>1:
 a,b=map(int,sys.argv[1:3])
 for i,r in enumerate(D[a:b],a):
  print(f'\n[{i}] {r["name"]}')
  for l in r['lines']:
   print(str(l['line_number'])+' '+l['original_line']+' '+','.join(x['ingredient_id']+':'+x['proposed_role'][0] for x in l['roles']))
  print('METHOD: '+' | '.join(r['instructions']))
  if r['preserved_owner_roles']: print('OWNER:',r['preserved_owner_roles'])
