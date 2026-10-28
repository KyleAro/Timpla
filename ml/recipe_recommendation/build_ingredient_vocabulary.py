import json
from collections import Counter
from pathlib import Path


MODEL_DIR = Path(__file__).resolve().parent
DATA_DIR = MODEL_DIR / "data" / "processed"


def main():
    input_path = DATA_DIR / "recipes.cleaned.json"

    recipes = json.loads(
        input_path.read_text(encoding="utf-8")
    )

    counts = Counter()

    for recipe in recipes:
        for ingredient in recipe["full_ingredients"]:
            counts[ingredient.casefold()] += 1

    vocabulary = [
        {
            "ingredient_line": line,
            "occurrences": count,
            "canonical_ingredients": [],
            "review_status": "pending",
        }
        for line, count in sorted(
            counts.items(),
            key=lambda item: (-item[1], item[0]),
        )
    ]

    output_path = DATA_DIR / "ingredient_vocabulary.json"

    output_path.write_text(
        json.dumps(
            vocabulary,
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )

    print(f"Recipes read: {len(recipes)}")
    print(f"Distinct ingredient lines: {len(vocabulary)}")
    print("\nMost common ingredient lines:")

    for item in vocabulary[:30]:
        print(
            f"{item['occurrences']:>4}  "
            f"{item['ingredient_line']}"
        )

    print(f"\nSaved to: {output_path}")


if __name__ == "__main__":
    main()
    