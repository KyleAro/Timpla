import csv
from pathlib import Path


MODEL_DIR = Path(__file__).resolve().parent

DATASET_PATH = (
    MODEL_DIR
    / "data"
    / "external"
    / "filipino_recipes_2k"
    / "recipes.csv"
)


def split_items(text):
    return [
        item.strip()
        for item in (text or "").split("|")
        if item.strip()
    ]


def main():
    with DATASET_PATH.open(
        "r", encoding="utf-8-sig", newline=""
    ) as file:
        recipes = list(csv.DictReader(file))

    print(f"Total recipe records: {len(recipes)}")

    for recipe in recipes[:3]:
        print("\n" + "=" * 60)
        print(f"Recipe: {recipe['recipe_name']}")

        print("\nFull ingredient list:")
        for ingredient in split_items(recipe["ingredients"]):
            print(f"  - {ingredient}")

        print("\nDataset ingredient names:")
        for ingredient in split_items(recipe["ingredient_names"]):
            print(f"  - {ingredient}")


if __name__ == "__main__":
    main()