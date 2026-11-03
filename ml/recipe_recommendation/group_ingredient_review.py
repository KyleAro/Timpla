import csv
import json
from collections import defaultdict
from pathlib import Path


MODEL_DIR = Path(__file__).resolve().parent
DATA_DIR = MODEL_DIR / "data" / "processed"


def main():
    input_path = DATA_DIR / "ingredient_mapping.proposed.json"
    csv_path = DATA_DIR / "ingredient_groups.review.csv"
    json_path = DATA_DIR / "ingredient_groups.members.json"

    if csv_path.exists() or json_path.exists():
        raise SystemExit(
            "Grouped review files already exist. "
            "Keep them to preserve review work."
        )

    mappings = json.loads(
        input_path.read_text(encoding="utf-8")
    )

    groups = defaultdict(list)

    for item in mappings:
        groups[item["lookup_text"]].append(item)

    ordered_groups = sorted(
        groups.items(),
        key=lambda pair: (
            -sum(item["occurrences"] for item in pair[1]),
            pair[0],
        ),
    )

    fields = [
        "lookup_text",
        "distinct_original_lines",
        "total_occurrences",
        "suggested_ingredients",
        "example_original_lines",
        "approved_ingredients",
        "decision",
        "notes",
    ]

    members = {}

    with csv_path.open(
        "x", encoding="utf-8-sig", newline=""
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()

        for lookup, items in ordered_groups:
            suggestions = {
                tuple(item["canonical_ingredients"])
                for item in items
                if item["canonical_ingredients"]
            }

            # Conflicting suggestions require explicit review.
            suggested = ""
            notes = ""

            if len(suggestions) == 1:
                suggested = ";".join(next(iter(suggestions)))
            elif len(suggestions) > 1:
                notes = "Conflicting automatic suggestions; review required."

            originals = [
                item["ingredient_line"] for item in items
            ]

            members[lookup] = originals

            writer.writerow({
                "lookup_text": lookup,
                "distinct_original_lines": len(items),
                "total_occurrences": sum(
                    item["occurrences"] for item in items
                ),
                "suggested_ingredients": suggested,
                "example_original_lines": " | ".join(originals[:4]),
                "approved_ingredients": "",
                "decision": "",
                "notes": notes,
            })

    json_path.write_text(
        json.dumps(
            members, ensure_ascii=False, indent=2
        ) + "\n",
        encoding="utf-8",
    )

    print(f"Original distinct ingredient lines: {len(mappings)}")
    print(f"Ingredient lookup groups: {len(groups)}")
    print(
        "Ingredient occurrences preserved: "
        f"{sum(item['occurrences'] for item in mappings)}"
    )

    print("\nMost frequent lookup groups:")

    for lookup, items in ordered_groups[:30]:
        occurrences = sum(
            item["occurrences"] for item in items
        )
        print(
            f"{occurrences:>5} occurrences | "
            f"{len(items):>4} variants | {lookup}"
        )

    print(f"\nReview sheet: {csv_path}")
    print(f"Original-line membership: {json_path}")


if __name__ == "__main__":
    main()