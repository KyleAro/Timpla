"""Suggest identities for batch 05; never approve, merge, or train anything."""
import csv
from pathlib import Path
import re
from normalize_ingredients import ALIASES

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data/processed'

# Specific forms remain separate. These are proposals for owner review.
NAMES = '''
salt|salt
sea salt|sea_salt
coarse sea salt|coarse_sea_salt
coarse salt|coarse_salt
kosher salt|kosher_salt
rock salt|rock_salt
water|water
garlic|garlic
onion|onion
onions|onion
red onion|red_onion
red onions|red_onion
white onion|white_onion
white onions|white_onion
yellow onion|yellow_onion
yellow onions|yellow_onion
shallots|shallot
ginger|ginger
ginger powder|ginger_powder
ground black pepper|black_pepper
black pepper|black_pepper
ground white pepper|ground_white_pepper
white pepper|white_pepper
peppercorn|peppercorn
peppercorns|peppercorn
whole peppercorns|peppercorn
black peppercorns|black_peppercorn
whole black peppercorns|black_peppercorn
garlic powder|garlic_powder
onion powder|onion_powder
cooking oil|cooking_oil
oil|cooking_oil
vegetable cooking oil|vegetable_oil
vegetable oil|vegetable_oil
canola oil|canola_oil
olive oil|olive_oil
extra virgin olive oil|extra_virgin_olive_oil
sesame oil|sesame_oil
peanut oil|peanut_oil
corn oil|corn_oil
refined coconut oil|refined_coconut_oil
soy sauce|soy_sauce
dark soy sauce|dark_soy_sauce
light soy sauce|light_soy_sauce
low-sodium soy sauce|low_sodium_soy_sauce
japanese soy sauce|japanese_soy_sauce
fish sauce|fish_sauce
patis|fish_sauce
oyster sauce|oyster_sauce
tomato sauce|tomato_sauce
tomato paste|tomato_paste
tomato ketchup|tomato_ketchup
banana ketchup|banana_ketchup
ketchup|ketchup
liquid seasoning|liquid_seasoning
knorr liquid seasoning|knorr_liquid_seasoning
vinegar|vinegar
white vinegar|white_vinegar
cane vinegar|cane_vinegar
coconut vinegar|coconut_vinegar
rice vinegar|rice_vinegar
balsamic vinegar|balsamic_vinegar
apple cider vinegar|apple_cider_vinegar
sherry vinegar|sherry_vinegar
white wine vinegar|white_wine_vinegar
palm vinegar|palm_vinegar
red cane vinegar|red_cane_vinegar
spiced vinegar|spiced_vinegar
sweet chili sauce|sweet_chili_sauce
hoisin sauce|hoisin_sauce
worcestershire sauce|worcestershire_sauce
hot sauce|hot_sauce
chili garlic sauce|chili_garlic_sauce
chili-garlic sauce|chili_garlic_sauce
mayonnaise|mayonnaise
peanut butter|peanut_butter
pickle relish|pickle_relish
sweet pickle relish|sweet_pickle_relish
barbecue sauce|barbecue_sauce
store-bought barbecue sauce|barbecue_sauce
lechon sauce|lechon_sauce
liver spread|liver_spread
sugar|sugar
white sugar|white_sugar
brown sugar|brown_sugar
dark brown sugar|dark_brown_sugar
coconut sugar|coconut_sugar
palm sugar|palm_sugar
muscovado sugar|muscovado_sugar
honey|honey
all-purpose flour|all_purpose_flour
all purpose flour|all_purpose_flour
flour|flour
cornstarch|cornstarch
corn starch|cornstarch
rice flour|rice_flour
glutinous rice flour|glutinous_rice_flour
potato starch|potato_starch
baking powder|baking_powder
bread crumbs|bread_crumbs
breadcrumbs|bread_crumbs
panko bread crumbs|panko_bread_crumbs
flour tortillas|flour_tortilla
lumpia wrapper|lumpia_wrapper
lumpia wrappers|lumpia_wrapper
spring roll lumpia wrappers|lumpia_wrapper
butter|butter
unsalted butter|unsalted_butter
salted butter|salted_butter
margarine|margarine
milk|milk
whole milk|whole_milk
fresh milk|fresh_milk
evaporated milk|evaporated_milk
buttermilk|buttermilk
cream|cream
heavy cream|heavy_cream
all-purpose cream|all_purpose_cream
coconut milk|coconut_milk
coconut cream|coconut_cream
cheese|cheese
cheddar cheese|cheddar_cheese
sharp cheddar cheese|sharp_cheddar_cheese
mozzarella cheese|mozzarella_cheese
parmesan cheese|parmesan_cheese
quick-melting cheese|quick_melting_cheese
egg|egg
eggs|egg
raw egg|egg
raw eggs|egg
hard boiled eggs|hard_boiled_egg
boiled eggs|boiled_egg
fried eggs|fried_egg
salted eggs|salted_egg
quail eggs|quail_egg
boiled quail eggs|boiled_quail_egg
chicken|chicken
whole chicken|whole_chicken
ground chicken|ground_chicken
chicken wings|chicken_wing
chicken liver|chicken_liver
chicken livers|chicken_liver
chicken breast|chicken_breast
chicken broth|chicken_broth
chicken stock|chicken_stock
chicken bouillon cube|chicken_bouillon_cube
chicken cube|chicken_seasoning_cube
chicken powder|chicken_powder
knorr chicken cube|knorr_chicken_cube
knorr pork cube|knorr_pork_cube
knorr pork cubes|knorr_pork_cube
knorr beef cube|knorr_beef_cube
knorr shrimp cube|knorr_shrimp_cube
beef bouillon cube|beef_bouillon_cube
pork bouillon cube|pork_bouillon_cube
pork bouillon cubes|pork_bouillon_cube
shrimp bouillon cube|shrimp_bouillon_cube
shrimp bouillon|shrimp_bouillon
shrimp cube|shrimp_seasoning_cube
beef|beef
ground beef|ground_beef
beef chuck|beef_chuck
beef shank|beef_shank
beef tripe|beef_tripe
beef short ribs|beef_short_rib
beef sirloin|beef_sirloin
beef stock|beef_stock
beef broth|beef_broth
pork|pork
ground pork|ground_pork
pork belly|pork_belly
whole pork belly|whole_pork_belly
pork shoulder|pork_shoulder
pork pigue|pork_pigue
pork leg|pork_leg
whole pork leg|whole_pork_leg
pork chops|pork_chop
pork chop|pork_chop
pork ribs|pork_rib
pork spare ribs|pork_spare_rib
pork liver|pork_liver
pig liver|pork_liver
pork blood|pork_blood
pork fat|pork_fat
pork intestine|pork_intestine
pig ears|pig_ear
pigs brain|pig_brain
pork stock|pork_stock
pork broth|pork_broth
vegetable stock|vegetable_stock
vegetable broth|vegetable_broth
fish stock|fish_stock
shrimp stock|shrimp_stock
shrimp juice|shrimp_juice
shrimp|shrimp
shrimps|shrimp
shrimp paste|shrimp_paste
sauteed shrimp paste|sauteed_shrimp_paste
dried shrimp|dried_shrimp
prawns|prawn
tiger prawns|tiger_prawn
squid|squid
squid ink|squid_ink
mussels|mussel
green mussels|green_mussel
crabmeat|crabmeat
fish fillet|fish_fillet
salmon fillet|salmon_fillet
salmon fillets|salmon_fillet
tilapia|tilapia
tilapia fillets|tilapia_fillet
tanigue steaks|tanigue_steak
pompano|pompano
tofu|tofu
cabbage|cabbage
napa cabbage|napa_cabbage
bok choy|bok_choy
baby bok choy|baby_bok_choy
pechay|pechay
pechay leaves|pechay
pechay tagalog|pechay_tagalog
spinach|spinach
baby spinach|baby_spinach
fresh spinach|spinach
eggplant|eggplant
eggplants|eggplant
chinese eggplant|chinese_eggplant
chinese eggplants|chinese_eggplant
carrot|carrot
carrots|carrot
tomato|tomato
tomatoes|tomato
ripe tomatoes|tomato
ripe tomato|tomato
roma tomato|roma_tomato
roma tomatoes|roma_tomato
plum tomato|plum_tomato
plum tomatoes|plum_tomato
native tomato|native_tomato
native tomatoes|native_tomato
potato|potato
potatoes|potato
baking potato|baking_potato
sweet potato|sweet_potato
okra|okra
bell pepper|bell_pepper
red bell pepper|red_bell_pepper
red bell peppers|red_bell_pepper
green bell pepper|green_bell_pepper
chili peppers|chili_pepper
red chili pepper|red_chili_pepper
red chilies|red_chili
green chili|green_chili
long green pepper|long_green_pepper
long green peppers|long_green_pepper
long green chili|long_green_chili
long green chilies|long_green_chili
thai chili|thai_chili
thai chili pepper|thai_chili
thai chili peppers|thai_chili
finger chilies|finger_chili
finger chili peppers|finger_chili
siling pangsigang|siling_pangsigang
siling pansigang|siling_pangsigang
siling labuyo|siling_labuyo
chili powder|chili_powder
chili flakes|chili_flakes
red chili pepper flakes|red_chili_pepper_flakes
red pepper flakes|red_pepper_flakes
cayenne pepper|cayenne_pepper
cayenne pepper powder|cayenne_pepper_powder
green peas|green_pea
frozen green peas|frozen_green_pea
snow peas|snow_pea
snap peas|snap_pea
green beans|green_bean
long green beans|long_green_bean
string beans|sitaw
snake beans|sitaw
sitaw|sitaw
green olives|green_olive
manzanilla olives|manzanilla_olive
shiitake mushrooms|shiitake_mushroom
cauliflower florets|cauliflower_floret
malunggay leaves|malunggay_leaves
fresh malunggay leaves|malunggay_leaves
kangkong|kangkong
kangkong leaves|kangkong_leaves
water spinach|kangkong
mustard leaves|mustard_leaves
mustard greens|mustard_greens
lemongrass|lemongrass
mint leaves|mint_leaves
cilantro|cilantro
parsley|parsley
flat leaf parsley|flat_leaf_parsley
chopped flat leaf parsley|flat_leaf_parsley
parsley leaves|parsley_leaves
scallions|spring_onion
spring onions|spring_onion
green onions|spring_onion
green onion|spring_onion
leeks|leek
chives|chive
celery|celery
pandan leaf|pandan_leaf
bay leaf|bay_leaf
bay leaves|bay_leaf
laurel leaf|bay_leaf
laurel leaves|bay_leaf
dried bay leaf|dried_bay_leaf
dried bay leaves|dried_bay_leaf
star anise|star_anise
paprika|paprika
spanish paprika|spanish_paprika
sweet paprika|sweet_paprika
smoked paprika|smoked_paprika
curry powder|curry_powder
yellow curry powder|yellow_curry_powder
cumin|cumin
ground cumin|ground_cumin
turmeric powder|turmeric_powder
ground turmeric|ground_turmeric
dried oregano|dried_oregano
italian seasoning|italian_seasoning
five-spice powder|five_spice_powder
chinese five-spice powder|chinese_five_spice_powder
saffron|saffron
whole cloves|whole_clove
cinnamon stick|cinnamon_stick
annatto seeds|annatto_seed
annatto oil|annatto_oil
annatto powder|annatto_powder
atsuete oil|annatto_oil
atsuete seeds|annatto_seed
rice|rice
uncooked rice|rice
white rice|white_rice
brown rice|brown_rice
short-grain rice|short_grain_rice
paella rice|paella_rice
cooked white rice|cooked_white_rice
steamed rice|cooked_rice
garlic fried rice|garlic_fried_rice
sinangag|garlic_fried_rice
rice washing|rice_washing
rice wine|rice_wine
white wine|white_wine
dry white wine|dry_white_wine
red wine|red_wine
chinese rice wine|chinese_rice_wine
mirin|mirin
calamansi|calamansi
calamansi juice|calamansi_juice
lemon|lemon
lemon juice|lemon_juice
lime|lime
lime juice|lime_juice
pineapple juice|pineapple_juice
unsweetened pineapple juice|unsweetened_pineapple_juice
pineapple chunks|pineapple_chunks
apple juice|apple_juice
orange juice|orange_juice
orange zest|orange_zest
lemon-lime soda|lemon_lime_soda
raisins|raisin
peanuts|peanut
unsalted peanuts|unsalted_peanut
roasted peanuts|roasted_peanut
unsalted peanuts ground|ground_unsalted_peanut
sesame seeds|sesame_seed
toasted sesame seeds|toasted_sesame_seed
mung beans|mung_bean
kamias|kamias
ampalaya|ampalaya
ampalaya leaves|ampalaya_leaves
upo|upo
kalabasa|kalabasa
butternut squash|butternut_squash
unripe tamarind|unripe_tamarind
unripe jackfruit|unripe_jackfruit
green papaya|green_papaya
unripe papaya|unripe_papaya
sago|sago
vanilla extract|vanilla_extract
miso paste|miso_paste
yellow miso paste|yellow_miso_paste
misua noodles|misua_noodles
miswa noodles|misua_noodles
fresh miki noodles|fresh_miki_noodles
miki noodles|miki_noodles
lomi noodles|lomi_noodles
pancit canton noodles|pancit_canton_noodles
pancit bihon|pancit_bihon
pancit bato|pancit_bato
chorizo de bilbao|chorizo_de_bilbao
chinese sausage|chinese_sausage
fried garlic bits|fried_garlic
toasted garlic|toasted_garlic
store-bought toasted garlic chips|toasted_garlic_chip
salted black beans|salted_black_bean
ube flavoring|ube_flavoring
'''
BASE = dict(line.split('|') for line in NAMES.strip().splitlines())
BASE.update({
    'fresh coconut milk': 'fresh_coconut_milk', 'frozen sweet peas': 'frozen_sweet_pea',
    'native vinegar': 'native_vinegar', 'cider vinegar': 'cider_vinegar',
    'sriracha hot sauce': 'sriracha_hot_sauce', 'cooking rice wine': 'cooking_rice_wine',
    'cold water': 'cold_water', 'ice-cold water': 'ice_cold_water', 'warm water': 'warm_water',
    'hot water': 'hot_water', 'egg yolks': 'egg_yolk', 'egg whites': 'egg_white',
    'melted butter': 'melted_butter', 'unsalted butter melted': 'melted_unsalted_butter',
    'chicharon': 'chicharon', 'leftover adobo sauce': 'leftover_adobo_sauce',
    'dried banana blossoms': 'dried_banana_blossom', 'crab fat aligue': 'crab_aligue',
    'cooking oil spray': 'cooking_oil_spray', 'chicken fillets': 'chicken_fillet',
    'chicken thighs': 'chicken_thigh', 'chicken leg quarters': 'chicken_leg_quarter',
    'sotanghon noodles': 'sotanghon_noodles', 'tinapa flakes': 'tinapa_flakes',
    'string beans': 'string_bean', 'snake beans': 'snake_bean',
    'fresh basil leaves': 'fresh_basil_leaves', 'lettuce leaves': 'lettuce_leaves',
    'thick rice noodles': 'thick_rice_noodles', 'uncooked spaghetti': 'uncooked_spaghetti',
    'sinigang na gabi mix': 'sinigang_na_gabi_mix',
    'sinigang sa sampalok mix': 'sinigang_sa_sampalok_mix',
    'sinigang sa sampaloc mix': 'sinigang_sa_sampalok_mix',
    'coconut oil': 'coconut_oil', 'dried thai chili': 'dried_thai_chili',
    'mustard leaves mustasa': 'mustard_leaves', 'sinigang mix': 'sinigang_mix',
    'dried anchovies': 'dried_anchovy', 'salted egg': 'salted_egg',
    'garbanzo beans': 'garbanzo_bean', 'garbanzos': 'garbanzo_bean',
    'puso ng saging banana blossom': 'banana_blossom',
    'mung bean sprouts': 'mung_bean_sprout', 'monggo sprouts': 'mung_bean_sprout',
    'lemon lime soda': 'lemon_lime_soda', '7-up': 'seven_up',
    'maggi magic sarap': 'maggi_magic_sarap', 'knorr savorrich pork': 'knorr_savorrich_pork',
    'barbecue marinade': 'barbecue_marinade', 'papaya atchara': 'papaya_atsara',
    'pickled vegetables atsara': 'atsara', 'kesong puti white cheese': 'kesong_puti',
    'whole milkfish': 'whole_milkfish', 'mud crabs': 'mud_crab',
    'tiger prawns sugpo': 'tiger_prawn', 'shiitake mushroom': 'shiitake_mushroom',
})

