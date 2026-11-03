import json,sys
from pathlib import Path
D=Path(__file__).resolve().parent.parent
p=json.loads((D/'partition_01.json').read_text(encoding='utf-8'))
if len(sys.argv)>1:
 a,b=map(int,sys.argv[1:3])
 for i in range(a,b):
  r=p[i]; print('\n#'+str(i)+' '+r['name'])
  seen={}
  for l in r['lines']:
   s=l['original_line']+' |'+','.join(x['ingredient_id']+':'+x['proposed_role'][0] for x in l['roles'])
   seen.setdefault(s,[]).append(str(l['line_number']))
  for s,ns in seen.items(): print('/'.join(ns)+' '+s)
  print('METHOD: '+' '.join(dict.fromkeys(r['instructions'])))
