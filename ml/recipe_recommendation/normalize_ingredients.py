import json
import re
from collections import Counter
from pathlib import Path


MODEL_DIR = Path(__file__).resolve().parent
DATA_DIR = MODEL_DIR / "data" / "processed"

# Handles quantities such as 3, 1/4, and 1 1/2.
NUMBER = r"(?:\d+/\d+|\d+(?:\.\d+)?)"
SINGLE_AMOUNT = rf"{NUMBER}(?:\s+\d+/\d+)?"
AMOUNT = (
    rf"{SINGLE_AMOUNT}"
    rf"(?:\s*(?:to|[-–])\s*{SINGLE_AMOUNT})?"
)

UNIT = (
    r"(?:table\s*spoons?|tea\s*spoons?|cups?|"
    r"tbsp\.?|tsp\.?|cloves?|heads?|pieces?|"
    r"ounces?|oz\.?|pounds?|lbs?\.?|"
    r"kilograms?|kilogrammes?|kilos?|kg\.?|"
    r"grams?|g\.?|quarts?|"
    r"liters?|litres?|bunches|bunch)"
)

QUANTITY_PREFIX = re.compile(
    rf"^{AMOUNT}\s+(?:{UNIT}\s+)?",
    flags=re.IGNORECASE,
)


# These are explicit equivalent names, not substring matches.
ALIASES = {
    "salt": ["salt"],
    "pepper": ["black_pepper"],
    "black pepper": ["black_pepper"],
    "ground black pepper": ["black_pepper"],
    "salt and pepper": ["salt", "black_pepper"],
    "salt and ground black pepper": ["salt", "black_pepper"],
    "soy sauce": ["soy_sauce"],
    "fish sauce": ["fish_sauce"],
    "vinegar": ["vinegar"],
    "water": ["water"],
    "oil": ["cooking_oil"],
    "cooking oil": ["cooking_oil"],
    "vegetable oil": ["vegetable_oil"],
    "canola oil": ["canola_oil"],
    "onion": ["onion"],
    "onion, peeled and chopped": ["onion"],
    "garlic": ["garlic"],
    "garlic, peeled and minced": ["garlic"],
}
ALIASES.update({
    # Garlic preparation variants
    "garlic crushed": ["garlic"],
    "garlic (minced)": ["garlic"],
    "garlic (chopped)": ["garlic"],

    # Preserve the specific onion variety.
    "medium yellow onion sliced": ["yellow_onion"],
    "onion, peeled and sliced thinly": ["onion"],

    # Sauces and other ingredients
    "sugar": ["sugar"],
    "brown sugar": ["brown_sugar"],
    "coconut milk": ["coconut_milk"],
    "fish sauce (patis)": ["fish_sauce"],
    "fish sauce patis": ["fish_sauce"],
    "tomato sauce": ["tomato_sauce"],
    "oyster sauce": ["oyster_sauce"],

    # Known usage notes
    "salt (to season)": ["salt"],
    "oil (for frying)": ["cooking_oil"],

    # Singular and plural forms
    "bay leaf": ["bay_leaf"],
    "bay leaves": ["bay_leaf"],
})
ALIASES.update({
    # Filipino names and usage notes
    "salt asin": ["salt"],
    "water tubig": ["water"],
    "soy sauce toyo": ["soy_sauce"],
    "salt and pepper to taste asin at paminta": [
        "salt",
        "black_pepper",
    ],

    # Peppercorns stay distinct from ground black pepper.
    "peppercorns": ["peppercorn"],
    "whole peppercorn": ["peppercorn"],

    # Bay leaves
    "bay leaves dahon ng laurel": ["bay_leaf"],
    "dried bay leaves": ["dried_bay_leaf"],

    # Eggs
    "egg": ["egg"],
    "eggs": ["egg"],

    # Onion varieties and preparation
    "medium red onion (chopped)": ["red_onion"],
    "medium yellow onion chopped": ["yellow_onion"],
    "medium onion sliced": ["onion"],
    "onion chopped": ["onion"],

    # Garlic powder stays distinct from fresh garlic.
    "garlic powder": ["garlic_powder"],
    "garlic bawang, minced": ["garlic"],

    # Other ingredients
    "calamansi juice": ["calamansi_juice"],
    "calamansi (to serve)": ["calamansi"],
    "butter": ["butter"],
    "water (as needed)": ["water"],
})
# Generate specific preparation variants for known ingredients.
# This does not remove preparation words from arbitrary ingredients.
PREPARATIONS = {
    "garlic": [
        "minced",
        "chopped",
        "crushed",
        "crushed and chopped",
        "peeled, chopped",
        "peeled and minced",
    ],
    "onion": [
        "chopped",
        "sliced",
        "minced",
        "peeled and chopped",
        "peeled and quartered",
        "peeled and sliced thinly",
    ],
    "red onion": [
        "chopped",
        "sliced",
        "minced",
        "peeled, chopped",
        "peeled, quartered",
        "peeled, sliced",
    ],
    "white onion": [
        "chopped",
        "sliced",
        "minced",
    ],
    "yellow onion": [
        "chopped",
        "sliced",
        "minced",
        "wedged",
    ],
    "egg": ["beaten"],
    "eggs": ["beaten"],
}

