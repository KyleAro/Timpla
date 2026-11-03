import argparse
import csv
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


MODEL_DIR = Path(__file__).resolve().parent
DATA_DIR = MODEL_DIR / "data" / "processed"

ID_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reviewer", required=True)
    args = parser.parse_args()

    reviewer = args.reviewer.strip()
    if not reviewer:
        raise ValueError("Reviewer name must not be blank.")

    review_path = DATA_DIR / "ingredient_groups.review.csv"
    members_path = DATA_DIR / "ingredient_groups.members.json"
    approved_path = DATA_DIR / "ingredient_mapping.approved.json"

    proposals = load_json(
        DATA_DIR / "ingredient_mapping.proposed.json"
    )
    members = load_json(members_path)
    approved = load_json(approved_path)

    expected_members = {}
    occurrences = {}

    for item in proposals:
        lookup = item["lookup_text"]

        expected_members.setdefault(lookup, set()).add(
            item["ingredient_line"]
        )
        occurrences[item["ingredient_line"]] = item["occurrences"]

    # Check that membership still matches the normalization output.
    if set(members) != set(expected_members):
        raise ValueError("Group membership is stale or incomplete.")

    for lookup, lines in members.items():
        if (
            len(lines) != len(set(lines))
            or set(lines) != expected_members[lookup]
        ):
            raise ValueError(
                f"Group membership mismatch: {lookup!r}"
            )

    with review_path.open(
        encoding="utf-8-sig", newline=""
    ) as file:
        rows = list(csv.DictReader(file))

    keys = [row["lookup_text"] for row in rows]

    if len(keys) != len(set(keys)) or set(keys) != set(members):
        raise ValueError(
            "Review CSV must contain each lookup group exactly once."
        )

    updated = dict(approved)
    imported = 0
    unchanged = 0
    reviewed_at = datetime.now(timezone.utc).isoformat()

    review_hash = hashlib.sha256(
        review_path.read_bytes()
    ).hexdigest()

    for row in rows:
        lookup = row["lookup_text"]
        decision = row["decision"].strip().lower()
        text = row["approved_ingredients"].strip()

        if decision not in {"", "approve", "defer"}:
            raise ValueError(
                f"Unknown decision for {lookup!r}: {decision!r}"
            )

        if decision != "approve":
            if text:
                raise ValueError(
                    f"{lookup!r}: ingredient IDs entered without approval."
                )
            continue

        canonical = [value.strip() for value in text.split(";")]

        if (
            not all(ID_PATTERN.fullmatch(value) for value in canonical)
            or len(canonical) != len(set(canonical))
        ):
            raise ValueError(
                f"Invalid or repeated ingredient IDs: {lookup!r}"
            )

        for line in members[lookup]:
            if line in updated:
                existing = updated[line]["canonical_ingredients"]

                if set(existing) != set(canonical):
                    raise ValueError(
                        f"Conflicting approval for {line!r}. "
                        "Nothing has been saved."
                    )

                unchanged += 1
                continue

            updated[line] = {
                "canonical_ingredients": canonical,
                "reviewed_by": reviewer,
                "reviewed_at": reviewed_at,
                "notes": row["notes"].strip(),
                "review_file": review_path.name,
                "lookup_group": lookup,
                "review_file_sha256": review_hash,
            }
            imported += 1

    # All rows are validated before changing the approved file.
    if imported:
        backup_path = DATA_DIR / (
            "ingredient_mapping.approved.before-groups.bak"
        )

        if not backup_path.exists():
            with backup_path.open("xb") as file:
                file.write(approved_path.read_bytes())

        temporary_path = approved_path.with_suffix(".json.tmp")

        with temporary_path.open("x", encoding="utf-8") as file:
            json.dump(
                updated, file, ensure_ascii=False, indent=2
            )
            file.write("\n")

        temporary_path.replace(approved_path)

    covered = sum(occurrences[line] for line in updated)
    total = sum(occurrences.values())

    print(f"New individual mappings imported: {imported}")
    print(f"Existing mappings preserved: {unchanged}")
    print(f"Total approved individual mappings: {len(updated)}")
    print(f"Approved ingredient occurrences: {covered}/{total}")
    print(f"Approved occurrence coverage: {covered / total:.1%}")
    print(
        "Deferred groups: "
        f"{sum(row['decision'].strip().lower() == 'defer' for row in rows)}"
    )


if __name__ == "__main__":
    main()













