import csv
import json
from pathlib import Path


MODEL_DIR = Path(__file__).resolve().parent
DATA_DIR = MODEL_DIR / "data" / "processed"

PILOT_NAMES = [
    "Basic Tortang Talong Recipe",
    "Ginisang Repolyo with Chicken",
    "Ginisang Repolyo with Giniling Recipe",
    "Halabos na Hipon Recipe",
]


def load_json(filename):
    return json.loads(
        (DATA_DIR / filename).read_text(encoding="utf-8")
    )


def main():
    output_path = DATA_DIR / "ingredient_review.pilot.csv"

    if output_path.exists():
        raise SystemExit(
            "Pilot review file already exists. "
            "Keep it to preserve your edits."
        )

    recipes = load_json("recipes.cleaned.json")
    mappings = load_json("ingredient_mapping.proposed.json")
    approved = load_json("ingredient_mapping.approved.json")

    proposed_by_line = {
        item["ingredient_line"]: item
        for item in mappings
    }

    selected = []

    for name in PILOT_NAMES:
        matches = [
            recipe for recipe in recipes
            if recipe["name"] == name
        ]

        if len(matches) != 1:
            raise ValueError(
                f"Expected one record for {name!r}; "
                f"found {len(matches)}."
            )

        selected.append(matches[0])

    # Collect ingredient lines that still need approval.
    pending = {}

    for recipe in selected:
        for original_line in recipe["full_ingredients"]:
            line = original_line.casefold()

            if line in approved:
                continue

            if line not in pending:
                proposal = proposed_by_line.get(line, {})

                pending[line] = {
                    "suggested": proposal.get(
                        "canonical_ingredients", []
                    ),
                    "recipes": set(),
                }

            pending[line]["recipes"].add(recipe["name"])

    fields = [
        "ingredient_line",
        "suggested_ingredients",
        "approved_ingredients",
        "decision",
        "notes",
        "recipe_names",
    ]

    with output_path.open(
        "x", encoding="utf-8-sig", newline=""
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()

        for line, item in sorted(pending.items()):
            writer.writerow({
                "ingredient_line": line,
                "suggested_ingredients": ";".join(
                    item["suggested"]
                ),
                "approved_ingredients": "",
                "decision": "",
                "notes": "",
                "recipe_names": " | ".join(
                    sorted(item["recipes"])
                ),
            })

    print(f"Pilot recipes selected: {len(selected)}")
    print(f"Distinct ingredient lines to review: {len(pending)}")
    print("\nRecipes:")

    for recipe in selected:
        print(f"  - {recipe['name']}")

    print(f"\nSaved to: {output_path}")


if __name__ == "__main__":
    main()