# Parenthetical translations are accepted only when explicitly listed here.
TRANSLATIONS = {
    'garlic': ['bawang'], 'onion': ['sibuyas'], 'red onion': ['sibuyas'],
    'white onion': ['sibuyas'], 'tomato': ['kamatis'], 'tomatoes': ['kamatis'],
    'roma tomatoes': ['kamatis'], 'potatoes': ['patatas'], 'potato': ['patatas'],
    'ginger': ['luya'], 'salt': ['asin'], 'sea salt': ['asin'], 'rock salt': ['asin'],
    'soy sauce': ['toyo'], 'fish sauce': ['patis'], 'patis': ['fish sauce'],
    'white vinegar': ['suka', 'sukang puti'], 'vinegar': ['suka'],
    'cane vinegar': ['suka'], 'cooking oil': ['mantika'], 'oil': ['mantika'],
    'canola oil': ['mantika'], 'sugar': ['asukal'], 'brown sugar': ['asukal na pula'],
    'coconut milk': ['gata'], 'coconut cream': ['kakang gata', 'kakang-gata'],
    'malunggay leaves': ['moringa'], 'lemongrass': ['tanglad'],
    'cilantro': ['wansoy'], 'bay leaf': ['dahon ng laurel'], 'bay leaves': ['dahon ng laurel'],
    'dried bay leaves': ['dahon ng laurel'], 'black pepper': ['paminta'],
    'ground black pepper': ['paminta', 'dinurog na paminta'],
    'whole black peppercorns': ['paminta', 'pamintang buo'],
    'peppercorns': ['paminta'], 'whole peppercorns': ['paminta', 'pamintang buo'],
    'pork belly': ['liempo'], 'pork shoulder': ['kasim'],
    'pork liver': ['atay ng baboy'], 'ground pork': ['giniling na baboy'],
    'chicken': ['manok'], 'shrimp': ['hipon'], 'squid': ['pusit'],
    'mussels': ['tahong'], 'green mussels': ['tahong'], 'prawns': ['sugpo'],
    'raisins': ['pasas'], 'green peas': ['gisantes'], 'snow peas': ['sitsaro'],
    'shallots': ['sibuyas tagalog'], 'butter': ['mantikilya'], 'whole milk': ['gatas'],
    'shrimp paste': ['bagoong alamang', 'bagoong'], 'sitaw': ['string beans'],
    'string beans': ['sitaw'], 'long green beans': ['sitaw'], 'snake beans': ['sitaw'],
}

