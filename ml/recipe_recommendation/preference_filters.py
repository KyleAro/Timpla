"""Conservative ingredient restrictions for recipe discovery (not allergen certification)."""
import re


def normalize(value):
    key = re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")
    return {"baboy": "pork", "itlog": "egg", "talong": "eggplant", "bawang": "garlic",
            "mani": "peanut", "hipon": "shrimp", "gatas": "milk", "toyo": "soy_sauce"}.get(key, key)


def contains_excluded(foods, excluded):
    for food in foods:
        name = normalize(food)
        for value in excluded:
            key = normalize(value)
            if key and (name == key or f"_{key}_" in f"_{name}_"):
                return True
    return False


ALLERGENS = {
    "peanuts": ["peanut", "peanuts", "groundnut", "groundnuts"],
    "shellfish": ["shrimp", "prawn", "crab", "lobster", "clam", "mussel", "oyster", "scallop", "squid", "octopus", "bagoong", "alamang", "hipon", "patis"],
    "eggs": ["egg", "eggs", "mayonnaise", "mayo", "itlog"],
    "dairy": ["milk", "cheese", "butter", "cream", "yogurt", "whey", "casein", "gatas"],
    "soy": ["soy", "soya", "tofu", "tokwa", "taho", "miso", "toyo"],
    "wheat": ["wheat", "flour", "bread", "breadcrumbs", "panko", "pasta", "noodles", "soy_sauce"],
}
ALLERGY_NAMES = {"peanut": "peanuts", "egg": "eggs", "milk": "dairy", "soybeans": "soy"}


def eligible(recipe, allergies=(), diet="No preference"):
    foods = recipe.get("all_food", [])
    verified = {normalize(value) for value in recipe.get("verified_free_from", [])}
    for value in allergies:
        key = normalize(value)
        key = ALLERGY_NAMES.get(key, key)
        if key in ALLERGENS:
            if contains_excluded(foods, ALLERGENS[key]):
                return False
        elif key not in verified:
            return False
    if diet != "No preference" and diet not in recipe.get("verified_diets", []):
        return False
    return True
