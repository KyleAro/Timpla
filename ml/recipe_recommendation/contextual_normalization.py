"""Additional explicit lexical/handling rules; unknown text is never an identity.

These rules do not infer ingredient quantities, substitutions, or recipe roles.
All original descriptions remain available for those separate decisions.
"""
import re
from functools import lru_cache


LEXICON = '''
active dry yeast|active_dry_yeast
baking soda|baking_soda
baby corn|baby_corn
young corn|young_corn
adobo flakes|adobo_flakes
bagnet|bagnet
annatto water|annatto_water
achuete oil|annatto_oil
atsuete powder|annatto_powder
achuete seeds|annatto_seed
anatto seeds|annatto_seed
bean sprouts|bean_sprout
black olives|black_olive
bonito flakes|bonito_flake
brandy|brandy
button mushrooms|button_mushroom
button mushroom|button_mushroom
cassava flour|cassava_flour
cassava starch|cassava_starch
cherry tomatoes|cherry_tomato
cherry tomato|cherry_tomato
chicken feet|chicken_feet
chicken legs|chicken_leg
chicken leg quarters|chicken_leg_quarter
chicken leg quarter|chicken_leg_quarter
chicken bouillon|chicken_bouillon
beef bouillon|beef_bouillon
beef bouillon cubes|beef_bouillon_cube
beef bouillon cube|beef_bouillon_cube
beef powder|beef_powder
beef shanks|beef_shank
beef short rib|beef_short_rib
bone-in beef shanks|bone_in_beef_shank
bone-in beef shank|bone_in_beef_shank
boneless chicken breasts|boneless_chicken_breast
boneless chicken breast|boneless_chicken_breast
boneless bangus belly|boneless_bangus_belly
boneless bangus|boneless_bangus
corn kernels|corn_kernel
corn on the cob|corn_on_the_cob
croutons|crouton
cuapao buns|cuapao_bun
dashi|dashi
day-old rice|day_old_cooked_rice
chili sauce|chili_sauce
chinese soy sauce|chinese_soy_sauce
chinese sausage|chinese_sausage
chorizo de bilbao|chorizo_de_bilbao
cinnamon bark|cinnamon_bark
clam|clam
clams|clam
mussels|mussel
squid balls|squid_ball
fish balls|fish_ball
meat tenderizer|meat_tenderizer
ground allspice|ground_allspice
nonstick cooking spray|nonstick_cooking_spray
cooking oil spray|cooking_oil_spray
sour cream|sour_cream
japanese white miso paste|japanese_white_miso_paste
white miso paste|white_miso_paste
green leaf lettuce|green_leaf_lettuce
banana blossoms|banana_blossom
banana leaves|banana_leaf
banana chili|banana_chili
beef hotdog|beef_hotdog
chili leaves|chili_leaves
long green chili|long_green_chili
long green chilies|long_green_chili
green finger chili|green_finger_chili
green finger chilies|green_finger_chili
finger chili|finger_chili
finger chilies|finger_chili
red chillies|red_chili
red chilies|red_chili
jalapeno peppers|jalapeno_pepper
jalapeno pepper|jalapeno_pepper
jalapeo peppers|jalapeno_pepper
jalapeo pepper|jalapeno_pepper
dried guajillo chiles|dried_guajillo_chili
sport pepper|sport_pepper
dried dilis|dried_anchovy
dried squid|dried_squid
dried shrimp|dried_shrimp
dried banana blossoms|dried_banana_blossom
young tamarind|young_tamarind
sweet tamarind pods|sweet_tamarind_pod
goat meat|goat_meat
duck|duck
chicken leg|chicken_leg
pork lungs|pork_lung
pig lungs|pork_lung
pigs lungs|pork_lung
pig heart|pork_heart
pig's heart|pork_heart
pigs heart|pork_heart
pork heart|pork_heart
pork skin|pork_skin
pig skin|pork_skin
pork face|pork_face
pig face|pork_face
pork ear|pork_ear
pork ears|pork_ear
pig ears|pork_ear
pork intestines|pork_intestine
pig intestines|pork_intestine
pork blood|pork_blood
pig blood|pork_blood
beef kidney|beef_kidney
pork kidney|pork_kidney
beef liver|beef_liver
salmon head|salmon_head
tuna steak|tuna_steak
milkfish belly|milkfish_belly
bangus belly|bangus_belly
whole tilapia fish|whole_tilapia
whole tilapia|whole_tilapia
whole bangus|whole_bangus
whole milkfish|whole_milkfish
red snapper|red_snapper
galunggong|galunggong
tinapang bangus|smoked_bangus
smoked milkfish|smoked_milkfish
smoked galunggong|smoked_galunggong
lemon zest|lemon_zest
orange zest|orange_zest
orange juice|orange_juice
dry sherry wine|dry_sherry_wine
sherry wine|sherry_wine
all purpose cream|all_purpose_cream
heavy cream|heavy_cream
whipping cream|whipping_cream
evaporated milk|evaporated_milk
condensed milk|condensed_milk
sweetened condensed milk|sweetened_condensed_milk
fresh milk|fresh_milk
rice water|rice_water
hot water|hot_water
cold water|cold_water
warm water|warm_water
ice water|ice_water
cooked rice|cooked_rice
cooked white rice|cooked_white_rice
white rice|white_rice
garlic fried rice|garlic_fried_rice
fried rice|fried_rice
fried brown rice|fried_brown_rice
leftover cooked rice|leftover_cooked_rice
leftover white rice|leftover_white_rice
hard-boiled egg|hard_boiled_egg
hard-boiled eggs|hard_boiled_egg
hard boiled eggs|hard_boiled_egg
salted egg|salted_egg
salted eggs|salted_egg
quail eggs|quail_egg
quail egg|quail_egg
egg whites|egg_white
egg white|egg_white
egg yolks|egg_yolk
egg yolk|egg_yolk
chicken egg|egg
chicken eggs|egg
silken tofu|silken_tofu
soft tofu|soft_tofu
extra firm tofu|extra_firm_tofu
firm tofu|firm_tofu
instant yeast|instant_yeast
unflavored gelatin|unflavored_gelatin
gelatin powder|gelatin_powder
rice noodles|rice_noodle
flat rice noodles|flat_rice_noodle
egg noodles|egg_noodle
misua|misua
sotanghon|sotanghon
pancit canton noodles|pancit_canton_noodle
pancit bihon|pancit_bihon
lomi noodles|lomi_noodle
miki noodles|miki_noodle
spaghetti|spaghetti
elbow macaroni|elbow_macaroni
penne pasta|penne_pasta
fettuccine|fettuccine
linguine|linguine
angel hair pasta|angel_hair_pasta
lasagna noodles|lasagna_noodle
lasagne sheets|lasagne_sheet
breadcrumbs|bread_crumbs
japanese breadcrumbs|panko_bread_crumbs
cream cheese|cream_cheese
mozzarella cheese|mozzarella_cheese
parmesan cheese|parmesan_cheese
cheddar cheese|cheddar_cheese
kesong puti|kesong_puti
white cheese|white_cheese
nori|nori
bagoong balayan|bagoong_balayan
bagoong isda|bagoong_isda
bagoong alamang|bagoong_alamang
black beans|black_bean
fermented black beans|fermented_black_bean
chickpeas|chickpea
garbanzo beans|garbanzo_bean
garbanzos|garbanzo_bean
green peas|green_pea
frozen green peas|frozen_green_pea
frozen sweet peas|frozen_sweet_pea
snow peas|snow_pea
snow pea|snow_pea
sugar snap peas|sugar_snap_pea
kaffir lime leaves|kaffir_lime_leaf
bay leaves|bay_leaf
dried bay leaves|dried_bay_leaf
fresh basil|fresh_basil
basil leaves|basil_leaf
cilantro leaves|cilantro_leaf
spinach leaves|spinach_leaf
malunggay leaves|malunggay_leaf
taro leaves|taro_leaf
mustard leaves|mustard_leaf
kangkong leaves|kangkong_leaves
rosemary|rosemary
thyme|thyme
oregano|oregano
dried oregano|dried_oregano
dried thyme|dried_thyme
dried rosemary|dried_rosemary
ground cumin|ground_cumin
ground cinnamon|ground_cinnamon
cumin seeds|cumin_seed
sesame seeds|sesame_seed
annatto seeds|annatto_seed
annatto powder|annatto_powder
black peppercorn|black_peppercorn
black peppercorns|black_peppercorn
cracked black peppercorns|cracked_black_peppercorn
crushed red pepper|crushed_red_pepper
red pepper flakes|red_pepper_flake
chili flakes|chili_flake
chili powder|chili_powder
cayenne powder|cayenne_powder
spanish paprika|spanish_paprika
smoked paprika|smoked_paprika
green papaya|green_papaya
unripe papaya|unripe_papaya
ripe papaya|ripe_papaya
ripe mango|ripe_mango
green mango|green_mango
unripe mango|unripe_mango
young coconut meat|young_coconut_meat
fresh coconut meat|fresh_coconut_meat
grated coconut|grated_coconut
desiccated coconut|desiccated_coconut
macapuno|macapuno
ube halaya|ube_halaya
ube extract|ube_extract
vanilla extract|vanilla_extract
vanilla essence|vanilla_essence
pandan extract|pandan_extract
pandan leaves|pandan_leaf
chocolate chips|chocolate_chip
cocoa powder|cocoa_powder
unsweetened cocoa powder|unsweetened_cocoa_powder
dark chocolate|dark_chocolate
milk chocolate|milk_chocolate
white chocolate|white_chocolate
raisins|raisin
pineapple chunks|pineapple_chunk
pineapple tidbits|pineapple_tidbit
crushed pineapple|crushed_pineapple
pineapple slices|pineapple_slice
pineapple juice|pineapple_juice
fruit cocktail|fruit_cocktail
maraschino cherries|maraschino_cherry
all-purpose flour|all_purpose_flour
all purpose flour|all_purpose_flour
rice flour|rice_flour
glutinous rice flour|glutinous_rice_flour
bread flour|bread_flour
cake flour|cake_flour
tapioca starch|tapioca_starch
tapioca pearls|tapioca_pearl
sago|sago
black tapioca pearls|black_tapioca_pearl
rolled oats|rolled_oats
quick cooking oats|quick_cooking_oats
oatmeal|oatmeal
powdered sugar|powdered_sugar
confectioners sugar|confectioners_sugar
granulated sugar|granulated_sugar
raw sugar|raw_sugar
molasses|molasses
maple syrup|maple_syrup
corn syrup|corn_syrup
light corn syrup|light_corn_syrup
dark corn syrup|dark_corn_syrup
lemon soda|lemon_soda
lemon-lime soda|lemon_lime_soda
lemon lime soda|lemon_lime_soda
clear soda|clear_soda
cola|cola
beer|beer
dark beer|dark_beer
red wine|red_wine
white wine|white_wine
rum|rum
coconut milk powder|coconut_milk_powder
knorr sinigang sa sampaloc mix|knorr_sinigang_sa_sampaloc_mix
knorr sinigang sa sampaloc mix original|knorr_sinigang_sa_sampaloc_mix_original
knorr ginataang gulay mix|knorr_ginataang_gulay_mix
knorr ginataang gulay recipe mix|knorr_ginataang_gulay_recipe_mix
knorr sinigang na may miso recipe mix|knorr_sinigang_na_may_miso_recipe_mix
sinigang sa sampaloc mix|sinigang_sa_sampaloc_mix
maggi magic sarap|maggi_magic_sarap
'''
EXTRA = dict(line.split('|') for line in LEXICON.strip().splitlines())
EXTRA.update({name: canonical for canonical, variants in {
    'radish': 'radish|radishes|labanos', 'daikon_radish': 'daikon radish|daikon',
    'chayote': 'chayote|sayote', 'jicama': 'jicama|singkamas',
    'taro': 'taro|gabi', 'taro_leaf': 'taro leaves',
    'bottle_gourd': 'bottle gourd|upo', 'sponge_gourd': 'sponge gourd|patola',
    'squash': 'squash|kalabasa|calabaza squash', 'kabocha_squash': 'kabocha squash',
    'bitter_gourd': 'bitter gourd|ampalaya', 'long_bean': 'long beans',
    'mushroom': 'mushroom|mushrooms', 'oyster_mushroom': 'oyster mushroom|oyster mushrooms',
    'shiitake_mushroom': 'shiitake mushroom|shiitake mushrooms',
    'dried_shiitake_mushroom': 'dried shiitake mushrooms|dried shiitake mushroom',
    'king_oyster_mushroom': 'king oyster mushrooms',
    'green_bean': 'green beans|baguio beans', 'bamboo_shoot': 'bamboo shoots|labong',
    'winged_bean': 'winged beans|sigarilyas|sigarilya',
    'pigeon_pea': 'pigeon peas|kadyos', 'batwan': 'batwan',
    'alugbati': 'alugbati', 'saluyot': 'saluyot', 'himbabao': 'himbabao',
    'chayote_top': 'chayote tops|sayote tops',
    'chicken': 'chicken|manok', 'pork': 'pork|baboy', 'beef': 'beef',
    'ground_chicken': 'ground chicken', 'ground_beef': 'ground beef',
    'pork_tenderloin': 'pork tenderloin', 'pork_shoulder': 'pork shoulder|pork kasim',
    'pork_ham': 'pork ham|pork pigue', 'pork_hock': 'pork hock|pork hocks|pork pata',
    'pork_belly': 'pork belly|pork liempo', 'pork_rib': 'pork ribs|pork rib',
    'pork_chop': 'pork chops|pork chop', 'pork_butt': 'pork butt',
    'beef_sirloin': 'beef sirloin', 'beef_brisket': 'beef brisket',
    'beef_chuck': 'beef chuck', 'beef_round': 'beef round',
    'beef_top_sirloin': 'beef top sirloin', 'beef_top_round': 'beef top round',
    'beef_short_rib': 'beef short ribs', 'beef_shank': 'beef shank',
    'oxtail': 'oxtail|ox tail|oxtails', 'beef_tripe': 'beef tripe|ox tripe',
    'tripe': 'tripe', 'carabeef': 'carabeef',
    'chicken_neck': 'chicken necks|chicken neck', 'chicken_gizzard': 'chicken gizzard|chicken gizzards',
    'chicken_wing': 'chicken wing|chicken wings', 'chicken_thigh': 'chicken thigh|chicken thighs',
    'chicken_breast': 'chicken breast|chicken breasts',
    'pork_liver': 'pork liver|pig liver', 'beef_tongue': 'beef tongue|ox tongue',
    'fish': 'fish', 'mackerel': 'mackerel', 'pompano': 'pompano',
    'grouper': 'grouper|lapu-lapu', 'sardine': 'sardine|sardines',
    'tilapia': 'tilapia', 'tuna': 'tuna', 'salmon': 'salmon',
    'milkfish': 'milkfish', 'bangus': 'bangus', 'shrimp': 'shrimp|shrimps',
    'prawn': 'prawn|prawns', 'crab': 'crab|crabs', 'crabmeat': 'crabmeat|crab meat',
    'mussel': 'mussel|mussels|tahong', 'oyster': 'oyster|oysters',
    'green_mussel': 'green mussels', 'blue_crab': 'blue crabs',
    'mud_crab': 'mud crabs', 'scallop': 'scallops', 'clams': 'clams',
    'squid': 'squid|pusit', 'cuttlefish': 'cuttlefish',
    'tulingan': 'tulingan', 'tambakol': 'tambakol', 'tanigue': 'tanigue',
    'dulong': 'dulong', 'tawilis': 'tawilis', 'kuhol': 'kuhol',
    'dried_fish': 'dried fish', 'tuyo': 'tuyo', 'tinapa': 'tinapa',
    'tocino': 'tocino', 'longganisa': 'longganisa|longanisa', 'ham': 'ham|hamon',
    'bacon': 'bacon', 'sausage': 'sausage|sausages', 'spam': 'spam',
    'meatloaf': 'meatloaf', 'corned_beef': 'corned beef', 'meatball': 'meatballs',
    'kimchi': 'kimchi', 'guacamole': 'guacamole', 'sriracha': 'sriracha',
    'pesto': 'pesto', 'wasabi': 'wasabi', 'sake': 'sake',
    'mirin': 'mirin', 'capers': 'capers', 'caper': 'caper',
    'shortening': 'shortening', 'buttermilk': 'buttermilk',
    'bread': 'bread', 'pandesal': 'pandesal', 'panko': 'panko',
    'tortilla': 'tortilla|tortillas', 'flour_tortilla': 'flour tortillas',
    'breadstick': 'breadsticks', 'cracker': 'crackers', 'crostini': 'crostini',
    'apple': 'apple|apples', 'orange': 'orange|oranges', 'lemon': 'lemon|lemons',
    'lime': 'lime|limes', 'banana': 'banana|bananas', 'saba_banana': 'saba banana|saba bananas',
    'plantain': 'plantain|plantains', 'mango': 'mango|mangoes',
    'guava': 'guava|guavas|bayabas', 'santol': 'santol',
    'jackfruit': 'jackfruit|langka', 'pineapple': 'pineapple',
    'avocado': 'avocado|avocados', 'strawberry': 'strawberry|strawberries',
    'grape': 'grape|grapes', 'watermelon': 'watermelon',
    'prune': 'prunes', 'cranberry': 'cranberries',
    'applesauce': 'applesauce', 'peanut': 'peanut|peanuts',
    'almond': 'almond|almonds', 'cashew': 'cashews', 'walnut': 'walnuts',
    'coconut': 'coconut|buko', 'potato': 'potato|potatoes',
    'sweet_potato': 'sweet potato|sweet potatoes',
    'cucumber': 'cucumber|cucumbers|pipino', 'zucchini': 'zucchini',
    'asparagus': 'asparagus', 'broccoli': 'broccoli', 'cauliflower': 'cauliflower',
    'lettuce': 'lettuce|letsugas', 'celery': 'celery', 'leek': 'leek|leeks',
    'chive': 'chives', 'shallot': 'shallot|shallots',
    'coriander': 'coriander', 'coriander_seed': 'coriander seeds',
    'nutmeg': 'nutmeg', 'allspice': 'allspice', 'saffron': 'saffron',
    'turmeric': 'turmeric', 'turmeric_powder': 'turmeric powder',
    'monosodium_glutamate': 'monosodium glutamate|msg|betsin|vetsin',
    'marjoram': 'marjoram', 'tarragon': 'tarragon', 'dill': 'dill',
    'cilantro': 'cilantro', 'parsley': 'parsley', 'kinchay': 'kinchay',
    'cumin': 'cumin', 'bay_leaf': 'bayleaf|bay leaf',
    'glutinous_rice': 'glutinous rice|sticky rice|malagkit',
    'long_grain_rice': 'long-grain rice|long grain rice',
    'jasmine_rice': 'jasmine rice', 'japanese_rice': 'japanese rice',
    'brown_rice': 'brown rice', 'spicy_vinegar': 'spicy vinegar',
}.items() for name in variants.split('|')})