for ingredient, preparations in PREPARATIONS.items():
    canonical = "egg" if ingredient == "eggs" else (
        ingredient.replace(" ", "_")
    )

    ALIASES.setdefault(ingredient, [canonical])

    for preparation in preparations:
        variants = [
            f"{ingredient} {preparation}",
            f"{ingredient}, {preparation}",
            f"{ingredient} ({preparation})",
            f"{preparation} {ingredient}",
        ]

        for variant in variants:
            ALIASES[variant] = [canonical]


ALIASES.update({
    # Filipino names and seasoning phrases
    "salt asin and pepper (paminta)": ["salt", "black_pepper"],
    "salt asin at paminta": ["salt", "black_pepper"],
    "salt to taste asin": ["salt"],
    "salt (ayon sa panlasa)": ["salt"],
    "salt to taste optional": ["salt"],
    "cooking oil mantika": ["cooking_oil"],
    "garlic minced (bawang)": ["garlic"],
    "freshly ground black pepper paminta": ["black_pepper"],

    # Preserve ingredient forms and varieties
    "black peppercorns": ["black_peppercorn"],
    "all-purpose flour": ["all_purpose_flour"],
    "flour": ["flour"],
    "cornstarch": ["cornstarch"],
    "coconut cream": ["coconut_cream"],
    "coconut milk (gata)": ["coconut_milk"],
    "white vinegar": ["white_vinegar"],
    "white vinegar suka": ["white_vinegar"],
    "granulated white sugar": ["white_sugar"],

    # Oils and sauces
    "sesame oil": ["sesame_oil"],
    "olive oil": ["olive_oil"],
    "oil (for deep-frying)": ["cooking_oil"],
    "vegetable oil (for frying)": ["vegetable_oil"],
    "banana ketchup": ["banana_ketchup"],
    "tomato paste": ["tomato_paste"],
    "liver spread": ["liver_spread"],
    "shrimp paste": ["shrimp_paste"],

    # Meat, broth, and seasoning cubes remain distinct.
    "chicken cut into serving pieces": ["chicken"],
    "ground pork": ["ground_pork"],
    "pork (use ground pork)": ["ground_pork"],
    "beef broth": ["beef_broth"],
    "chicken broth": ["chicken_broth"],
    "knorr pork cube": ["knorr_pork_cube"],
    "knorr chicken cube": ["knorr_chicken_cube"],
    "knorr shrimp cube": ["knorr_shrimp_cube"],

    # Vegetables and other ingredients
    "malunggay leaves": ["malunggay_leaves"],
    "potatoes, peeled and quartered": ["potato"],
    "baking potato cubed": ["baking_potato"],
    "roma tomatoes, chopped": ["roma_tomato"],
    "fresh spinach": ["spinach"],
    "bok choy": ["bok_choy"],
    "ginger (minced)": ["ginger"],
    "thumb-size ginger, peeled and julienned": ["ginger"],
    "thumb-size ginger, peeled and minced": ["ginger"],
    "chopped scallions": ["scallion"],
    "green peas": ["green_pea"],
    "raisins": ["raisin"],
    "pineapple juice": ["pineapple_juice"],
    "star anise": ["star_anise"],
})
ALIASES.update({
    # Vegetables and herbs
    "okra": ["okra"],
    "chinese eggplant sliced": ["chinese_eggplant"],
    "onion diced": ["onion"],
    "red onion (quartered)": ["red_onion"],
    "yellow onion diced": ["yellow_onion"],
    "onion sibuyas, finely chopped": ["onion"],
    "onion sibuyas, chopped": ["onion"],
    "onion sibuyas, peeled and chopped": ["onion"],
    "baby bok choy": ["baby_bok_choy"],
    "green finger chili (siling pangsigang)": ["siling_pangsigang"],
    "potatoes patatas, peeled and quartered": ["potato"],
    "fresh spinach, stems trimmed": ["spinach"],
    "tomato, chopped": ["tomato"],
    "carrot (julienned)": ["carrot"],
    "carrot cubed": ["carrot"],
    "plum tomato diced": ["plum_tomato"],
    "chopped parsley": ["parsley"],
    "chopped cabbage": ["cabbage"],
    "potatoes (cubed)": ["potato"],
    "potatoes, peeled and cubed": ["potato"],
    "tomato wedged": ["tomato"],
    "tomatoes (quartered)": ["tomato"],
    "spring onions": ["spring_onion"],

    # Garlic and ginger preparation variants
    "garlic bawang, peeled and minced": ["garlic"],
    "garlic crushed and minced": ["garlic"],
    "garlic (tinadtad)": ["garlic"],
    "garlic, peeled and crushed": ["garlic"],
    "ginger (grated)": ["ginger"],
    "ginger (chopped)": ["ginger"],
    "ginger (julienned)": ["ginger"],
    "fried garlic bits": ["fried_garlic"],

    # Sauces, seasonings, and oils
    "mayonnaise": ["mayonnaise"],
    "peanut butter": ["peanut_butter"],
    "lechon sauce": ["lechon_sauce"],
    "curry powder": ["curry_powder"],
    "liquid seasoning": ["liquid_seasoning"],
    "paprika": ["paprika"],
    "white sugar": ["white_sugar"],
    "worcestershire sauce": ["worcestershire_sauce"],
    "patis (fish sauce)": ["fish_sauce"],
    "rock salt": ["rock_salt"],
    "onion powder": ["onion_powder"],
    "vinegar suka": ["vinegar"],
    "extra virgin olive oil": ["extra_virgin_olive_oil"],
    "brown sugar asukal na pula": ["brown_sugar"],
    "bay leaf dahon ng laurel": ["bay_leaf"],

    # Preserve these forms as separate identities.
    "pineapple chunks": ["pineapple_chunks"],
    "coconut cream (kakang gata)": ["coconut_cream"],
    "chicken stock": ["chicken_stock"],
    "chicken bouillon cube": ["chicken_bouillon_cube"],
    "ground beef": ["ground_beef"],
    "chicken, cut into serving parts": ["chicken"],
    "calamansi": ["calamansi"],
    "lemon (to serve)": ["lemon"],
    "lemon juice": ["lemon_juice"],

    # Explicit usage notes
    "cooking oil (for deep frying)": ["cooking_oil"],
    "cooking oil (for frying)": ["cooking_oil"],
    "oil (for sauteing)": ["cooking_oil"],
    "oil (as needed)": ["cooking_oil"],
    "canola oil for frying": ["canola_oil"],
    "ground black pepper (ayon sa panlasa)": ["black_pepper"],
    "black pepper (ayon sa panlasa)": ["black_pepper"],
    "ground black pepper paminta": ["black_pepper"],
    "black pepper paminta": ["black_pepper"],
    "ground black pepper (or to taste)": ["black_pepper"],
    "salt (or to taste)": ["salt"],
    "water (or as needed)": ["water"],
})
def prepare_for_lookup(line):
    text = line.casefold().strip()
    text = QUANTITY_PREFIX.sub("", text)

    # Remove a leading size description after the quantity.
    # Meaningful varieties such as "yellow" or "roma" stay.
    text = re.sub(
        r"^(?:small|medium|large)(?:-sized)?\s+",
        "",
        text,
    )

    text = re.sub(
        r"\s*(?:\(to taste\)|to taste)\s*$",
        "",
        text,
    )

    return re.sub(r"\s+", " ", text).strip()

