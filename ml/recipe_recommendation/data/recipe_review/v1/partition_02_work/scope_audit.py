import json
from pathlib import Path
p=Path(__file__).parent;a=json.loads((p/'annotations.json').read_text(encoding='utf-8'))
for i,b in {541:'Generic creamy mushroom pork chops use evaporated milk but do not establish a distinct Filipino adaptation.',598:'Buttered garlic shrimp is a generic preparation; supplied text gives insufficient Filipino adaptation evidence.',599:'Fish-sauce-poached fried chicken is contextual, but this generic spring-chicken text does not firmly identify a Filipino adaptation.',623:'Generic egg-and-flour breaded pork chops have no identifying Filipino adaptation beyond ordinary rice/ketchup service.',665:'Garlic-roasted squash and potatoes are generic roast vegetables; the word kalabasa alone does not establish a Filipino adaptation.',668:'Pureed cream sayote soup with chicken and ginger lacks sufficient identifying Filipino adaptation evidence.',685:'Salted grilled pompano with oil spray is generic; toyomansi serving suggestion alone does not establish a distinct Filipino preparation.'}.items():a[str(i)]['scope']='U';a[str(i)]['scope_basis']=b
a['100']['roles']['E']=[1,2,3,8]
a['502']['roles']['S'].append(9)
a['128']['issues'].append(['lemon balm incorporation','Named lemon balm is listed but main method only explicitly uses lemon-balm buds as garnish; leaf infusion/incorporation is not explained.','other'])
(p/'annotations.json').write_text(json.dumps(a,indent=2,ensure_ascii=False),encoding='utf-8')
