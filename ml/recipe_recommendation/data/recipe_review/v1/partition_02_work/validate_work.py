import json
from pathlib import Path
p=Path(__file__).resolve().parent;d=json.loads((p.parent/'partition_02.json').read_text(encoding='utf-8'));a=json.loads((p/'annotations.json').read_text(encoding='utf-8'))
print('Reviewed',len(a),'of',len(d));assert set(a)==set(map(str,range(len(d))))
errors=[]
for i,r in enumerate(d):
 byline={l['line_number']:l for l in r['lines']}
 for tag,entries in a[str(i)]['roles'].items():
  for spec in entries:
   ln=spec if isinstance(spec,int) else spec[0]
   if ln not in byline:errors.append((i,'missing line',spec));continue
   ids={x['ingredient_id'] for x in byline[ln]['roles']}
   if not isinstance(spec,int) and spec[1] not in ids:errors.append((i,'missing leaf',spec,ids))
print('Errors',errors)
