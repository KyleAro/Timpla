import json,sys
from pathlib import Path
p=Path(__file__).resolve().parent.parent
d=json.loads((p/'partition_02.json').read_text(encoding='utf-8'))
for i in range(int(sys.argv[1]),min(int(sys.argv[2]),len(d))):
 r=d[i];print('\n#'+str(i)+' '+r['name'])
 for l in r['lines']:
  print(str(l['line_number'])+' '+l['original_line']+' | '+','.join(x['ingredient_id']+':'+x['proposed_role'][0] for x in l['roles']))
 print('METHOD '+' '.join(r['instructions']))
 if r.get('preserved_owner_roles'): print('OWNER',r['preserved_owner_roles'])
