import json
from pathlib import Path


MODEL_DIR = Path(__file__).resolve().parent
DATA_DIR = MODEL_DIR / "data" / "processed"


def main():
    recipes = json.loads(
        (DATA_DIR / "recipes.cleaned.json").read_text(
            encoding="utf-8"
        )
    )

    approved = json.loads(
        (DATA_DIR / "ingredient_mapping.approved.json").read_text(
            encoding="utf-8"
        )
    )

    output = []
    total_lines = 0
    approved_lines = 0
    fully_mapped_recipes = 0

    for recipe in recipes:
        annotations = []
        canonical_ingredients = set()

        for line in recipe["full_ingredients"]:
            total_lines += 1
            mapping = approved.get(line.casefold())

            if mapping:
                approved_lines += 1
                canonical = mapping["canonical_ingredients"]
                canonical_ingredients.update(canonical)

                annotations.append({
                    "original_line": line,
                    "canonical_ingredients": canonical,
                    "status": "approved",
                    "mapping_method": mapping.get("review_type", "owner_recorded_review"),
                    "mapping_reviewer": mapping.get("reviewed_by", ""),
                })
            else:
                annotations.append({
                    "original_line": line,
                    "canonical_ingredients": [],
                    "status": "pending",
                })

        unresolved_count = sum(
            item["status"] == "pending"
            for item in annotations
        )

        fully_mapped = (
            bool(annotations) and unresolved_count == 0
        )

        if fully_mapped:
            fully_mapped_recipes += 1

        # Preserve the original recipe fields.
        prepared = dict(recipe)

        prepared["ingredient_annotations"] = annotations
        prepared["approved_ingredient_ids"] = sorted(
            canonical_ingredients
        )
        prepared["unresolved_ingredient_count"] = unresolved_count
        prepared["ingredient_mapping_complete"] = fully_mapped

        # Ingredient identities alone do not make training data ready.
        prepared["ready_for_training"] = False

        output.append(prepared)

    output_path = DATA_DIR / "recipes.annotated.json"

    output_path.write_text(
        json.dumps(
            output, ensure_ascii=False, indent=2
        ) + "\n",
        encoding="utf-8",
    )

    coverage = (
        approved_lines / total_lines * 100
        if total_lines else 0
    )

    print(f"Recipes processed: {len(output)}")
    print(f"Ingredient lines: {total_lines}")
    print(f"Lines with approved mappings: {approved_lines}")
    print(f"Approved mapping coverage: {coverage:.1f}%")
    print(f"Fully mapped recipes: {fully_mapped_recipes}")
    print(
        "Recipes still needing ingredient review: "
        f"{len(output) - fully_mapped_recipes}"
    )
    print(f"\nSaved to: {output_path}")


if __name__ == "__main__":
    main()
