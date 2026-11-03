exec(open(__file__.replace('batch2.py','record.py'),encoding='utf-8-sig').read().split("add(0,")[0])
for i,summary in {45:'Salmon heads, peanut base and vegetables align with the kare-kare method.',46:'Fish caldereta sauce and vegetables supplied; peas are listed but not incorporated in method.',47:'Bangus marinade and salsa are listed; prepared garlic fried rice has no subrecipe.',48:'Goto ingredients and separate tenderizing/cooking water are supplied.',49:'Reserved rib broth, tomato-liver sauce and vegetables match the method.',50:'Shrimp-shell tamarind sauce and noodles supplied but method requires unlisted salt.',51:'Salmon belly, souring mix and vegetables align.',52:'Dough and pork-asado filling have listed components.',53:'Noodle sauce, seafood stock and toppings can be made from the listed ingredients.',54:'Chicken marinade, tomato-liver sauce and vegetables align.',55:'Shrimp-shell tamarind sauce and noodles supplied but method requires unlisted salt.',56:'Coconut tomato chicken curry components align.',57:'Menudo pork, liver and vegetables align.',58:'Mixed-meat pochero and vegetables are supplied; fish bagoong is a serving accompaniment.',59:'Mixed-meat pochero with canned pork and beans aligns.',60:'Squid marinade and kaldereta sauce supplied.',61:'Pork menudo with hotdogs and liver matches method.',62:'Cubed beef, coconut-tomato sauce and vegetables align; beef cubes mean meat, not bouillon.',63:'Bistek marinade, onion rings and garlic rice are supplied.',64:'Chicken menudo with local hotdogs, tomato and vegetables aligns.'}.items():
 add(i,'I',I,summary)
a['45']['roles']={'E':[8],'S':[16,17]}
a['46']['roles']={'E':[6,7,14],'S':[16]};a['46']['notes']=['Green peas are listed but no incorporation step is supplied; optional garnish is not a required gap.']
a['47']['roles']={'E':[1],'S':[3,4,5,6,15]};a['47']['issues']=[['garlic red rice','Method calls for prepared garlic fried rice but no rice subrecipe or quantities of its constituents are supplied.','subrecipe_dependency']]
a['48']['roles']={'S':[7,12,14],'E':[9]}
a['49']['roles']={'E':[9,16,17]};a['49']['deps']=['Braising broth is retained from cooking the ribs in the listed water.']
for i in [50,55]:
 a[str(i)]['scope']='O';a[str(i)]['scope_basis']='Explicit pad Thai preparation with tamarind, rice noodles, shrimp shells and peanuts; no identifiable Filipino adaptation beyond local naming/citrus.';a[str(i)]['roles']={'S':[17]};a[str(i)]['issues']=[['salt','Method seasons chicken and egg with salt, absent from list.','missing_ingredient']];a[str(i)]['deps']=['Shrimp shells are retained from the listed shrimp and used to make the sauce base.']
a['51']['roles']={'S':[10]}
a['52']['roles']={'E':[1,10,11],'S':[14,15]}
a['53']['roles']={'S':[14,15]};a['53']['deps']=['Shrimp heads and retained shrimp boiling liquid make the listed shrimp stock; do not double-count stock purchase.']
a['54']['roles']={'E':[8,9,13],'S':[12]};a['54']['deps']=['Reserved pineapple-soy marinade returns to the sauce.']
a['56']['roles']={'E':[16],'S':[8,9]}
a['57']['roles']={'E':[6,13,14]}
a['58']['roles']={'E':[11]}
a['59']['roles']={'E':[12]}
a['60']['roles']={'E':[6,11],'S':[12]};a['60']['deps']=['Reserved vinegar marinade is returned to the stew.']
a['61']['roles']={'E':[6],'S':[11]}
a['62']['roles']={'E':[2,7,9]}
a['63']['roles']={'S':[10],'E':[13]};a['63']['deps']=['Rice is explicitly cooked and cooled before frying; preserve that state.']
a['64']['roles']={'E':[6,7]}
f.write_text(json.dumps(a,indent=2,ensure_ascii=False),encoding='utf-8')
