"""Conservative preference filtering before ranking; no allergy-safety certification."""
import re

ALLERGENS = {
    'peanuts': r'peanut|groundnut|arachis',
    'shellfish': r'shrimp|prawn|crab|lobster|crayfish|clam|mussel|oyster|scallop|squid|cuttlefish|octopus|bagoong|alamang|hipon|patis|seafood|surimi',
    'eggs': r'(^|_)eggs?(_|$)|mayonnaise|meringue|custard|leche_flan',
    'dairy': r'milk|cream|cheese|butter|yogurt|yoghurt|whey|casein|ghee|margarine|chocolate',
    'soy': r'soy|soya|tofu|tokwa|taho|miso|edamame|tempeh|teriyaki|hoisin|oyster_sauce|margarine',
    'wheat': r'wheat|flour|bread|pasta|spaghetti|macaroni|noodle|pancit|panko|cracker|biscuit|soy_sauce|teriyaki|hoisin|oyster_sauce|lumpia_wrapper|wonton|dumpling_wrapper|seitan',
}
ALIASES = {'peanut': 'peanuts', 'egg': 'eggs', 'milk': 'dairy', 'soya': 'soy'}


def normalize(value):
    return re.sub(r'\s+', '_', value.strip().lower())


def contains_excluded(foods, excluded):
    # Match whole ingredient terms, including forms such as pork_belly and garlic_powder.
    return any(re.search(r'(^|_)' + re.escape(value) + r'(_|$)', food)
               for value in excluded for food in foods)


def eligible(recipe, allergies=(), diet='No preference'):
    # Diet labels require reviewed evidence. Missing labels never imply compliance.
    if diet != 'No preference' and diet not in recipe.get('verified_diets', []):
        return False
    foods = recipe['all_food']
    for value in allergies:
        name = normalize(value)
        name = ALIASES.get(name, name)
        pattern = ALLERGENS.get(name)
        if pattern is None:
            # Custom allergies require an explicit reviewed declaration.
            if name not in recipe.get('verified_free_from', []):
                return False
        elif any(re.search(pattern, food) for food in foods):
            return False
    return True
