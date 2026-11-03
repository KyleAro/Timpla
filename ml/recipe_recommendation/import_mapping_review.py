import argparse
import csv
from html import parser
from html import parser
import json
import re
from datetime import datetime, timezone
from pathlib import Path


MODEL_DIR = Path(__file__).resolve().parent
DATA_DIR = MODEL_DIR / "data" / "processed"

CANONICAL_ID = re.compile(r"^[a-z][a-z0-9_]*$")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reviewer", required=True)
    parser.add_argument(
    "--review-file",
    type=Path,
    default=DATA_DIR / "ingredient_review.batch01.csv",
    )
    args = parser.parse_args()

    reviewer = args.reviewer.strip()
    if not reviewer:
        raise ValueError("Reviewer name must not be blank.")

    review_path = args.review_file
    vocabulary_path = DATA_DIR / "ingredient_vocabulary.json"
    output_path = DATA_DIR / "ingredient_mapping.approved.json"

    vocabulary = json.loads(
        vocabulary_path.read_text(encoding="utf-8")
    )
    known_lines = {
        item["ingredient_line"] for item in vocabulary
    }

    approved = {}
    if output_path.exists():
        approved = json.loads(
            output_path.read_text(encoding="utf-8")
        )

    with review_path.open(
        encoding="utf-8-sig", newline=""
    ) as file:
        reader = csv.DictReader(file)

        required_columns = {
            "ingredient_line",
            "approved_ingredients",
            "decision",
            "notes",
        }

        missing = required_columns - set(reader.fieldnames or [])
        if missing:
            raise ValueError(
                f"Missing CSV columns: {sorted(missing)}"
            )

        rows = list(reader)

    imported = 0
    unchanged = 0
    deferred = 0
    pending = 0
    seen_lines = set()
    reviewed_at = datetime.now(timezone.utc).isoformat()

    for row_number, row in enumerate(rows, start=2):
        line = row["ingredient_line"]
        decision = row["decision"].strip().lower()
        approved_text = row["approved_ingredients"].strip()

        if line not in known_lines:
            raise ValueError(
                f"Row {row_number}: ingredient line not in vocabulary."
            )

        if line in seen_lines:
            raise ValueError(
                f"Row {row_number}: duplicate ingredient line."
            )
        seen_lines.add(line)

        if decision not in {"", "approve", "defer"}:
            raise ValueError(
                f"Row {row_number}: unknown decision {decision!r}."
            )

        if decision != "approve":
            if approved_text:
                raise ValueError(
                    f"Row {row_number}: approved ingredients entered "
                    "without an approve decision."
                )

            if decision == "defer":
                deferred += 1
            else:
                pending += 1
            continue

        ingredients = [
            value.strip()
            for value in approved_text.split(";")
        ]

        if not all(
            CANONICAL_ID.fullmatch(value)
            for value in ingredients
        ):
            raise ValueError(
                f"Row {row_number}: enter ingredient IDs such as "
                "'salt' or 'salt;black_pepper'."
            )

        if len(set(ingredients)) != len(ingredients):
            raise ValueError(
                f"Row {row_number}: repeated ingredient ID."
            )

        if line in approved:
            existing = approved[line]["canonical_ingredients"]

            if set(existing) != set(ingredients):
                raise ValueError(
                    f"Row {row_number}: conflicts with an existing "
                    "approved mapping. Review the conflict first."
                )

            unchanged += 1
            continue

        approved[line] = {
            "canonical_ingredients": ingredients,
            "reviewed_by": reviewer,
            "reviewed_at": reviewed_at,
            "notes": row["notes"].strip(),
            "review_file": review_path.name,
        }
        imported += 1

    # Write only after every row has passed validation.
    output_path.write_text(
        json.dumps(
            approved, ensure_ascii=False, indent=2
        ) + "\n",
        encoding="utf-8",
    )

    print(f"New approved mappings imported: {imported}")
    print(f"Already imported and unchanged: {unchanged}")
    print(f"Deferred rows: {deferred}")
    print(f"Pending rows: {pending}")
    print(f"Total approved mappings: {len(approved)}")
    print(f"\nSaved to: {output_path}")


if __name__ == "__main__":
    main()