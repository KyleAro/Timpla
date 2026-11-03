import json
from pathlib import Path
p=Path(__file__).parent;a=json.loads((p/'annotations.json').read_text(encoding='utf-8'));d=json.loads((p.parent/'partition_02.json').read_text(encoding='utf-8'))
for i,ln,old,new,reason in [(11,19,'dried_romaine_lettuce','fresh Romaine lettuce, washed and surface-dried','Drying after washing is not dehydration.'),(35,2,'pork','pork_liver','Pork shares the liver head noun in the pork-or-beef alternative.'),(138,5,'chicken_tinola','raw chicken in tinola cut','Raw cut is not prepared tinola.'),(172,9,'pork','pork_stock','Pork shares the stock head noun in the pork-or-shrimp alternative.'),(239,1,'tuna','canned_tuna','Raw line explicitly specifies a can; method drains canned liquid.'),(340,10,'fish','fish_broth','Fish shares the broth head noun in the fish-or-shrimp alternative.')]:
 raw=next(l['original_line'] for l in d[i]['lines'] if l['line_number']==ln)
 a[str(i)]['notes'].append('Normalization concern: line '+str(ln)+' '+repr(raw)+' currently uses '+old+'; proposed identity '+new+'. '+reason+' Existing tree and ID retained for correction review.')
 if not any(x[2]=='other' and old in x[1] for x in a[str(i)]['issues']):a[str(i)]['issues'].append(['normalized identity',reason+' Current leaf '+old+' does not preserve supplied raw identity/state.','other'])
a['239']['summary']='Canned-tuna sisig method aligns with the raw can ingredient; normalized tuna leaf loses the canned state.'
a['239']['issues']=[x for x in a['239']['issues'] if x[0]!='tuna state']
a['172']['roles'].pop('E',None);a['340']['roles']={}
for i in [170,287,304,318,335]:a[str(i)]['notes'].append('Supplied source-text concern: ingredient wording and method differ; current leaf follows its raw line. Do not silently relabel this as a normalization correction.')
a['170']['issues'][0][2]='terminology'
(p/'annotations.json').write_text(json.dumps(a,indent=2,ensure_ascii=False),encoding='utf-8')