EXACT = {
    'bundle kangkong water spinach leaves': ['kangkong_leaves'],
    'finger chilies siling pangsigang sliced': ['siling_pangsigang'],
    'green finger chili siling haba': ['siling_haba'],
    'long green chilies siling pangsigang': ['siling_pangsigang'],
    'finger chilies siling haba': ['siling_haba'],
    'green finger chilies siling pangsigang': ['siling_pangsigang'],
    'long green chili siling pansigang': ['siling_pangsigang'],
    'freshly ground black pepper dinurog na paminta': ['black_pepper'],
    'frozen green peas thawed': ['frozen_green_pea'],
    'green peas thawed': ['thawed_green_pea'],
    'fresh calamansi juice': ['fresh_calamansi_juice'],
    'juice of 1 lemon': ['lemon_juice'],
    'long beans sitaw ends trimmed and cut into 3-inch lengths': ['sitaw'],
    'all-purpose flour arina': ['all_purpose_flour'],
    'anchovy sauce bagoong isda': ['anchovy_sauce'],
    'annatto oil atsuete oil': ['annatto_oil'],
    'annatto powder atsuete': ['annatto_powder'],
    'banana ketchup banana catsup': ['banana_ketchup'],
    'beef chuck paypay cubed': ['beef_chuck'],
    'beef shank bulalo': ['beef_shank'],
    'black peppercorns lightly crushed': ['crushed_black_peppercorn'],
    'butter melted': ['melted_butter'],
    'chili leaves dahon ng sili': ['chili_leaves'],
    'dried anchovies dilis': ['dried_anchovy'],
    'egg yolks only': ['egg_yolk'],
    'eggplants talong': ['eggplant'],
    'garbanzo beans garbanzos': ['garbanzo_bean'],
    'garlic whole': ['whole_garlic'],
    'garlic crushed bawang': ['garlic'],
    'garlic minced bawang dinurog': ['garlic'],
    'garlic peeled and minced bawang': ['garlic'],
    'garlic rice to serve': ['garlic_fried_rice'],
    'glutinous rice malagkit rinsed': ['glutinous_rice'],
    'hardboiled eggs peeled and quartered': ['hard_boiled_egg'],
    'hotdogs sliced diagonally': ['hotdog'],
    'japanese breadcrumbs panko': ['panko_bread_crumbs'],
    'kamias bilimbi': ['kamias'],
    'kangkong leaves and tender stalks only': ['kangkong_leaves_and_tender_stalks'],
    'leftover white rice': ['leftover_white_rice'],
    'long green chili pepper': ['long_green_chili'],
    'malunggay': ['malunggay'],
    'peppercorns cracked': ['cracked_peppercorn'],
    'red onion sliced into wedges': ['red_onion'],
    'red onion chopped into small pieces': ['red_onion'],
    'rice steamed to serve': ['cooked_rice'],
    'salt tot aste': ['salt'],
    'salted egg itlog na maalat peeled and quartered': ['salted_egg'],
    'water warm': ['warm_water'],
    'white rice cooked': ['cooked_white_rice'],
    'whole chicken cut into 8 pieces': ['whole_chicken'],
    'chicken cut into 8 pieces': ['chicken'],
    'chicken use breast part': ['chicken_breast'],
    'unsalted butter melted': ['melted_unsalted_butter'],
    'garlic rice': ['garlic_fried_rice'],
    'rice uncooked': ['rice'], 'rice steamed': ['cooked_rice'],
    'rice cooked': ['cooked_rice'], 'rice cooked cooled': ['cooled_cooked_rice'],
    'chicken use chicken thighs': ['chicken_thigh'],
    'chicken use leg quarters': ['chicken_leg_quarter'],
    'chicken use fillets': ['chicken_fillet'],
    'pork use pork belly': ['pork_belly'], 'pork use kasim': ['pork_shoulder'],
    'pork use pork chops': ['pork_chop'],
    'pork use ground lean pork': ['lean_ground_pork'],
    'pork use pork ribs buto-buto': ['pork_rib'],
    'stalks celery chopped': ['celery'], 'stalk celery diced': ['celery'],
    'squid pusit cleaned and sliced into rings': ['squid'],
    'sayote chayote sliced': ['chayote'],
    'white vinegar sukang puti': ['white_vinegar'],
    'whole milk gatas': ['whole_milk'],
    'thick coconut milk kakang gata': ['thick_coconut_milk'],
    'toasted mung beans cracked': ['cracked_toasted_mung_bean'],
    'roasted peanuts crushed': ['roasted_peanut'],
    'peanuts roasted and finely chopped': ['roasted_peanut'],
    'sausage casing balat ng longganisa': ['sausage_casing'],
}


