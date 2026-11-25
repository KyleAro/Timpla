"""Build traceable ingredient priorities from the active serving catalog; no model fitting."""
import collections
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
DEST = Path(__file__).resolve().parents[1] / 'dist'
SOURCE = ROOT / 'ml/recipe_recommendation/models/quick_v1/catalog.json'

# UI grouping only. These rules do not define ingredient substitutions or
# compatibility. Every exported identity keeps the serving catalog's exact ID.
FRUITS = set('mango banana calamansi lemon lime orange apple pineapple papaya avocado watermelon melon cantaloupe coconut jackfruit langka guava grape strawberry raisin tamarind sampalok santol kamias bilimbi pomelo durian rambutan lychee pear peach apricot plum cherry blueberry raspberry blackberry guyabano soursop breadfruit atis chico kiwi passionfruit dragonfruit'.split())
VEGETABLES = set('garlic onion ginger carrot tomato potato cabbage eggplant okra squash pumpkin kalabasa cucumber bitter_gourd ampalaya string_bean sitaw pechay bok_choy kangkong spinach malunggay chayote sayote radish daikon broccoli cauliflower bell_pepper celery zucchini leek scallion spring_onion shallot mushroom taro gabi sweet_potato yam ube cassava corn mung_bean monggo munggo bean_sprout lettuce water_spinach bottle_gourd upo sponge_gourd patola snow_pea green_pea chickpea green_bean long_bean bamboo_shoot banana_blossom banana_heart banana_leaf chili siling_pangsigang siling_labuyo thai_chili jalapeno lemongrass turmeric basil cilantro parsley mint dill chive green_papaya'.split())
FISH = set('fish tilapia milkfish bangus tuna salmon sardine sardines mackerel grouper lapu_lapu galunggong scad catfish hito pompano snapper anchovy anchovies cod sole halibut trout swordfish mahi_mahi talakitok tulingan hasa_hasa danggit dalag bangus_belly'.split())
SEAFOOD = set('shrimp prawn crab lobster mussel clam oyster scallop squid octopus cuttlefish tahong halaan talaba alimasag alimango pusit hipon scallops mussels clams oysters crabs'.split())
def contains(identity, terms):
    return any(re.search(r'(^|_)' + re.escape(term) + r'(_|$)', identity) for term in terms)

def classify(identity):
    if contains(identity, {'sauce', 'paste', 'broth', 'stock', 'bouillon', 'cube', 'powder', 'flour', 'starch', 'cornstarch', 'oil', 'vinegar', 'sugar', 'salt', 'peppercorn', 'black_pepper', 'white_pepper', 'pepper_unspecified', 'bay_leaf', 'juice', 'ketchup', 'catsup', 'extract', 'syrup', 'jam', 'jelly', 'puree', 'nectar', 'seasoning', 'mix', 'noodle', 'pasta', 'spaghetti', 'macaroni', 'rice', 'rice_grains', 'cooked_rice', 'cooked_white_rice', 'water', 'gelatin', 'yeast', 'baking', 'soda', 'bread', 'breadcrumb', 'cracker', 'wrapper', 'tortilla', 'chocolate', 'cocoa', 'coffee', 'tea', 'honey', 'mayonnaise', 'fish_sauce', 'coconut_milk', 'coconut_cream', 'coconut_water'}):
        return 'Pantry & seasonings', None
    if contains(identity, {'adobo', 'fried_rice', 'sausage', 'ham', 'bacon', 'tocino', 'longganisa', 'hotdog', 'spam', 'corned_beef', 'meatball', 'lechon', 'sisig', 'embutido', 'tapa', 'luncheon_meat'}):
        return 'Prepared foods', None
    if contains(identity, {'chicken', 'manok'}): return 'Chicken', None
    if contains(identity, {'pork', 'baboy'}): return 'Pork', None
    if contains(identity, {'beef', 'oxtail', 'ox', 'baka'}): return 'Beef', None
    if contains(identity, {'shrimp', 'prawn', 'hipon'}): return 'Seafood', 'Shrimp & Prawns'
    if contains(identity, {'crab', 'crabs', 'lobster', 'alimango', 'alimasag'}): return 'Seafood', 'Crabs & Lobsters'
    if contains(identity, {'squid', 'octopus', 'cuttlefish', 'pusit'}): return 'Seafood', 'Squid & Octopus'
    if contains(identity, SEAFOOD): return 'Seafood', 'Shellfish'
    if contains(identity, FISH): return 'Seafood', 'Fish'
    if contains(identity, VEGETABLES): return 'Vegetables', None
    if contains(identity, FRUITS): return 'Fruits', None
    if contains(identity, {'egg', 'eggs', 'quail_egg', 'milk', 'cheese', 'butter', 'cream', 'yogurt', 'yoghurt'}): return 'Eggs & dairy', None
    return 'Other recipe ingredients', None

def leaves(tree):
    if not isinstance(tree, dict): return set()
    if 'ingredient_id' in tree: return {tree['ingredient_id']}
    return set().union(*(leaves(child) for key in ('all_of', 'any_of') for child in tree.get(key, [])))

def main():
    raw = SOURCE.read_bytes()
    recipes = json.loads(raw)
    counts, essential_counts = collections.Counter(), collections.Counter()
    examples = collections.defaultdict(list)
    for recipe in recipes:
        essential_counts.update(leaves(recipe['essential']))
        for identity in set(recipe['all_food']):
            counts[identity] += 1
            if len(examples[identity]) < 3: examples[identity].append({'id': recipe['id'], 'name': recipe['name']})
    rows = []
    for identity, count in counts.most_common():
        category, subgroup = classify(identity)
        rows.append({'id': identity, 'name': identity.replace('_', ' ').capitalize(), 'category': category,
                     **({'subgroup': subgroup} if subgroup else {}), 'recipeCount': count,
                     'essentialRecipeCount': essential_counts[identity], 'examples': examples[identity]})
    visual = [row for row in rows if row['category'] in ('Fruits', 'Vegetables', 'Chicken', 'Pork', 'Beef', 'Seafood') and row['recipeCount'] >= 5]
    result = {'recipeCount': len(recipes), 'ingredientCount': len(rows), 'source': 'ml/recipe_recommendation/models/quick_v1/catalog.json',
              'sourceSha256': hashlib.sha256(raw).hexdigest(), 'note': 'Recipe counts measure catalog presence, not visual detectability or verified human annotations. Category grouping is a proposal; ingredient IDs and counts are unchanged.',
              'suggestedFolderIds': [row['id'] for row in visual], 'ingredients': rows}
    (DEST / 'recipe-needs.js').write_text('export default ' + json.dumps(result, ensure_ascii=False, separators=(',', ':')) + ';\n', encoding='utf-8')
    grouped = collections.defaultdict(list)
    for row in rows: grouped[row['category']].append(row['name'])
    (DEST / 'recipe-ingredients.json').write_text(json.dumps(grouped, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'recipes': len(recipes), 'ingredientIdentities': len(rows), 'suggestedVisualFolders': len(visual), 'groupCounts': dict(collections.Counter(row['category'] for row in rows))}))

if __name__ == '__main__': main()
