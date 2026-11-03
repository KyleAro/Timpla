import csv
import json
from pathlib import Path


MODEL_DIR = Path(__file__).resolve().parent
DATA_DIR = MODEL_DIR / "data" / "processed"


def main():
    input_path = DATA_DIR / "ingredient_mapping.proposed.json"
    output_path = DATA_DIR / "ingredient_review.batch01.csv"

    # Protect any review work you have already entered.
    if output_path.exists():
        raise SystemExit(
            f"Review file already exists: {output_path}\n"
            "Keep it. Use a new batch filename for another export."
        )

    mappings = json.loads(
        input_path.read_text(encoding="utf-8")
    )

    proposed = sorted(
        [
            item for item in mappings
            if item["review_status"] == "proposed"
        ],
        key=lambda item: (
            -item["occurrences"],
            item["ingredient_line"],
        ),
    )

    unresolved = sorted(
        [
            item for item in mappings
            if item["review_status"] == "unresolved"
        ],
        key=lambda item: (
            -item["occurrences"],
            item["ingredient_line"],
        ),
    )

    batch = proposed[:50] + unresolved[:150]

    fields = [
        "ingredient_line",
        "occurrences",
        "suggested_ingredients",
        "approved_ingredients",
        "decision",
        "notes",
    ]

    with output_path.open(
        "x", encoding="utf-8-sig", newline=""
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()

        for item in batch:
            writer.writerow({
                "ingredient_line": item["ingredient_line"],
                "occurrences": item["occurrences"],
                "suggested_ingredients": ";".join(
                    item["canonical_ingredients"]
                ),
                "approved_ingredients": "",
                "decision": "",
                "notes": "",
            })

    print(f"Proposed mappings to check: {len(proposed[:50])}")
    print(f"Unresolved lines to review: {len(unresolved[:150])}")
    print(f"Total review rows: {len(batch)}")
    print(f"\nSaved to: {output_path}")


if __name__ == "__main__":
    main()