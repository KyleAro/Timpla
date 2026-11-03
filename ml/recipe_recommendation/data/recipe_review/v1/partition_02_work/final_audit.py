import json
from pathlib import Path
p=Path(__file__).parent;a=json.loads((p/'annotations.json').read_text(encoding='utf-8'));d=json.loads((p.parent/'partition_02.json').read_text(encoding='utf-8'))
def norm(i,ln,old,new,why):
 raw=next(l['original_line'] for l in d[i]['lines'] if l['line_number']==ln)
 note=f'Normalization concern: line {ln} {raw!r} currently uses {old}; proposed identity {new}. {why} Existing tree and ID retained for correction review.'
 if note not in a[str(i)]['notes']:a[str(i)]['notes'].append(note)
 a[str(i)]['issues'].append(['normalized state or identity',f'Line {ln}: {why} Current leaf {old}; proposed {new}.','other'])
for i,ln,old,new in [(0,42,'pimiento','canned pimiento'),(35,13,'garbanzo_bean','canned drained garbanzo beans'),(57,12,'garbanzo_bean','canned drained garbanzo beans'),(60,7,'green_pea','canned green peas'),(81,10,'young_corn','canned young corn'),(94,3,'chickpea','canned chickpeas'),(97,10,'baby_corn','canned drained baby corn'),(126,8,'pimiento','canned pimiento'),(152,5,'button_mushroom','canned button mushrooms'),(159,10,'green_jackfruit','canned drained green jackfruit'),(166,8,'whole_mushroom','canned drained whole mushrooms'),(187,4,'tomato','canned diced tomato'),(233,10,'tomato','canned crushed tomato'),(249,7,'fermented_black_bean','canned rinsed tausi'),(256,3,'tomato','canned diced tomato'),(355,8,'white_bean','canned drained white beans')]:norm(i,ln,old,new,'Raw line explicitly supplies a canned/prepared state not represented by the generic food leaf; preserve this state for availability matching.')
norm(502,9,'lemon','lemon soda (alternative to lime soda)','Shared head noun soda applies to both lemon and lime; whole lemon is not the stated drink.')
norm(618,5,'peppercorn','crushed peppercorn','Raw line explicitly says crushed; current leaf omits the preparation state.')
norm(619,1,'white_rice','cooked white rice, preferably leftovers','Raw line prefers leftovers and method immediately stir-fries rice; raw rice cannot substitute for cooked rice.')
# Source-list versus method contradictions are distinct from normalization failures.
a['514']['notes'].append('Supplied source-text concern: raw line 2 says 1 Cup mung bean sprouts (togue), and leaf mung_bean_sprout follows it; method instead rinses/boils dry mung beans. This is not a normalization error.')
a['402']['notes'].append('Supplied source-text concern: raw line 2 explicitly says 1 lb. grilled pork belly while method marinates and grills it; current grilled_pork_belly leaf follows raw wording.')
a['508']['notes'].append('Supplied source-text concern: raw pork line says use adobo cut, shredded, while method uses shredded pork/chicken adobo. Adobo cut alone does not establish a cooked dish.')
a['665']['summary']='Garlic-roasted squash and potatoes lack pepper; flattened ingredient text may duplicate potato requirements.'
a['665']['issues'][1]=['vegetable grouping','Line 1 combines squash and marble potatoes in all_of, and line 2 again lists potatoes; method roasts squash and potatoes separately. Quantities/grouping need clarification.','terminology']
a['665']['notes'].append('Current expression is all_of squash and marble_potato, not any_of; preserve it while reviewing flattened raw-line grouping.')
for i,r in enumerate(d):
 for l in r['lines']:
  if not l['terminology_review_required']:continue
  raw=l['original_line'];ids=', '.join(x['ingredient_id'] for x in l['roles'])
  a[str(i)]['notes'].append(f'Supplied terminology flag retained: line {l["line_number"]} {raw!r}; current identity {ids}. English label and source gloss require project terminology review; no source/tree correction or human approval asserted.')
  a[str(i)]['issues'].append(['source terminology',f'Line {l["line_number"]} is explicitly flagged for terminology review in input: {raw}.','terminology'])
a['0']['issues'].append(['calamansi juice quantity','Line 15 gives Calamansi Juice with no amount for the separate serving sauce.','state_or_quantity'])
(p/'annotations.json').write_text(json.dumps(a,indent=2,ensure_ascii=False),encoding='utf-8')
