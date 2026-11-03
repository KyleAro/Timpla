import json,sys,re
from pathlib import Path
p=Path(__file__).resolve().parent.parent
d=json.loads((p/'partition_02.json').read_text(encoding='utf-8'))
stop=set('the a an to with and of in for or until then into from on your you it is as about at be them all this that these those by can will should have has while remaining over medium heat high low minutes minute seconds second stirring cook cooking continue add place remove set aside let bring boil simmer once well gently carefully make prepare transfer serve hot share enjoy before after start begin next now put return combine mix together finally ready occasionally regularly constantly through cooked'.split())
for i in range(int(sys.argv[1]),min(int(sys.argv[2]),len(d))):
 r=d[i];print('\n#'+str(i)+' '+r['name'])
 print('; '.join(str(l['line_number'])+(' OPTIONAL ' if 'optional' in l['original_line'].lower() else ':')+','.join(x['ingredient_id']+':'+x['proposed_role'][0] for x in l['roles']) for l in r['lines']))
 m=' '.join(r['instructions']);m=re.sub(r'\(([^)]*)\)',lambda v:v[0] if not any(w in v[0].lower() for w in ['ang ','mga ','hanggang ','para ','ilagay','lutuin','igisa','ihalo','dagdag','kung ','palamig','sigurad']) else '',m)
 m=' '.join(w for w in m.split() if w.lower().strip('.,:;') not in stop)
 print('M:',m)
 if r.get('preserved_owner_roles'):print('OWNER',r['preserved_owner_roles'])