def clean(text):
    return re.sub(r'\s+', ' ', re.sub(r'[(),\[\]]', ' ', text.lower())).strip(' .,:')


def propose(lookup, trusted_roots=None):
    text = clean(lookup)
    if not text:
        return [], 'Missing ingredient text; inspect the original record.'
    # A usage note containing 'or' is not an ingredient alternative.
    text = re.sub(r'\s+or (?:to taste|as needed)$', '', text)
    if re.search(r'\bor\b|\bo\b', text):
        return [], 'Ingredient alternative or ambiguous disjunction; review in recipe context.'
    if re.search(r'\bpepper\b', text) and not re.search(r'\bblack\b|\bwhite\b|\bchili\b|\bbell\b|\bgreen\b|\bred\b|\bcayenne\b', text):
        return [], 'Pepper variety unspecified; do not assume black pepper.'
    if text in {'beef cube', 'beef cubes', 'pork cubes'}:
        return [], 'Could be meat pieces or seasoning; inspect the original recipe.'
    if re.search(r'\brecipe\b|cooking procedure|reserved broth', text):
        return [], 'Recipe dependency or unclear reference needs source review.'
    if 'thai chili' in text and 'siling labuyo' in text:
        return [], 'Specific chili labels conflict; inspect recipe context.'
    if text in EXACT:
        return EXACT[text], 'Explicit agent-authored identity/state rule; original quantities and instructions retained.'
    if re.fullmatch(r'cornstarch dissolved in [\d ./]+(?:cups?|tablespoons?|teaspoons?) water', text):
        return ['cornstarch', 'water'], 'Both starch and water are explicitly named in the slurry.'
    # Remove recognizable packaging, keeping the complete original line elsewhere.
    size = r'\d+(?:\.\d+)?[- ]?(?:ounces?|oz\.?|grams?|g|ml)'
    text = re.sub(rf'^(?:{size}\s+(?:can|pack|packet)|(?:can|pack|packet)\s+{size})\s+', '', text)
    text = re.sub(r'^(?:can|pack|packet)\s+(?=tomato sauce|coconut milk)', '', text)
    text = re.sub(r'^of\s+', '', text)
    text = re.sub(r'^(?:thumbs?|thumb-sized|thumb-size|thumb size|thumb-sized piece|\d+[- ]inch(?: piece)?)\s+(?=(?:fresh )?ginger)', '', text)
    text = re.sub(r'^(?:stalks?|slices|bundle|whole head)\s+(?=lemongrass|celery|green onion|ginger|garlic|kangkong|pechay)', '', text)
    text = re.sub(r'^head\s+(?=cabbage)', '', text)
    text = re.sub(r'^ml\s+(?=coconut milk)', '', text)
    text = re.sub(r'^\d+(?:\.\d+)?\s+ounces?\s+each\s+', '', text)
    if lookup in ALIASES:
        ids = ALIASES[lookup]
        ids = ['spring_onion' if x == 'scallion' else x for x in ids]
        return ids, 'Existing explicit alias; retains raw text and is not substitution approval.'
    if text == 'fish sauce and ground black pepper':
        return ['fish_sauce', 'black_pepper'], 'Two explicitly named ingredients, both required by this line.'
    if text == 'salt and freshly ground black pepper':
        return ['salt', 'black_pepper'], 'Two explicitly named ingredients.'
    # Only shape/handling notes and explicit use notes are ignored for identity.
    # Cooked, fried, frozen, toasted, ground, dried, salted, meat cuts and varieties
    # are NOT removed by this grammar.
    handling = r'(?:peeled|chopped|finely chopped|minced|crushed|smashed|pounded|grated|sliced|thinly sliced|sliced thinly|diced|cubed|quartered|wedged|shredded|julienned|julienne|beaten|well beaten|cleaned|deveined|shelled|seeded|cored|gutted|halved|trimmed|tinadtad|hiniwa|naka-slice|nakahiwa ng manipis|washed|rinsed|pitted|cloves separated|stems trimmed|ends trimmed|tendrils trimmed|head removed|shell removed|tails left on|head and shell removed|shell and head removed|stemmed|leaves separated|with tails left on)'
    usage = r'(?:divided|optional|to taste|to season|for garnish|for topping|to serve|to served|for frying|for deep-frying|for deep frying|for sauteing|for sauteeing|as needed|more as needed|more if needed|to cover meat|enough to cover the meat|for boiling|for cooking|for steaming|for soaking|for sealing lumpia|for brushing|to fry|to deep-fry|for pan frying|for shallow-frying|pang-prito|pampalasa|ayon sa panlasa|more to taste|to taste if necessary|for deep frying)'
    cutting = r'(?:(?:cut|sliced) (?:into|in) (?:\d+(?:/\d+)?[- ]inch(?: long)? |\d+ inch length |small |thin |large )?(?:pieces|cubes|strips|squares|chunks|lengths)|cut into serving (?:pieces|parts))'
    tail = re.compile(rf'^\s*(?:(?:and\s+)?(?:{handling}|{usage}|{cutting})\s*)+$')
    bases = dict(BASE)
    bases.update(trusted_roots or {})
    for base in sorted(bases, key=len, reverse=True):
        variants = [base]
        for translation in TRANSLATIONS.get(base, []):
            variants += [base + ' ' + translation, translation + ' ' + base]
        for variant in variants:
            if text == variant:
                return [bases[base]], 'Explicit ingredient name/translation; automated identity rule, not a substitution decision.'
            if text.startswith(variant + ' '):
                remaining = text[len(variant):].strip()
                for translation in TRANSLATIONS.get(base, []):
                    remaining = re.sub(r'\b'+re.escape(translation)+r'\b', '', remaining)
                remaining = re.sub(r'\s+', ' ', remaining).strip()
                if tail.fullmatch(remaining):
                    return [bases[base]], 'Explicit base plus recognized handling/use note; original state/quantity text retained.'
            if text.endswith(' ' + variant):
                prefix = text[:-len(variant)].strip()
                if re.fullmatch(handling, prefix):
                    return [bases[base]], 'Recognized handling prefix; identity only, not preparation equivalence.'
    from contextual_normalization import parse_flat
    extra = parse_flat(lookup, bases)
    if extra:
        return extra, 'Explicit extended lexicon and fully recognized quantity/handling/translation grammar; original text retained.'
    return [], 'No conservative rule matched; review original line and recipe context.'


def main():
    source = DATA / 'ingredient_groups.batch05.review.csv'
    target = DATA / 'ingredient_groups.batch05.proposals.csv'
    if target.exists():
        raise SystemExit('Proposal file already exists; preserve it and any review edits.')
    with source.open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames + ['proposal_basis']
        rows = list(reader)
    if any(row['decision'] or row['approved_ingredients'] for row in rows):
        raise ValueError('Review work exists in source; do not replace or relabel it.')
    count = 0
    covered = 0
    for row in rows:
        ids, basis = propose(row['lookup_text'])
        row['suggested_ingredients'] = ';'.join(ids)
        row['proposal_basis'] = basis
        if ids:
            count += 1
            covered += int(row['total_occurrences'])
    with target.open('x', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f'Batch groups: {len(rows)}; groups with proposals: {count}; unresolved: {len(rows)-count}')
    print(f'Occurrences represented by proposals: {covered}; not additional approved coverage.')
    print('Approval decisions remain blank. Master review and approved mappings unchanged.')
    print(f'Saved: {target}')


if __name__ == '__main__':
    main()
