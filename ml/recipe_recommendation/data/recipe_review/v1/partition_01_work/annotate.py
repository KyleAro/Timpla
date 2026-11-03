import json
from pathlib import Path
D=Path(__file__).resolve().parent.parent
P=json.loads((D/'partition_01.json').read_text(encoding='utf-8'))
F=D/'partition_01_work'/'annotations.json'
A=json.loads(F.read_text()) if F.exists() else {}
def batch(a,b):
 for i in range(a,b): A[str(i)]={'scope':'in','scope_basis': 'The supplied dish identity and preparation describe a Filipino '+P[i]['name']+' variant.', 'status':'no_obvious_gap','basis':'Compared the supplied ingredient requirements with the cooking method; no material unexplained ingredient gap identified within this dataset text.','issues':[],'roles':{},'deps':[],'notes':[]}
def scope(i,d,b): A[str(i)].update(scope=d,scope_basis=b)
def issue(i,item,evidence,kind='missing_ingredient',status='gap_identified'):
 a=A[str(i)];a['status']=status;a['basis']='The supplied list and method contain the following unresolved inconsistency; original-source comparison remains pending.';a['issues'].append(dict(item=item,evidence=evidence,kind=kind))
def role(i,ids,r,b):
 for x in ids.split(','): A[str(i)]['roles'][x]=[r,b]