# Only explicit translations are removed. Conflicting biological labels stay pending.
TRANSLATIONS = {
    'garlic': ['bawang'], 'onion': ['sibuyas'], 'red onion': ['pulang sibuyas'],
    'white onion': ['puting sibuyas'], 'ginger': ['luya'], 'salt': ['asin'],
    'water': ['tubig'], 'cold water': ['malamig na tubig'],
    'sugar': ['asukal'], 'brown sugar': ['asukal na pula', 'asukal na kayumanggi'],
    'black pepper': ['dinurog na paminta', 'paminta'],
    'ground black pepper': ['dinurog na paminta', 'paminta'],
    'fish sauce': ['patis'], 'soy sauce': ['toyo'], 'vinegar': ['suka'],
    'cooking oil': ['mantika'], 'canola oil': ['mantika'], 'vegetable oil': ['mantika'],
    'butter': ['mantikilya'], 'egg': ['itlog'], 'eggs': ['itlog'],
    'carrot': ['karot'], 'carrots': ['karot'], 'tomato': ['kamatis'],
    'tomatoes': ['kamatis'], 'potato': ['patatas', 'patata'], 'potatoes': ['patatas', 'patata'],
    'radish': ['labanos'], 'daikon radish': ['labanos'], 'chayote': ['sayote'],
    'sayote': ['chayote'], 'ampalaya': ['bitter gourd', 'bitter melon'],
    'bitter gourd': ['ampalaya'], 'eggplant': ['talong'], 'eggplants': ['talong'],
    'talong': ['eggplant'], 'squash': ['kalabasa'], 'kalabasa': ['squash'],
    'calabaza squash': ['kalabasa'], 'kabocha squash': ['kalabasa'],
    'sweet potato': ['kamote'], 'sweet potatoes': ['kamote'], 'taro': ['gabi'],
    'jicama': ['singkamas'], 'kangkong': ['water spinach'],
    'malunggay': ['moringa'], 'moringa leaves': ['malunggay'],
    'bok choy': ['pechay'], 'pechay': ['bok choy'],
    'sitaw': ['string beans', 'long beans', 'snake beans'],
    'string beans': ['sitaw'], 'long beans': ['sitaw'], 'snake beans': ['sitaw'],
    'green beans': ['baguio beans', 'abitsuelas'], 'baguio beans': ['abitsuelas'],
    'bean sprouts': ['togue'], 'green peas': ['gisantes', 'gisante'],
    'lemongrass': ['tanglad'], 'cilantro': ['wansoy'],
    'spring onions': ['dahon ng sibuyas'], 'green onions': ['dahon ng sibuyas'],
    'scallions': ['dahon ng sibuyas'], 'annatto seeds': ['atsuete', 'achuete'],
    'annatto powder': ['atsuete'], 'coconut milk': ['gata'],
    'coconut cream': ['kakang gata'], 'glutinous rice': ['malagkit'],
    'salted egg': ['itlog na maalat'], 'salted eggs': ['itlog na maalat'],
    'milkfish': ['bangus'], 'bangus': ['milkfish'], 'squid': ['pusit'],
    'shrimp': ['hipon'], 'pork blood': ['dugo ng baboy'],
    'pork lungs': ['baga ng baboy'], 'pork belly': ['liempo'],
    'pork shoulder': ['kasim'], 'pork hock': ['pata'],
    'beef shank': ['bulalo'], 'chili leaves': ['dahon ng sili'],
    'bay leaves': ['dahon ng laurel'], 'dried bay leaves': ['dahon ng laurel'],
    'crushed pork rinds': ['chicharon'], 'black beans': ['tausi'],
    'fermented black beans': ['tausi'], 'chickpeas': ['garbanzos'],
    'cornstarch': ['corn starch'], 'coconut': ['buko'],
}

