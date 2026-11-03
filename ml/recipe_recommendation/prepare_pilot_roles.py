import json
from datetime import datetime, timezone
from pathlib import Path


MODEL_DIR = Path(__file__).resolve().parent
DATA_DIR = MODEL_DIR / "data" / "processed"


PILOT_ROLES = {
    "Basic Tortang Talong Recipe": {
        "major": [
            "chinese_eggplant",
            "egg",
        ],
        "supporting": [
            "salt",
            "black_pepper",
            "cooking_oil",
        ],
    },
    "Ginisang Repolyo with Chicken": {
        "major": [
            "cabbage",
            "chicken_breast",
        ],
        "supporting": [
            "onion",
            "garlic",
            "red_bell_pepper",
            "green_bell_pepper",
            "oyster_sauce",
            "knorr_chicken_cube",
            "water",
            "cooking_oil",
            "salt",
            "black_pepper",
        ],
    },
    "Ginisang Repolyo with Giniling Recipe": {
    "major": [
        "cabbage",
        "ground_pork",
    ],
    "supporting": [
        "red_bell_pepper",
        "green_bell_pepper",
        "tomato",
        "yellow_onion",
        "garlic",
        "chicken_broth",
        "fish_sauce",
        "black_pepper",
        "cooking_oil",
    ],
},
    "Halabos na Hipon Recipe": {
        "major": [
            "shrimp",
            "lemon_lime_soda",
        ],
        "supporting": [
            "sea_salt",
        ],
    },
}


def main():
    input_path = DATA_DIR / "recipes.annotated.json"
    output_path = DATA_DIR / "recipes.pilot.roles.json"

    recipes = json.loads(
        input_path.read_text(encoding="utf-8")
    )

    prepared = []
    reviewed_at = datetime.now(timezone.utc).isoformat()

    for name, roles in PILOT_ROLES.items():
        matches = [
            recipe for recipe in recipes
            if recipe["name"] == name
        ]

        if len(matches) != 1:
            raise ValueError(
                f"Expected one recipe named {name!r}; "
                f"found {len(matches)}."
            )

        recipe = matches[0]

        if not recipe["ingredient_mapping_complete"]:
            raise ValueError(
                f"Ingredient mappings are incomplete: {name}"
            )

        major = set(roles["major"])
        supporting = set(roles["supporting"])
        actual = set(recipe["approved_ingredient_ids"])

        if major & supporting:
            raise ValueError(
                f"Ingredient roles overlap: {name}"
            )

        assigned = major | supporting

        if assigned != actual:
            raise ValueError(
                f"Ingredient mismatch for {name}.\n"
                f"Not assigned a role: {sorted(actual - assigned)}\n"
                f"Assigned but absent: {sorted(assigned - actual)}"
            )

        record = dict(recipe)
        record["major"] = roles["major"]
        record["supporting"] = roles["supporting"]
        record["optional"] = []

        record["ingredient_role_review"] = {
            "status": "approved",
            "reviewed_by": "Kyle",
            "reviewed_at": reviewed_at,
            "basis": (
                "Timpla pilot ingredient roles approved "
                "by the project owner."
            ),
        }

        record["source_completeness_review_status"] = "pending"
        record["ready_for_training"] = False

        prepared.append(record)

    # Save only after all four recipes pass validation.
    output_path.write_text(
        json.dumps(
            prepared, ensure_ascii=False, indent=2
        ) + "\n",
        encoding="utf-8",
    )

    print(f"Pilot recipes prepared: {len(prepared)}")

    for recipe in prepared:
        print(f"\n{recipe['name']}")
        print("  Essential: " + ", ".join(recipe["major"]))
        print("  Supporting: " + ", ".join(recipe["supporting"]))

    print("\nIngredient role review: approved")
    print("Source completeness review: pending")
    print("Ranking examples and labels: not prepared for this pilot")
    print(f"\nSaved to: {output_path}")


if __name__ == "__main__":
    main()