def dep(i,s): A[str(i)]['deps'].append(s)
def note(i,s): A[str(i)]['notes'].append(s)
def save():F.write_text(json.dumps(A,ensure_ascii=False,indent=2),encoding='utf-8')
if __name__ == '__main__':
    batch(0,50)

    scope(0,'out','Spanish-style squid-ink fideos/paellera preparation; supplied text provides no identifiable Filipino adaptation.')

    issue(0,'pepper','First method step seasons prawns with pepper, absent from all repeated ingredient sets.')

    dep(2,'Reserved pork broth is produced by boiling the listed pork; alternative chicken-stock poaching is an alternative path, not an additional mandatory purchase.')

    issue(2,'cooking water quantity','Method boils pork in 8 cups water and sauce in 2–3 cups; only the cornstarch dilution water is explicitly listed.','state_or_quantity','needs_review')

    dep(4,'Sisig is prepared from listed pork face and used in the rice stuffing; cooked and cooled rice is a prepared-state requirement.')

    role(6,'skin_on_chicken_thigh,skin_on_chicken_drumstick','essential','Required two pounds of chicken is the dish body; only extra wings are if desired, preserving the listed alternative expression.')

    issue(7,'pepper and ginger','Opening instruction tosses vegetables and shrimp with pepper and ginger, neither listed.')

    dep(8,'Sinigang stock is made from listed reserved prawn heads and crabs, then reused to cook paella rice; heads are not a separate prawn purchase.')

    issue(8,'water','Stock method adds 5 cups water, absent from list.')

    dep(9,'Beef broth is retained from cooking the listed brisket; cold day-old rice must already be cooked before frying.')

    role(9,'soy_sauce,brown_sugar','essential','Soy and sugar form the sweet soy braise that defines the pares component.')

    role(9,'garlic','essential','Garlic is defining in the included garlic fried rice; listed garlic quantities remain separate lines.')

    role(12,'tomato_sauce','essential','Tomato sauce forms the defining menudo braise rather than an optional condiment.')

    note(13,'Meatballs are listed as prepared topping; method offers desired toppings but supplies no meatball subrecipe. Do not infer raw meat equals prepared meatballs.')

    role(15,'calamansi','optional','Method explicitly makes the finishing calamansi drizzle if desired.')

    dep(17,'Rice is tossed briefly in olive oil; the method presupposes cooked rice although the ingredient says only white rice.')

    issue(17,'rice cooked state','White rice line lacks cooked state; brief tossing for olive rice presupposes cooked rice.','state_or_quantity','needs_review')

    dep(18,'Seven cups broth is reserved from cooking listed tripe and beef bones; fried garlic is a prepared topping.')

    role(18,'fried_garlic,calamansi','supporting','Finishing garnish/accompaniment; availability is still required unless source says optional.')

    scope(20,'out','Explicit Hong Kong-style brisket with hoisin, rice wine and egg noodles; no identifiable Filipino adaptation is supplied.')

    dep(21,'Leftover coating mix comes from the listed flour/starch mixture. Roast chicken drippings are a separately listed prepared input, not produced by frying these legs.')

    issue(21,'roast chicken drippings dependency','Gravy requires 1½ cups roast chicken drippings; no roasting subrecipe is given.','subrecipe_dependency','needs_review')

    issue(24,'cooking oil','Method heats oil for sautéing; no oil appears in ingredient lines.')

    dep(25,'Vegetable cooking liquid is retained for sauce, with listed water permitted to top up the liquid.')

    issue(26,'pepper quantity','Marinade pepper quantity is recorded as ? teaspoon.','state_or_quantity','needs_review')

    issue(27,'green peas versus green beans','Ingredient list says one can green beans; method adds canned green peas.','terminology','needs_review')

    note(27,'Olives and hard-boiled egg are explicitly if-desired garnishes, not mandatory ingredient gaps.')

    dep(27,'Shrimp-head stock is listed as prepared stock; method does not require a separate head purchase or equate it to uncooked shrimp.')

    issue(28,'red onion','Method combines chopped red onions in marinade; list provides only white onion subsequently sautéed.')

    role(28,'birds_eye_chili,chili_flakes','optional','Filling method explicitly labels the chili pepper or chili flakes optional; alternative preserved.')

    issue(29,'water','Bringhe method adds 3 cups water and adobo adds 4 cups, with no water line.')

    dep(29,'Crispy adobo flakes are made from listed pork and adobo liquids; leftover adobo is an explicitly offered alternative.')

    issue(30,'leeks versus spring onions','Ingredient line lists leeks; method repeatedly calls the white and green parts spring onions.','terminology','needs_review')

    scope(30,'in','Pancit preparation with calamansi accompaniment is an identifiable local Chinese-influenced noodle adaptation.')

    scope(31,'in','Despite carne-asada title, supplied pork-belly preparation with sweet saba bananas and rice identifies a local Filipino adaptation.')

    issue(31,'water','Method adds 5 cups water to braise pork; no water line supplied.')

    issue(35,'pig face and pepper','Method boils pig ear and face and later seasons with pepper; list has pig ears only and no pepper.')

    issue(36,'cornstarch','Sauce mixing step explicitly includes cornstarch, absent from list.')

    dep(37,'Reserve two cups liquid from goat simmering for the kaldereta sauce; liver spread is thinned with broth already in the pan.')

    role(37,'tomato_sauce','essential','Tomato sauce is the kaldereta sauce base in this supplied variant.')

    role(38,'soy_sauce,calamansi_juice','essential','Soy and calamansi are defining liquids of the explicitly named toyomansi glaze.')

    issue(41,'pepper quantity','Spicy-vinegar dip pepper quantity appears as ? teaspoon.','state_or_quantity','needs_review')

    dep(42,'Broth, scrap meat and marrow come from the listed pork/beef bones; marrow topping is if desired.')

    dep(43,'Reserved chicken broth comes from poaching the listed chicken, water and aromatics.')

    issue(44,'star anise, bay leaves, ginger and calabaza squash','Method adds star anise and bay leaves to oxtail, sautés ginger, and blanches calabaza squash; none is listed.')

    dep(44,'Hot meat broth is retained to build peanut sauce; listed optional tripe remains optional.')

    scope(45,'needs','Pineapple curry fried rice could be Thai-style or a local adaptation; supplied text provides insufficient Filipino-specific evidence.')

    issue(45,'eggs and fried shallots','Final step garnishes with chopped eggs and crispy fried shallots; no eggs listed and listed raw shallots have no frying preparation specified.','state_or_quantity','needs_review')

    scope(46,'in','Puttanesca is adapted with explicitly listed bagoong isda/Balayan, providing Filipino preparation evidence.')

    role(46,'tomato_sauce,canned_anchovy_in_oil,anchovy_sauce','essential','These supply the substantial tomato and anchovy/bagoong sauce that defines this adapted puttanesca.')

    scope(47,'in','Chicharon is explicitly mixed into pork meatballs as a substantive local adaptation.')

    role(48,'tomato,red_onion','essential','Tomato and sliced onion are substantive components tossed with grilled pork in the kilawin sauce.')

    issue(49,'whole peppercorns','Tripe boiling step requires whole peppercorns; list only gives unspecified salt and pepper to taste.','terminology','needs_review')

    dep(49,'Two cups broth is reserved from cooking the listed tripe; do not add purchased broth independently.')

    save()