NUMBER = r'(?:\d+(?:\.\d+)?(?:\s*/\s*\d+)?|\d+\s+\d+/\d+)'
UNIT = r'(?:fl\s*oz|ounces?|oz\.?|pounds?|lbs?\.?|kilograms?|kilos?|kg|grams?|gms?|g|ml|milliliters?|cups?|tablespoons?|teaspoons?|tbsp\.?|tsp\.?|liters?|litres?|quarts?|pints?|inches?|inch|pieces?)'
PACKAGE = r'(?:cans?|packs?|packages?|packets?|pouches?|bottles?|boxes?|blocks?|bundles?|bunch(?:es)?|stalks?|bulbs?|cloves?|heads?|slabs?|knobs?|thumbs?|thumb-size|thumb-sized|thumb size|sized|slices?|sprigs?)'


def tidy(text):
    text = text.casefold()
    # Normalize both Unicode typography and reversible UTF-8/CP1252 artifacts.
    if any(marker in text for marker in ('\u00e2\u20ac', '\u00c2')):
        try:
            text = text.encode('cp1252').decode('utf-8')
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
    for before, after in {'\u2019': "'", '\u2018': "'", '\u2013': '-', '\u2014': '-',
                          '\u00bd': '1/2', '\u00bc': '1/4', '\u00be': '3/4',
                          'jalape\u00f1o': 'jalapeno'}.items():
        text = text.replace(before, after)
    text = re.sub(r'^(?:filipino|tagalog):\s*', '', text)
    text = re.sub(r'[(),\[\]:;]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip(' .,:;-')
    text = re.sub(r'\s+-\s+', ' ', text)
    text = text.replace('thinly-sliced', 'thinly sliced').replace('well-beaten', 'well beaten')
    # Numbered footnote references are metadata; their source remains available
    # and completeness/role review remains pending. No note contents are guessed.
    text = re.sub(r'\b(?:see\s+)?notes?\s*\d*\b', '', text)
    text = re.sub(r'\s+(?:recipe below|recipe follows|click here)$', '', text)
    text = re.sub(r'\s+(?:provides|adds|creates)\b.*$', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    # Spelling corrections are finite and do not infer missing ingredients.
    for old, new in {'buttter': 'butter', 'coves garlic': 'cloves garlic',
                     'tablspoons': 'tablespoons', 'opional': 'optional',
                     'sliced into cut into': 'cut into',
                     'hot dogs': 'hotdogs', 'tablepespoons': 'tablespoons',
                     'staks': 'stalks', 'slced': 'sliced', 'lareg': 'large',
                     'mayonnise': 'mayonnaise', 'mayonnnaise': 'mayonnaise',
                     'chined eggplant': 'chinese eggplant',
                     'luke warm': 'lukewarm', 'pepperorn': 'peppercorn',
                     'dilited': 'diluted', 'anatto powder': 'annatto powder',
                     'siling pansigang': 'siling pangsigang',
                     'siding pansigang': 'siling pangsigang',
                     'lechon kawaii': 'lechon kawali',
                     'cut unto': 'cut into', 'cut into cut into': 'cut into',
                     'chooped': 'chopped', 'sliceddiagonally': 'sliced diagonally',
                     'eggpplant': 'eggplant', 'cloved garlic': 'cloves garlic',
                     'cornstach': 'cornstarch', 'curly parsely': 'curly parsley',
                     'frehs': 'fresh', 'shitake': 'shiitake', 'lighty beaten': 'lightly beaten',
                     'extra-virgin': 'extra virgin', 'extra-firm': 'extra firm',
                     'dungeneous': 'dungeness', 'table spoon': 'tablespoon',
                     'tablepoons': 'tablespoons', 'tesapoon': 'teaspoon',
                     'tespoon': 'teaspoon', 'tspn': 'teaspoon', 'strings beans': 'string beans',
                     'bokchoy': 'bok choy', 'boo choy': 'bok choy', 'giner': 'ginger',
                     'medim': 'medium', 'meduim': 'medium', 'medum': 'medium',
                     'kiilogram': 'kilogram', 'kiilo': 'kilo', 'choped': 'chopped',
                     'silced': 'sliced', 'garlic.': 'garlic', 'ginger.': 'ginger',
                     'julliened': 'julienned', 'juilienne': 'julienne',
                     'garlicchopped': 'chopped', 'naka-chop': 'chopped',
                     'naka-shred': 'shredded', 'naka-slice': 'sliced',
                     'freshly-grated': 'freshly grated', 'to mato': 'tomato',
                     'tinapa fakes': 'tinapa flakes', 'caups': 'cups',
                     'tablepoos': 'tablespoons', 'tablespoos': 'tablespoons',
                     'calabasa': 'kalabasa'}.items():
        text = text.replace(old, new)
    return text


def strip_amount(text):
    previous = None
    while previous != text:
        previous = text
        text = re.sub(r'^(?:optional\s+|about\s+|approximately\s+|around\s+|~|of\s+|a pinch of\s+|pinch\s+|a few\s+|few\s+|heaping\s+|generous\s+|each\s+|pc\.\s+|\+\s+|additional ingredient\s+|a (?:bunch|handful|dash|hint|pack|small amount) of\s+|a (?:little|pinch)\s+)', '', text)
        text = re.sub(rf'^(?:\?|/\d+)\s+(?:{UNIT})\s+', '', text)
        text = re.sub(rf'^(?:and\s+)?{NUMBER}(?:\s*(?:to|-)\s*{NUMBER})?\s*(?:{UNIT}\s+)?', '', text)
        text = re.sub(rf'^[- ]?(?:inch|inches)(?:[- ]thick|[- ]long)?\s+', '', text)
        text = re.sub(rf'^(?:{UNIT}|{PACKAGE}|dozen|coils?|cobs?|ears?|drops?|dash|drop|sheets?|strips?|handful|slivers?|tasang|kutsara|kutsarita|baso|pcs\.?|tbsps\.?|sachet|spears?|sticks?|tubs?)\s+', '', text)
        text = re.sub(r'^(?:small|medium|large|big|jumbo)\s+(?=onions?|carrots?|tomatoes?|potatoes?|garlic|cabbage|ginger|eggs?\b)', '', text)
        text = text.lstrip(' -')
    return text


SELECTIONS = {
    'pork use kasim': 'pork shoulder', 'pork use pigue': 'pork ham',
    'pork use pork cubes kasim': 'pork shoulder', 'pork pork cubes kasim': 'pork shoulder',
    'pork menudo cut': 'pork menudo cut',
    'beef use shank with bone marrow': 'beef shank with bone marrow',
    'beef use bone-in beef shank bulalo': 'bone-in beef shank',
    'beef use beef cubes': 'beef meat cubes',
    'chicken use ground chicken': 'ground chicken',
    'chicken use different parts': 'mixed chicken parts',
    'chicken use quarter cut chicken thigh and leg': 'chicken leg quarter',
    'beef use sirloin cut': 'beef sirloin', 'beef use short ribs': 'beef short ribs',
    'pork use pork knuckle front part': 'pork hock',
    'salmon use belly': 'salmon belly', 'lapu-lapu use fillet': 'grouper fillet',
}
EXTRA.update({'pork menudo cut': 'pork_menudo_cut',
              'beef shank with bone marrow': 'beef_shank_with_bone_marrow',
              'beef meat cubes': 'beef_meat_cube', 'mixed chicken parts': 'mixed_chicken_parts',
              'pork meat cubes': 'pork_meat_cube', 'salmon belly': 'salmon_belly',
              'grouper fillet': 'grouper_fillet'})
EXTRA.update(dict(line.split('|') for line in '''
enoki mushrooms|enoki_mushroom
dried thyme leaves|dried_thyme_leaf
dried green mung beans|dried_green_mung_bean
dry mung beans|dry_mung_bean
dry sherry|dry_sherry
ground cloves|ground_cloves
ground ginger|ground_ginger
ground oregano|ground_oregano
ground peanut|ground_peanut
ground peanuts|ground_peanut
garlic salt|garlic_salt
green curry paste|green_curry_paste
kaffir lime leaf|kaffir_lime_leaf
kasubha|kasubha
kikiam|kikiam
knorr savorrich chicken|knorr_savorrich_chicken
lady's choice mayonnaise|ladys_choice_mayonnaise
leftover lechon|leftover_lechon
lechon kawali|lechon_kawali
lemon wedges|lemon_wedge
lime wedges|lime_wedge
light brown sugar|light_brown_sugar
lima beans|lima_bean
local white vinegar|local_white_vinegar
maggi magic chicken cubes|maggi_magic_chicken_cube
manila clams|manila_clam
nestle all-purpose cream|nestle_all_purpose_cream
tamarind soup mix|tamarind_soup_mix
pampanga longganisa|pampanga_longganisa
peas|pea
pepper corns|peppercorn
pork belly strips|pork_belly_strips
pork belly with ribs|pork_belly_with_ribs
pork sinigang cut|pork_sinigang_cut
pork cracklings|pork_crackling
pork jowl|pork_jowl
pork rinds|pork_rind
queso de bola|queso_de_bola
red native tomatoes|red_native_tomato
red radish|red_radish
ripe red tomatoes|ripe_red_tomato
spring onion|spring_onion
spring roll wrappers|spring_roll_wrapper
squid rings|squid_ring
baby leeks|baby_leek
sweet corn|sweet_corn
sweet gherkins|sweet_gherkin
sweet onion|sweet_onion
sweet relish|sweet_relish
sweet rice|sweet_rice
tamarind base powder|tamarind_base_powder
tamarind leaves|tamarind_leaf
instant kare-kare mix|instant_kare_kare_mix
pickles|pickle
ready-to-cook sisig|ready_to_cook_sisig
pimiento|pimiento
taco seasoning mix|taco_seasoning_mix
kidney beans|kidney_bean
white beans|white_bean
brown pinto beans|brown_pinto_bean
white corn|white_corn
whole kernel corn|whole_kernel_corn
whole kernel corns|whole_kernel_corn
canned diced tomatoes|canned_diced_tomato
ubod|ubod
whole catfish|whole_catfish
whole native chicken|whole_native_chicken
tahure|tahure
salay-salay fish|salay_salay_fish
chinese sausages|chinese_sausage
wood ear mushrooms|wood_ear_mushroom
dried wood ear mushrooms|dried_wood_ear_mushroom
knorr sinigang na isda mix|knorr_sinigang_na_isda_mix
knorr sinigang na may gabi recipe mix|knorr_sinigang_na_may_gabi_recipe_mix
pork back fat|pork_back_fat
solid white albacore tuna in water|solid_white_albacore_tuna_in_water
canned tuna flakes in oil|canned_tuna_flakes_in_oil
tuna flakes in oil|tuna_flakes_in_oil
whole kernel corn|whole_kernel_corn
sardines in tomato sauce|sardines_in_tomato_sauce
processed cheese|processed_cheese
quickmelt cheese|quickmelt_cheese
sweet tomato sauce|sweet_tomato_sauce
frozen chicken nuggets|frozen_chicken_nugget
spaghetti noodles|spaghetti_noodle
canned pineapple chunks|canned_pineapple_chunk
vienna sausage|vienna_sausage
square spice ham|square_spice_ham
yellow curry powder|yellow_curry_powder
mahi mahi fillets|mahi_mahi_fillet
tom yum paste|tom_yum_paste
canned creamed corn|canned_creamed_corn
straw mushrooms|straw_mushroom
hainanese chicken rice flavoring mix|hainanese_chicken_rice_flavoring_mix
5 spice powder|five_spice_powder
five spice powder|five_spice_powder
'''.strip().splitlines()))
# Additional literal food names reviewed from the remaining corpus. Unknown
# species/types stay explicitly unspecified rather than borrowing a detector ID.
for _name in '''carne asada|chicharon bulaklak|chicken drumsticks|chicken tinola|
coconut aminos|cooking spray|coriander root|corn meal|crab shells|cremini mushrooms|
danggit|dashi granules|dijon mustard|dill leaves|fennel seeds|fish fingers|fish flakes|
foie gras|french mustard|goatskin|green peppercorns|gyoza wrappers|ham bone|ham slices|
hamburger bun|igado|iodized salt|kielbasa sausages|lamb tapa|lemongrass leaves|
lemongrass stalks|macaroni|maggi savor|mahi-mahi fillet|mango jam|mango nectar|
mango-tamarind jelly|mantou buns|marble potatoes|maskobado|miki lucban|nanami togarashi|
onion rings|panko breadcrumbs|pasta noodles|pasta shells|pink peppercorns|plain yogurt|
pork bones|pork inasal|pork lard|pork spareribs|pork steaks|pork strips|powdered milk|
powdered tamarind|red peppercorns|saffron flower|saffron threads|sea snails|
sea vegetables|serrano peppers|sherry|spanish olives|sprite|star margarine|
sugar peas|sweet paprika|sweet peas|taco seasoning|tamarind base|tamarind concentrate|
thick yogurt|tortilla chips|udon noodles|vegan mayonnaise|vermicelli noodles|
white peppercorns|wonton wrappers|yellow mustard|young coconuts|chicken thigh fillets|
chicken wing drumettes and flats|chicken-flavored liquid seasoning|chinese chilli bean sauce|
chinese chorizo|chinese mustasa|chinese pork stew|chinese straw mushrooms|
chipotle chili in adobo sauce|chipotle pepper in adobo sauce|chorizo macau|
chorizo pamplona|chuck roast|cilantro root|cilantro sprigs|cilantro stems|
cinnamon sticks|clam meat|cloves|coconut palm|condensed cream of mushroom soup|
corn cobs|cow cheeks|cow trotters|cow's foot|cows heart|cows small intestine|
crabstick|cream dory fish fillets|cream of asparagus soup powder|cream of mushroom soup|
crispy boneless dilis|crispy fried garlic bits|crispy garlic bits|crispy garlic chips|
crispy mushroom chips|curly parsley|curry leaves|dinner rolls|distilled white vinegar|
dried ancho chiles|dried green mung beans|dried mung beans|dried munggo|
dried rice paper|dried shrimp fry|dry soy chunks|dungeness crab clusters|
egg noodles|egg plant|fettuccine noodles|filipino hotdogs|fish filet|fish fillet|
five-spice powder|flat miki noodles|flat-leaf parsley|fresh breadcrumbs|
fresh ginger root|fresh kamote tops|fresh miki noodles|first-press coconut milk|
thyme|coconut milk powder|pork pancreas|fish skin chicharon
'''.replace('\n', '').strip().split('|'):
    _name = _name.strip()
    EXTRA.setdefault(_name, _name.replace('-', '_').replace("'", '').replace(' ', '_'))
EXTRA.update({'chili': 'chili_unspecified_variety', 'chili pepper': 'chili_pepper_unspecified_variety',
              'red pepper': 'red_pepper_unspecified_type', 'green chilies': 'green_chili_unspecified_variety',
              'heart': 'heart_unspecified_animal', 'kidney': 'kidney_unspecified_animal',
              'intestines': 'intestines_unspecified_animal', 'liver': 'liver_unspecified_animal',
              'kakang gata': 'kakang_gata', 'kalamansi juice': 'calamansi_juice',
              'kamatis': 'tomato', 'luya': 'ginger', 'sibuyas': 'onion', 'suka': 'vinegar',
              'pulot': 'honey', 'saba': 'saba_banana', 'cayenne': 'cayenne_unspecified_form',
              'catsup': 'ketchup', 'canned gata': 'canned_coconut_milk', 'okras': 'okra',
              'pork giniling': 'ground_pork', 'monggo beans': 'mung_bean',
              'miso yellow': 'yellow_miso', 'sashimi-grade tuna': 'sashimi_grade_tuna',
              'pig\'s blood': 'pork_blood', 'pigs blood': 'pork_blood', 'pigs liver': 'pork_liver',
              'vinegar white': 'white_vinegar', 'mayonnaise mayo': 'mayonnaise',
              'sugar peas': 'sugar_pea', 'chili pepper siling labuyo': 'siling_labuyo',
              'chili pepper siling pangsigang': 'siling_pangsigang',
              'chili pepper labuyo': 'labuyo', 'finger chilis': 'finger_chili',
              'thai chili': 'thai_chili', 'thai chili pepper': 'thai_chili',
              'thai chili peppers': 'thai_chili', 'thai chilies': 'thai_chili',
              'chili pepper flakes': 'chili_pepper_flakes', 'saluyot leaves': 'saluyot_leaf'})
EXTRA.update(dict(line.split('|') for line in '''
aa powder|aa_powder
achuete|achuete_unspecified_form
atsuete|atsuete_unspecified_form
achiote atsuete seeds|annatto_seed
achiote|achiote_unspecified_form
annatto extract|annatto_extract
achuete extract|annatto_extract
acorn squash|acorn_squash
adobo|adobo
adobo flavored mix|adobo_flavored_mix
colorless alamang|colorless_alamang
anisado|anisado
anise wine|anise_wine
chinese rice wine|chinese_rice_wine
ap flour|all_purpose_flour
artichoke hearts|artichoke_heart
asin|salt
asparagus spears|asparagus_spear
atsara|atsara
baby potatoes|baby_potato
bagoong|bagoong_unspecified_type
bagoong monamon|bagoong_monamon
balaw|balaw
bamboo shoot|bamboo_shoot
banana hearts|banana_heart
banana catsup|banana_ketchup
banana senorita variety|senorita_banana
basting sauce|basting_sauce
bataw|bataw
batuan|batuan
bawang|garlic
beef base|beef_base
beef bile|beef_bile
beef bones|beef_bone
beef bones with marrow|beef_bone_with_marrow
beef bones with meat|beef_bone_with_meat
beef book tripe|beef_book_tripe
bible tripe|beef_book_tripe
beef heart|beef_heart
beef intestines|beef_intestine
beef small intestine|beef_small_intestine
beef kalitiran|beef_kalitiran
beef rump steak|beef_rump_steak
beef shoulder bones with tendons|beef_shoulder_bone_with_tendon
beef sukiyaki|beef_sukiyaki
beef tapa|beef_tapa
beef tenderloin|beef_tenderloin
beef tendons|beef_tendon
beef striploin|beef_striploin
beef chucks|beef_chuck
beef neck bones|beef_neck_bone
beef kneecap|beef_kneecap
beef shin shanks|beef_shin_shank
beef-flavored instant ramen|beef_flavored_instant_ramen
bell peppers|bell_pepper
bell pepper strips|bell_pepper_strips
benguet rice|benguet_rice
bicol chilies|bicol_chili
bihon noodles|bihon_noodle
bile|bile_unspecified_animal
bird's eye chilies|birds_eye_chili
birds eye chili|birds_eye_chili
birds eye chilies|birds_eye_chili
bisaya squid|bisaya_squid
bitter melon|bitter_melon
black fungus|black_fungus
blue ginger|blue_ginger
blue oyster mushrooms|blue_oyster_mushroom
bokchoy|bok_choy
bok choy leaves|bok_choy_leaf
boneless bangus bellies|boneless_bangus_belly
boneless chicken thigh fillets|boneless_chicken_thigh_fillet
boneless chicken thigh meat|boneless_chicken_thigh_meat
boneless skinless chicken thigh meat|boneless_skinless_chicken_thigh_meat
bottom round roast|bottom_round_roast
bouillon cubes|bouillon_cube_unspecified_type
bourbon whiskey|bourbon_whiskey
breakfast steak|breakfast_steak
breakfast beef steaks|breakfast_beef_steak
broccoli crown|broccoli_crown
broccoli florets|broccoli_floret
broth|broth_unspecified_type
panutsa|panutsa
corkwood tree flowers|corkwood_tree_flower
bunga ng malunggay|bunga_ng_malunggay
buttercup squash|buttercup_squash
cajun seasoning|cajun_seasoning
cajun seasoning mix|cajun_seasoning_mix
calamansi concentrate|calamansi_concentrate
calamansi leaves|calamansi_leaf
calamansi halves|calamansi_halves
spanish-style sardines|spanish_style_sardine
canned cream of corn|canned_cream_of_corn
canned mango nectar|canned_mango_nectar
canned pineapples|canned_pineapple
canned spicy tuna flakes in oil|canned_spicy_tuna_flakes_in_oil
canned sardines in oil|canned_sardine_in_oil
canned tomato puree|canned_tomato_puree
canned tuna in oil|canned_tuna_in_oil
canned tuna in water|canned_tuna_in_water
canned water chestnuts|canned_water_chestnut
canned tausi|canned_tausi
pork and beans|pork_and_beans
canola|canola_oil
canton noodles|canton_noodle
'''.strip().splitlines()))
# Curated food/product names encountered in the remaining source vocabulary.
# Each is an explicit name, not a fallback slug for an arbitrary source line.
CURATED_NAMES = '''
ahi tuna|alfredo sauce|aligue paste|anchovy sauce|annatto paste|artichoke heart|
avocado oil|baby back rib|banana heart|banana pepper|basmati rice|beef bottom round|
black bean sauce|black vinegar|bone marrow|bouillon cube|broth cube|bullet tuna|
calamansi juice|canned whole kernel corn|canola cooking oil|carabao meat|
century egg|char siu sauce|cheese sauce|chicken intestine|chicken meat|chicken quarter|
chili bean paste|chili paste|chinese black vinegar|chinese cabbage|chinese cooking wine|
chinese napa cabbage|chinese parsley|chinese straw mushroom|chipotle pepper|
chorizo bilbao|chuck steak|chunky corned beef|cilantro lime rice|clam stock|
coconut curry paste|coconut juice|coconut meat|coconut palm vinegar|coconut sap vinegar|
coconut water|cooking wine|corn flour|country style rib|crab fat|cream dory fillet|
cream dory fish fillet|creamy peanut butter|crispy dilis|crispy fried garlic|
crispy fried shallot|crispy mushroom|crispy shallot|crocodile meat|crushed piquin pepper|
crushed tomato|curry paste|dashi stock|datu puti cane vinegar|dressed duck|
dried basil|dried black mushroom|dried chili|dried coriander|dried kamias|
dried mexican oregano|dried parsley|dried red chili pepper|dried wood ear mushroom|
duck egg|edam cheese|eden cheese|enoki mushroom|fatty pork|filipino eggplant|
filipino style hotdog|filipino style tomato sauce|fish bouillon cube|fish paste|
fish steak|freshwater shrimp|frog leg|frog legs|fuji apple|garlic mayonnaise|
garlic skin|garlicky sausage|ghost pepper|ginataang gulay mix|glutinous rice powder|
granulated white sugar|grape tomato|green banana|green chili pepper|green jackfruit|
green langka|green native tomato|green peppercorn|green pickle relish|green tamarind|
guajillo pepper|gyoza wrapper|ham hock|hot chili|hot chili pepper|hot chili sauce|
hot red chili pepper|hungarian sausage|ice cube|iceberg lettuce|ilocos longganisa|
iloko vinegar|imitation crab meat|indian eggplant|indian mango|instant kare mix|
italian style tomato sauce|japanese corn|japanese eggplant|japanese rice vinegar|
jasponica rice|jumbo hotdog|jumbo squid|korean barbecue mix|korean hot pepper paste|
kurma curry powder|labahita fillet|laoag longganisa|lean beef|lean pork|
lean pork meat|lechon belly|lechon liempo|lechon manok|lechon manok sauce|
leftover adobo meat|leftover chicken|leftover ham|leftover roast chicken|
light japanese soy sauce|light mayonnaise|light olive oil|lime soda|
liquid smoke flavoring|littleneck clam|local vinegar|long chili|long chili pepper|
long eggplant|long grain white rice|long red chili|low sodium chicken stock|
low sodium soy sauce|lukewarm water|luncheon meat|magic sarap all-purpose seasoning|
malunggay pasta|mango relish|mapo tofu mix|marble potato|mature coconut|
melting cheese|milkfish steak|miponica rice|monterey jack cheese|mussel broth|
native chicken|native duck|native pechay|native red tomatoes|navel orange|
neutral cooking oil|neutral oil|nutmeg powder|oil spray|orange sweet potato|
ordinary cooking oil|ordinary vinegar|original style tomato sauce|
overripe green mango|peanut sauce|pig brain|pig ear|pig intestine|pig leg|pig meat|
pink peppercorn|pinot grigio white wine|pork adobo sauce|pork chicharon|
pork hamonado sausage|pork spare rib|premium soy sauce|prepared sisig|
pure vinegar|quick melt cheese|quick melting cheese|raw egg yolk|raw shrimp|
red curry paste|red curry powder|red finger chili|red peppercorn|red rice|
red snapper fillet|red thai chili|red thai chili pepper|red tomato|regular hotdog|
reno liver spread|reserved beef broth|reserved marinade|ribeye steak|rice wine vinegar|
rock sugar|romaine lettuce|rotisserie chicken|round eggplant|safflower oil|
salmon steak|sashimi grade tuna|savoy cabbage|seafood stock|seasoned vinegar|
semi sweet chocolate|serrano pepper|short grain rice|short rib|shrimp base powder|
shrimp broth|shrimp head|shrimp powder|sinamak vinegar|sinigang mix powder|
sinigang na sampaloc mix|sinigang na sampalok mix|sinigang powder|sinigang powder mix|
sinigang sa kamias powder mix|sinigang sa sampalok paste|smelt fish|smoked bacon|
smoked bangus|smoked coconut cream|smoked fish|smoked tinapa|snap pea|soda water|
sole fillet|solid white albacore tuna|spaghetti sauce|spanish bomba rice|spanish onion|
spare rib|spicy green pepper|spicy red chili|spicy shrimp paste|
spicy sinigang na sampalok mix|spicy thai chili|spicy tuna|spider crab|
square wonton wrapper|sriracha hot chili sauce|sriracha sauce|stewing beef|
suahe shrimp|sweet bell pepper|sweet ham|sweet kernel corn|sweet pea|sweet soy sauce|
sweet style filipino spaghetti sauce|sweet style spaghetti sauce|
sweetened shredded coconut|swordfish steak|szechuan pepper|tabasco sauce|table salt|
tamarind juice|tamarind paste|tamarind powder|tamarind sinigang mix|
tamarind soup base mix|tanigue steak|tap water|tapioca flour|tartar sauce|
teriyaki sauce|thai basil|thai chili sauce|thai eggplant|thai green curry paste|
thai red chili|thai red chilies|thai red peppers|thai shrimp paste|thai soy sauce|
thick coconut cream|thin coconut milk|tiger prawn|tilapia fillet|tinapang galunggong|
tinapang isda|tomato juice|tomato-based sardines|tonkatsu sauce|top sirloin|truffle oil|
tuna belly|tuna fillet|tuna jaw|tuna meat|uncooked elbow macaroni|
uncooked glutinous rice|vegetable shortening|vietnamese coriander|vigan longganisa|
violet sticky rice|wanton wrapper|wasabi mayonnaise|wheat bread|white bread|
white fish|white fish fillet|white fish steak|white mushroom|white pepper powder|
white peppercorn|white radish|whole golden pompano|whole pig leg|whole pigs leg|
whole pork leg|whole salmon|whole spring chicken|whole wheat pandesal|
whole wheat pita bread|whole wheat spaghetti|wonton wrapper|wood ear mushroom|
yellow miso soybean paste|yellow sweet potato|young coconut|young green jackfruit
'''
for _name in re.sub(r'\s+', ' ', CURATED_NAMES).strip().split('|'):
    _name = _name.strip()
    EXTRA.setdefault(_name, _name.replace('-', '_').replace(' ', '_'))
EXTRA.update(dict(line.split('|') for line in '''
miso|miso
laing|laing
adobong pusit|adobong_pusit
pork adobo|pork_adobo
rice wash|rice_wash
rice washing|rice_washing
rice washing water|rice_washing_water
hotdog|hotdog
hotdogs|hotdog
potato cube|potato_cube
tomato cube|tomato_cube
lechon carajay|lechon_carajay
glutinous rice balls|glutinous_rice_ball
salted krill|salted_krill
mung bean sprout|mung_bean_sprout
flour stick noodles|flour_stick_noodle
long green chili pepper|long_green_chili
chick pea|chickpea
green pea|green_pea
butternut squash|butternut_squash
opo squash|opo_squash
sugpo|tiger_prawn
spicy bagoong alamang|spicy_bagoong_alamang
taba ng talangka|taba_ng_talangka
alamang|alamang
fresh pepper leaves|fresh_pepper_leaves
beef ribs|beef_rib
coke|coke
corned beef brisket|corned_beef_brisket
fennel bulb|fennel_bulb
large sea scallops|large_sea_scallop
shaoxing cooking wine|shaoxing_cooking_wine
banana flower bud|banana_flower_bud
banana blossom|banana_blossom
palabok noodles|palabok_noodle
cornstarch sticks|cornstarch_stick
hot pepper leaves|hot_pepper_leaf
tamarind flower buds|tamarind_flower_bud
monggo|mung_bean
beef neck bone|beef_neck_bone
baking potato|baking_potato
steamed oysters|steamed_oyster
maggi magic sinigang sa sampaloc|maggi_magic_sinigang_sa_sampaloc
knorr beef cube|knorr_beef_cube
knorr beef cubes|knorr_beef_cube
knorr pork cube|knorr_pork_cube
knorr pork cubes|knorr_pork_cube
knorr chicken cube|knorr_chicken_cube
patis sauce|fish_sauce
pats fish sauce|fish_sauce
mayonnise|mayonnaise
'''.strip().splitlines()))
TRANSLATIONS.update({
    'radish': ['labanos'], 'gabi': ['taro root'],
    'tofu': ['tokwa'], 'firm tofu': ['tokwa'],
    'taro leaves': ['dahon ng gabi'], 'pork rinds': ['chicharon'],
    'pork cracklings': ['chicharon'], 'pig face': ['maskara'],
    'goat meat': ['chevon'], 'mud crabs': ['alimango'],
    'tulingan': ['bullet tuna'], 'kasubha': ['safflower'],
    'lima beans': ['patani'], 'snow peas': ['chicharo', 'sitsaro'],
    'dried banana blossoms': ['puso ng saging'],
    'freshly grated coconut': ['niyog'], 'white corn': ['puting mais'],
    'sweet rice': ['malagkit'], 'tamarind': ['sampalok'],
    'wood ear mushrooms': ['tenga ng daga'], 'dried wood ear mushrooms': ['tenga ng daga'],
    'salted egg': ['itlog na maalat'], 'boneless bangus': ['milkfish'],
    'garlic powder': ['pulbos na bawang'], 'oyster sauce': ['sarsa ng talaba'],
    'turmeric': ['luyang dilaw'], 'unsalted butter': ['mantikilya'],
    'light soy sauce': ['toyo'], 'liver spread': ['atay spread'],
    'honey': ['pulot'], 'kangkong': ['water spinach', 'onchoy'],
    'bird\'s eye chili': ['siling labuyo'],
    'tinapa flakes': ['smoked fish', 'smoked fish flakes'],
    'siling pangsigang': ['long green pepper', 'long green chili pepper'],
    'long green chili pepper': ['siling pangsigang'],
    'napa cabbage': ['pechay baguio'], 'napa cabbages': ['pechay baguio'],
    'sugpo': ['tiger prawn'], 'tiger prawn': ['sugpo'],
    'glutinous rice balls': ['bilo-bilo'],
    'banana flower bud': ['puso ng saging'], 'banana blossom': ['puso ng saging'],
    'garlic fried rice': ['sinangag'], 'pancit canton': ['flour stick noodles', 'flour noodles'],
    'palabok noodles': ['cornstarch sticks'],
    'hot pepper leaves': ['dahon ng sili'], 'steamed oysters': ['talaba'],
    'sotanghon': ['cellophane noodles'], 'sotanghon noodles': ['cellophane noodles'],
    'kamote': ['sweet potato'], 'saluyot leaves': ['jute leaves'],
    'amaranth leaves': ['kulitis'], 'bay leaves': ['laurel'],
    'opo squash': ['upo'], 'upo': ['opo squash'],
    'achuete': ['annatto'], 'atsuete': ['annatto'],
    'achuete seeds': ['annatto seeds'], 'atsuete seeds': ['annatto seeds'],
    'anatto seeds': ['atsuete'], 'annatto seeds': ['atsuete', 'achuete', 'atsuete seeds'],
    'achuete oil': ['annatto oil'], 'atsuete oil': ['annatto oil'],
    'achuete extract': ['annatto extract'], 'atsuete powder': ['annatto powder', 'achuete/annatto'],
    'annatto powder': ['atsuete', 'astuete', 'atsuete powder'],
    'ampalaya': ['bitter gourd', 'bitter melon', 'bittermelon'],
    'ampalaya leaves': ['bitter melon leaves', 'bittermelon leaves'],
    'apple cider vinegar': ['suka', 'suka ng mansanas'],
    'bagoong alamang': ['fermented shrimp paste'], 'bagoong isda': ['fermented fish'],
    'bagoong': ['fermented shrimp paste'], 'bagoong monamon': ['fermented fish sauce'],
    'baking potato': ['patatas'], 'baking powder': ['pampaalsa'],
    'bamboo shoots': ['labong'], 'banana blossoms': ['puso ng saging'],
    'banana heart': ['puso ng saging'], 'banana hearts': ['puso ng saging'],
    'banana leaves': ['dahon ng saging'], 'banana ketchup': ['ketsup na saging', 'saging ketsup'],
    'beef brisket': ['baka', 'brisket ng baka'], 'beef broth': ['sabaw ng baka'],
    'beef heart': ['puso', 'puso ng baka'], 'beef intestines': ['bituka ng baka'],
    'beef kidney': ['bato ng baka'], 'beef liver': ['atay', 'atay ng baka'],
    'beef short ribs': ['tadyang ng baka', 'tadyang'], 'beef ribs': ['tadyang'],
    'beef tendons': ['litid'], 'beef tongue': ['dila ng baka'],
    'beef tripe': ['tuwalya', 'tuwalya ng baka'],
    'beef bile': ['apdo ng baka', 'apdo'], 'bile': ['apdo'],
    'beef sirloin': ['karne ng baka'], 'beef rump steak': ['karne ng baka'],
    'beef shanks': ['buto-buto', 'tulan ng baka'], 'bone-in beef shank': ['buto-buto'],
    'bataw': ['hyacinth bean'], 'betsin': ['msg'],
    'bihon noodles': ['thin rice noodles'], 'black fungus': ['tengang daga'],
    'blue ginger': ['galangal'], 'blue crabs': ['alimasag'],
    'bird\'s eye chilies': ['siling labuyo'], 'birds eye chili': ['siling labuyo'],
    'birds eye chilies': ['siling labuyo'],
    'bok choy': ['chinese leafy cabbage', 'pechay'],
    'boneless bangus': ['milkfish'], 'boneless bangus bellies': ['milkfish bellies'],
    'boneless skinless chicken thigh': ['hita ng manok', 'manok na hita'],
    'boneless skinless chicken breast': ['dibdib ng manok'],
    'bottled crab fat paste': ['aligue'], 'bottled crab fat': ['taba ng talangka'],
    'broccoli': ['brokoli'], 'brown sugar': ['asukal', 'asukal na mapula', 'asukal na pula'],
    'corkwood tree flowers': ['katuray'], 'button mushrooms': ['kabute'],
    'cabbage': ['repolyo'], 'calamansi': ['philippine lime'],
    'calamansi juice': ['kalamansi', 'katas ng kalamansi', 'katas ng calamansi'],
    'cane vinegar': ['suka ng tubo'], 'canola oil': ['langis', 'mantika'],
    'heart': ['puso'], 'kidney': ['bato'], 'intestines': ['bituka'],
    'miso': ['soybean paste'], 'milk': ['gatas'], 'sago': ['tapioca'],
    'amaranth leaves': ['kulitis'], 'saluyot leaves': ['jute leaves'],
    'egg whites': ['puti ng itlog'], 'coconut juice': ['buko juice', 'buko jioce'],
    'coconut sap vinegar': ['sukang tuba'], 'chinese sausages': ['lap cheong'],
    'cinnamon stick': ['kanela'], 'clam': ['halaan', 'almejas'],
    'clams': ['halaan', 'almejas'], 'coconut meat': ['laman ng buko'],
    'fresh coconut meat': ['laman ng buko'], 'fresh coconut water': ['buko juice'],
    'condensed milk': ['kondensadang gatas'], 'day-old rice': ['kanin'],
    'steamed rice': ['kanin'], 'cooked white rice': ['kanin'],
    'corn': ['mais'], 'corn cobs': ['mais'], 'corn on the cob': ['mais'],
    'cows heart': ['puso ng baka'], 'cow trotters': ['paa ng baka'],
    'cow\'s foot': ['paa ng baka'], 'crab': ['alimasag'], 'crabs': ['alimasag', 'alimango'],
    'black peppercorns': ['pamintang buo', 'paminta'],
    'cracked black peppercorns': ['dinurog na paminta'], 'black pepper': ['paminta', 'pamintang durog'],
    'dried mung beans': ['monggo'], 'dried munggo': ['mung beans'],
    'dried green mung beans': ['monggo'], 'dried shrimp': ['hibi', 'hibe'],
    'fresh cilantro': ['wansuy'], 'cilantro leaves': ['wansoy'],
    'chinese chorizo': ['chorizo macau'], 'chorizo macau': ['chinese chorizo'],
    'chinese eggplants': ['talong na mahaba'], 'chinese cooking wine': ['shaoxing wine'],
    'egg noodles': ['pancit canton'], 'dried oregano': ['oregano'],
})


HANDLING = r'(?:peeled|pared|chopped|chopped finely|finely chopped|coarsely chopped|roughly chopped|minced|crushed|smashed|pounded|bruised|grated|sliced|thinly sliced|sliced thinly|sliced diagonally|sliced lengthwise|sliced in half|sliced into wedges|diced|finely diced|cubed|quartered|wedged|shredded|julienned|julienne|beaten|well beaten|cleaned|clean|deveined|shelled|seeded|deseeded|cored|gutted|halved|trimmed|washed|rinsed|pitted|drained|rinsed and drained|flaked|scrubbed|brushed|scored|deboned|bones removed|skin removed|skin and bones removed|scales removed|scales and innards removed|cleaned of scales|core removed|stems removed|stems trimmed|stem removed|stemmed|leaves separated|ends trimmed|shell removed|shells removed|head removed|heads removed|heads and shells removed|shells and heads removed|head and shell removed|shell and head removed|tails left on|with tails left on|thawed|cloves separated|split lengthwise|tied|tied into a knot|tied in a knot|crumbled|cut in half|cut into halves|cut into quarters|cut into thirds|cut into wedges|cut into rings|cut into strips|cut into cubes|cut into chunks|cut into serving pieces|cut into serving parts|cut into bite-size pieces|cut into bite-sized pieces|cut into small pieces|cut into small cubes|cut into thin strips|cut into thin slices|cut into strips lengthwise|tinadtad|hiniwa|hiniwa ng manipis|hiniwang manipis|nakahiwa ng manipis|durugin|dinurog|hiniwa pahaba|sariwa)'
USAGE = r'(?:optional|divided|to taste|to season|for seasoning|for garnish|for garnishing|for topping|for toppings|to serve|for serving|to served|for frying|for deep frying|for deep-frying|for shallow-frying|for pan frying|for sauteing|for sauteeing|for cooking|for steaming|for boiling|for boiling pork|for soaking|for brushing|for coating|for dusting|for dredging|for sealing|for sealing lumpia|as needed|more as needed|more if needed|more to taste|enough to cover|to cover|to cover meat|enough to cover the meat|to balance heat|to balance the heat|to fry|to deep-fry|pang-prito|ayon sa panlasa|para sa pagkulo|pampalasa)'
CUT = rf'(?:(?:cut|sliced|chopped) (?:into|in) (?:(?:about\s+)?{NUMBER}(?:\s*(?:to|-)\s*{NUMBER})?\s*[- ]?(?:inch|inches|cm)(?:[- ]thick|[- ]long)?\s+|small\s+|thin\s+|large\s+|big\s+|bite-sized\s+|bite-size\s+)?(?:pieces|cubes|strips|squares|chunks|lengths|sticks|rounds|rings|slices|wedges)|cut {NUMBER} inches long|sliced into {NUMBER}|cut into {NUMBER})'
TAIL = re.compile(rf'^(?:(?:and |then )?(?:{HANDLING}|{USAGE}|{CUT})\s*)+$')


def handling_only(text):
    """Recognize shape-only wording without consuming another food or state.

    All tokens must belong to this finite vocabulary and an action is required.
    Physical part names require explicit removal; e.g. "shrimp heads" cannot be
    collapsed to shrimp. Boiled/fried/raw and food names are deliberately absent.
    """
    if not text.isascii():
        return False
    actions = set('peeled pared chopped minced diced grated sliced cut quartered halved split smashed crushed pounded julienned shredded cleaned washed rinsed drained deveined shelled seeded deseeded cored trimmed pitted gutted deboned scaled scored flaked crumbled beaten bruised tied separated hiniwa nakahiwa hiwain ginayat dinurog binalatan hinati tinadtad gadgarin kudkurin kinadkad gayatin kinalas tadtarin hinugasan tinatad mashed macerated stripped batihin batiin chunked'.split())
    words = actions | set('and then into in on a an the of to for small large medium bite sized size thick thin thickly thinly diagonally diagonal lengthwise crosswise cubes strips pieces chunks squares rounds wedges rings lengths sticks halves half quarters thirds portions segments bias fine finely coarsely roughly lightly slightly separately well very desired sizes round length long inch inches cm mm foot feet about approximately each per down out up at both sides through across removed discarded nilinis nang ng na manipis pahaba haba pulgadang piraso maliliit tig iisang dalawang pulgada kapal malalaking freshly'.split())
    parts = set('skin skins bone bones scale scales stem stems stalk stalks end ends seed seeds head heads shell shells tail tails core cores'.split())
    tokens = re.findall(r"[a-z]+|\d+(?:\.\d+)?", text.casefold())
    lexical = {token for token in tokens if not token[0].isdigit()}
    if not tokens or tokens[-1] in {'and', 'or', 'into', 'in', 'of', 'for', 'to', 'on', 'then', 'with'}:
        return False
    if lexical & parts:
        if not lexical & {'removed', 'discarded', 'trimmed', 'deboned', 'shelled', 'seeded', 'deseeded', 'cored', 'gutted', 'scaled'}:
            return False
    return bool(lexical & actions) and lexical <= words | parts
HANDLING_MORE = r'(?:cloves|sliced into wedges|cut into wedges|debearded|beards removed|peeled and deveined|cleaned and deveined|cut into 8 pieces|cut into 4 pieces|each cut into 8 pieces|each cut into 4 pieces)'
HANDLING = rf'(?:{HANDLING}|{HANDLING_MORE})'
TAIL = re.compile(rf'^(?:(?:and |then )?(?:{HANDLING}|{USAGE}|{CUT})\s*)+$')
HANDLING_EXTRA = r'(?:separated|finely sliced|thinly julienned|sliced on a bias|sliced thinly into rings|cut thinly on a bias|lightly peeled|beards removed|scaled|nilinis|binalatan|nabalatan|strained|squeezed|cut up|cut-up to serving pieces|cut into parts|chopped into serving pieces|trimmed and washed|roughly diced|cubed small|cubed medium|leaves only|ends trimmed|sliced thickly|finely grated|thoroughly cleaned|patted dry|washed and dried|rinsed and dried|cut at the roots|sliced into half-rounds)'
HANDLING = rf'(?:{HANDLING}|{HANDLING_EXTRA})'
USAGE = rf'(?:{USAGE}|to garnish|more to serve|for dipping|to taste more to serve|or more to taste|or more as needed|or to taste|to taste asin)'
TAIL = re.compile(rf'^(?:(?:and |then )?(?:{HANDLING}|{USAGE}|{CUT})\s*)+$')


@lru_cache(maxsize=4)
def name_index(root_items):
    names = dict(EXTRA)
    names.update({tidy(k): v for k, v in root_items})
    # Inflect only known food nouns, preserving explicitly recorded spellings.
    irregular = {'leaf': 'leaves', 'potato': 'potatoes', 'tomato': 'tomatoes',
                 'chili': 'chilies', 'berry': 'berries', 'loaf': 'loaves'}
    nouns = set('pepper bean pea egg tomato potato leaf mushroom shrimp prawn oyster clam crab chili chile steak fillet rib noodle onion carrot cucumber eggplant sausage hotdog banana orange lemon lime apple stick wrapper sprout seed breast thigh leg drumstick slice flake clove squash scallion shallot ball ear foot wing gizzard heart intestine kidney liver cabbage coconut blossom'.split())
    for name, canonical in list(names.items()):
        head = name.split()[-1]
        if head in nouns:
            plural = irregular.get(head, head+'es' if head.endswith(('s', 'ch', 'sh', 'x')) else head+'s')
            names.setdefault(name[:-len(head)]+plural, canonical)
    starts, ends = {}, {}
    for name in sorted(names, key=len, reverse=True):
        variants = {name}
        for translation in TRANSLATIONS.get(name, []):
            variants.update({name+' '+translation, translation+' '+name})
        for variant in sorted(variants, key=len, reverse=True):
            record = (name, variant, names[name])
            starts.setdefault(variant.split()[0], []).append(record)
            ends.setdefault(variant.split()[-1], []).append(record)
    return starts, ends


def parse_flat(text, roots):
    """Recognize a full literal ingredient plus finite handling/translation text."""
    text = tidy(text)
    previous = None
    while previous != text:
        previous = text
        text = strip_amount(text)
        text = re.sub(r'^(?:(?:small to medium|medium to large|small|medium|large|jumbo|big)(?:[- ]size[ds]?)?\s+)+', '', text)
    text = re.sub(r'\s+(?:we|i) (?:used|use|prefer)\b.*$', '', text).strip()
    text = re.sub(r'\s+preferably\b.*$', '', text).strip()
    text = re.sub(r'\s+for (?:soaking|boiling|rinsing|washing|steaming) (?:the )?[a-z -]+$', '', text).strip()
    text = re.sub(r'\s+(?:plus (?:more|extra)(?: if needed)?|more to taste|more if desired|plus more to season|add more to taste)$', '', text).strip()
    text = re.sub(r'\b(cooked|boiled) (?:until tender|according to package directions|according to package instructions)\b', r'\1', text)
    text = re.sub(r'\bor (?:more to taste|more as needed|to taste|as needed)(?:\s|$)', '', text).strip()
    if not text or re.search(r'\bor\b|\bo\b|cooking procedure', text):
        return []
    if re.search(r'\brecipe\b', text) and 'recipe mix' not in text:
        return []
    shape = re.fullmatch(r'(?:(?:finely|coarsely|roughly|freshly) )?(chopped|minced|sliced|diced|grated|crushed|shredded|julienned|flaked|pounded) (.+)', text)
    if shape:
        parsed = parse_flat(shape[2], roots)
        if parsed:
            return parsed
    for old, replacement in sorted(SELECTIONS.items(), key=lambda p:-len(p[0])):
        if old != replacement and (text == old or text.startswith(old+' ')):
            return parse_flat(replacement+text[len(old):], roots)
    text = re.sub(r'^(pork|beef|chicken) use (?=\1\b)', '', text)
    text = re.sub(r'^(pork|beef|chicken) use (tenderloin|shoulder|belly|sirloin|top round|top sirloin|brisket|breast|thigh|legs?|wings?)\b', r'\1 \2', text)
    # Trailing package weights are measurements, not ingredient qualifiers.
    text = re.sub(rf'\s+(?:about\s+)?{NUMBER}[- ]?(?:{UNIT})(?:\s+(?:each|per pack|pack))?$', '', text).strip()
    # Prefer the established canonical identity for an already recognized name.
    starts, ends = name_index(tuple(sorted(roots.items())))
    words = text.split()
    seen = set()
    for name, variant, canonical in starts.get(words[0], []) + ends.get(words[-1], []):
        if (name, variant) in seen:
            continue
        seen.add((name, variant))
        if text == variant:
            return [canonical]
        if text.startswith(variant+' '):
            tail = text[len(variant):].strip()
            for translation in TRANSLATIONS.get(name, []):
                tail = re.sub(r'\b'+re.escape(translation)+r'\b', '', tail)
            tail = re.sub(r'\s+', ' ', tail).strip()
            if not tail or TAIL.fullmatch(tail) or handling_only(tail):
                return [canonical]
        if text.endswith(' '+variant) and re.fullmatch(HANDLING, text[:-len(variant)].strip()):
            return [canonical]
    # Explicit preparation states become distinct IDs, never the unprepared base.
    # This is a state-qualified ingredient identity, not a substitution policy.
    states = ('boneless skinless', 'skinless boneless', 'bone-in', 'boneless',
              'skinless', 'hard-boiled', 'hard boiled', 'boiled', 'cooked', 'fried',
              'grilled', 'roasted', 'toasted', 'smoked', 'dried', 'frozen',
              'salted', 'pickled', 'steamed', 'melted', 'clarified', 'fresh',
              'ripe', 'unripe', 'young', 'whole', 'ground', 'scrambled', 'softened',
              'crispy fried', 'pan-fried', 'deep-fried', 'freshly squeezed', 'baked',
              'canned', 'leftover', 'cooked and shredded', 'boiled and shredded',
              'poached', 'soft-boiled', 'chilled', 'cold', 'raw', 'browned', 'broiled',
              'dehydrated', 'rehydrated', 'unpeeled', 'unsulphured', 'store-bought',
              'low sodium', 'low-sodium', 'unsalted', 'sweetened', 'unsweetened',
              'native', 'spicy', 'thin', 'thick', 'pure', 'homemade', 'first extract',
              'coarsely ground', 'finely ground', 'freshly ground', 'coarsely cracked',
              'freshly cracked', 'cracked', 'deep fried', 'pan fried', 'filtered')
    for state in states:
        remainder = None
        if text.startswith(state+' '):
            remainder = text[len(state):].strip()
        elif text.endswith(' '+state):
            remainder = text[:-len(state)].strip()
        if remainder and remainder != text:
            ids = parse_flat(remainder, roots)
            if ids:
                qualifier = state.replace('-', '_').replace(' ', '_')
                return [qualifier+'_'+value for value in ids]
        match = re.fullmatch(r'(.+?) '+re.escape(state)+r' (.+)', text)
        if match and TAIL.fullmatch(match[2]):
            return parse_flat(state+' '+match[1]+' '+match[2], roots)
    # These physical qualifiers are retained in IDs rather than thrown away as
    # handling notes. The remaining text must still parse completely.
    physical = {'skin on': 'skin_on', 'skin-on': 'skin_on', 'with skin': 'skin_on',
                'skin off': 'skin_off', 'without skin': 'skin_off',
                'bone in': 'bone_in', 'with bones': 'bone_in',
                'with ribs': 'with_ribs', 'without ribs': 'without_ribs',
                'with shell and head': 'head_and_shell_on',
                'with shells and heads': 'head_and_shell_on',
                'head-on': 'head_on', 'head on': 'head_on',
                'with shell': 'shell_on', 'with shells': 'shell_on',
                'leaves and tender stalks only': 'leaves_and_tender_stalks',
                'leaves and tender stems': 'leaves_and_tender_stems',
                'tender stalks and leaves only': 'tender_stalks_and_leaves',
                'white part only': 'white_part', 'white parts only': 'white_parts',
                'white part': 'white_part', 'white parts': 'white_parts',
                'white portions only': 'white_portions', 'white portions': 'white_portions',
                'white fleshy part only': 'white_fleshy_part',
                'white and light green parts': 'white_and_light_green_parts',
                'dark green part only': 'dark_green_part', 'green part only': 'green_part'}
    for phrase, qualifier in sorted(physical.items(), key=lambda x:-len(x[0])):
        remainder, replacements = re.subn(r'(?<!\w)'+re.escape(phrase)+r'(?!\w)', '', text)
        if replacements:
            ids = parse_flat(re.sub(r'\s+', ' ', remainder).strip(), roots)
            if ids:
                return [qualifier+'_'+value for value in ids]
    return []