def main():
    input_path = DATA_DIR / "ingredient_vocabulary.json"

    vocabulary = json.loads(
        input_path.read_text(encoding="utf-8")
    )

    proposed = []
    mapped_lines = 0
    mapped_occurrences = 0
    total_occurrences = 0
    ingredient_counts = Counter()

    for item in vocabulary:
        line = item["ingredient_line"]
        occurrences = item["occurrences"]
        lookup = prepare_for_lookup(line)
        canonical = ALIASES.get(lookup, [])

        total_occurrences += occurrences

        if canonical:
            mapped_lines += 1
            mapped_occurrences += occurrences

            for ingredient in canonical:
                ingredient_counts[ingredient] += occurrences

        proposed.append({
            "ingredient_line": line,
            "occurrences": occurrences,
            "lookup_text": lookup,
            "canonical_ingredients": canonical,
            "review_status": (
                "proposed" if canonical else "unresolved"
            ),
        })

    output_path = DATA_DIR / "ingredient_mapping.proposed.json"

    output_path.write_text(
        json.dumps(
            proposed,
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )

    print(f"Distinct lines: {len(vocabulary)}")
    print(f"Lines with proposed mappings: {mapped_lines}")
    print(f"Unresolved lines: {len(vocabulary) - mapped_lines}")
    print(
        "Ingredient-line occurrences covered: "
        f"{mapped_occurrences}/{total_occurrences}"
    )

    print("\nProposed ingredient counts:")
    for ingredient, count in ingredient_counts.most_common():
        print(f"{count:>5}  {ingredient}")

    print("\nMost common unresolved lines:")
    unresolved = [
        item for item in proposed
        if item["review_status"] == "unresolved"
    ]

    for item in unresolved[:100]:
        print(
            f"{item['occurrences']:>4}  "
            f"{item['ingredient_line']}"
        )

    print(f"\nSaved to: {output_path}")


if __name__ == "__main__":
    main()