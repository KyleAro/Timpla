import csv
import hashlib
import html
import json
import re
import unicodedata
from pathlib import Path


MODEL_DIR = Path(__file__).resolve().parent
EXTERNAL_DIR = MODEL_DIR / "data" / "external"
OUTPUT_DIR = MODEL_DIR / "data" / "processed"

SOURCES = [
    {
        "name": "filipino_recipes_2k",
        "full_field": "ingredients",
        "full_separator": "|",
        "names_separator": "|",
        "steps_separator": "|",
    },
    {
        "name": "filtered_filipino_recipes",
        "full_field": "full_ingredients",
        "full_separator": "\n",
        "names_separator": ",",
        "steps_separator": "\n",
    },
]


def clean_text(value):
    """Clean formatting without removing ingredient details."""
    text = html.unescape(value or "")
    text = unicodedata.normalize("NFC", text)
    return re.sub(r"\s+", " ", text).strip()


def split_items(value, separator):
    """Split before cleaning so newline boundaries are preserved."""
    return [
        cleaned
        for item in (value or "").split(separator)
        if (cleaned := clean_text(item))
    ]


def unique_names(items):
    """Remove repeated names while preserving their original order."""
    result = []
    seen = set()

    for item in items:
        key = item.casefold()
        if key not in seen:
            seen.add(key)
            result.append(item)

    return result


def record_fingerprint(name, ingredients, instructions):
    """Compare full records, rather than recipe titles alone."""
    content = {
        "name": name.casefold(),
        "ingredients": [item.casefold() for item in ingredients],
        "instructions": [item.casefold() for item in instructions],
    }

    encoded = json.dumps(
        content, ensure_ascii=False, sort_keys=True
    ).encode("utf-8")

    return hashlib.sha256(encoded).hexdigest()


def main():
    records = {}
    source_counts = {}
    merged_duplicates = 0

    for source in SOURCES:
        path = EXTERNAL_DIR / source["name"] / "recipes.csv"

        with path.open(
            "r", encoding="utf-8-sig", newline=""
        ) as file:
            reader = csv.DictReader(file)

            required_columns = {
                "recipe_name",
                source["full_field"],
                "ingredient_names",
                "instructions",
            }

            missing = required_columns - set(reader.fieldnames or [])
            if missing:
                raise ValueError(
                    f"{path.name}: missing columns {sorted(missing)}"
                )

            count = 0

            for row_number, row in enumerate(reader, start=2):
                count += 1

                name = clean_text(row["recipe_name"])

                ingredients = split_items(
                    row[source["full_field"]],
                    source["full_separator"],
                )

                ingredient_names = unique_names(
                    split_items(
                        row["ingredient_names"],
                        source["names_separator"],
                    )
                )

                instructions = split_items(
                    row["instructions"],
                    source["steps_separator"],
                )

                fingerprint = record_fingerprint(
                    name, ingredients, instructions
                )

                # Keep every source row, including duplicate records.
                origin = {
                    "collection": source["name"],
                    "csv_record_number": row_number,
                    "source_url": clean_text(row.get("url")),
                    "provided_ingredient_names": ingredient_names,
                    "raw_record": row,
                }

                if fingerprint in records:
                    records[fingerprint]["sources"].append(origin)
                    merged_duplicates += 1
                    continue

                flags = []

                if not name:
                    flags.append("missing_recipe_name")

                if not ingredients:
                    flags.append("missing_full_ingredients")

                if not ingredient_names:
                    flags.append("missing_provided_ingredient_names")

                if not instructions:
                    flags.append("missing_instructions")

                # This is a review hint, not proof of missing ingredients.
                if len(ingredient_names) < len(ingredients):
                    flags.append(
                        "provided_names_shorter_than_full_ingredient_list"
                    )

                records[fingerprint] = {
                    "id": fingerprint,
                    "name": name,
                    "full_ingredients": ingredients,
                    "instructions": instructions,
                    "review_flags": flags,
                    "ingredient_review_status": "pending",
                    "sources": [origin],
                }

            source_counts[source["name"]] = count

    cleaned_records = list(records.values())

    summary = {
        "source_rows": source_counts,
        "total_source_rows": sum(source_counts.values()),
        "merged_duplicate_rows": merged_duplicates,
        "output_records": len(cleaned_records),
        "records_with_review_flags": sum(
            bool(record["review_flags"])
            for record in cleaned_records
        ),
        "ingredient_roles_assigned": False,
        "ready_for_training": False,
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    outputs = {
        "recipes.cleaned.json": cleaned_records,
        "cleaning_report.json": summary,
    }

    for filename, content in outputs.items():
        output_path = OUTPUT_DIR / filename
        output_path.write_text(
            json.dumps(content, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    print(json.dumps(summary, indent=2))
    print(f"\nSaved cleaned data to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()