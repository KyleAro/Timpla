"""Prepare and audit the entire recipe corpus. Never fit a model or invent labels."""
import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from merge_semantic_review import project, validate_record

ROOT = Path(__file__).resolve().parent
ID_PATTERN = re.compile(r"[a-z][a-z0-9_]*")


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False).encode("utf-8")).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_csv(path, fields, rows):
    with path.open("x", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def assemble(recipes, proposals, approved, role_reviews, source_checks, deferred_reviews=(), requirement_resolutions=None):
    """Construct full-corpus artifacts without changing the input files."""
    ids = [r["id"] for r in recipes]
    if not recipes or len(ids) != len(set(ids)):
        raise ValueError("Nonempty corpus and unique recipe IDs required")
    vocabulary = Counter(line.casefold() for r in recipes for line in r["full_ingredients"])
    if requirement_resolutions is not None and set(requirement_resolutions) != set(vocabulary):
        raise ValueError("Requirement resolution vocabulary does not match the corpus")
    if requirement_resolutions is not None:
        contexts = {}
        instruction_contexts = {}
        for recipe in recipes:
            for line in recipe['full_ingredients']:
                contexts.setdefault(line.casefold(), {})[recipe['id']] = digest(recipe['full_ingredients'])
                instruction_contexts.setdefault(line.casefold(), {})[recipe['id']] = digest(recipe.get('instructions', []))
        for line, record in requirement_resolutions.items():
            if record.get('context_ingredient_hashes') is not None and record['context_ingredient_hashes'] != contexts[line]:
                raise ValueError('Recipe ingredients changed after semantic annotation')
            if record.get('context_instruction_hashes') is not None and record['context_instruction_hashes'] != instruction_contexts[line]:
                raise ValueError('Recipe instructions changed after semantic annotation')
            if record.get('status') == 'contextual':
                if set(record.get('per_recipe', {})) != set(contexts[line]):
                    raise ValueError('Contextual decisions must cover exact recipe contexts')
                for rid in contexts[line]:
                    validate_record(project(record, rid))
            else:
                validate_record(record)
    proposed = {p["ingredient_line"]: p for p in proposals}
    if len(proposed) != len(proposals) or set(proposed) != set(vocabulary):
        raise ValueError("Proposal vocabulary does not match the cleaned corpus")
    for line, mapping in approved.items():
        if line not in vocabulary or not mapping.get("reviewed_by") or not mapping.get("reviewed_at"):
            raise ValueError("Approved mapping lacks vocabulary membership or review provenance")
        values = mapping["canonical_ingredients"]
        if not values or len(set(values)) != len(values) or not all(ID_PATTERN.fullmatch(v) for v in values):
            raise ValueError("Invalid approved ingredient IDs")
    roles = {r["id"]: r for r in role_reviews}
    sources = {r["recipe_id"]: r for r in source_checks}
    if len(roles) != len(role_reviews) or len(sources) != len(source_checks):
        raise ValueError("Duplicate recipe reviews")
    if (set(roles) | set(sources)) - set(ids):
        raise ValueError("Review refers to an unknown recipe")
    deferred = {row["ingredient_line"]: row for row in deferred_reviews if row.get("decision") == "defer"}
    mapping_rows, role_rows, source_rows, corpus = [], [], [], []
    flag_counts = Counter()
    mapped_occurrences = 0
    complete_mappings = 0
    for line, occurrences in sorted(vocabulary.items(), key=lambda pair: (-pair[1], pair[0])):
        review = approved.get(line)
        mapping_rows.append({
            "ingredient_line": line, "occurrences": occurrences,
            "suggested_ingredients": ";".join(proposed[line]["canonical_ingredients"]),
            "approved_ingredients": ";".join(review["canonical_ingredients"]) if review else "",
            "decision": "approve" if review else ("defer" if line in deferred else ""),
            "notes": review.get("notes", "") if review else deferred.get(line, {}).get("notes", ""),
            "reviewed_by": review["reviewed_by"] if review else "",
            "reviewed_at": review["reviewed_at"] if review else "",
        })
    for recipe in recipes:
        rid = recipe["id"]
        reviewed = roles.get(rid)
        role_by_id = {}
        if reviewed:
            metadata = reviewed["ingredient_role_review"]
            if metadata.get("status") != "approved" or not metadata.get("reviewed_by"):
                raise ValueError("Role review must preserve actual approval provenance")
            for role in ("major", "supporting", "optional"):
                for value in reviewed[role]:
                    if value in role_by_id:
                        raise ValueError("Ingredient roles overlap")
                    role_by_id[value] = role
        annotations = []
        all_ids = set()
        for index, line in enumerate(recipe["full_ingredients"], start=1):
            key = line.casefold()
            resolution = project(requirement_resolutions[key], rid) if requirement_resolutions is not None else None
            mapping = approved.get(key)
            canonical = mapping["canonical_ingredients"] if mapping else []
            all_ids.update(canonical)
            mapped_occurrences += bool(mapping)
            # One row per ingredient identity, or one unresolved row for the original line.
            for value in canonical or [""]:
                assigned = role_by_id.get(value, "")
                role_rows.append({
                    "recipe_id": rid, "recipe_name": recipe["name"], "line_number": index,
                    "ingredient_line": key, "canonical_ingredient": value,
                    "suggested_ingredients": ";".join(proposed[key]["canonical_ingredients"]),
                    "mapping_status": "approved" if mapping else "pending",
                    "role": assigned, "decision": "approve" if assigned else "",
                    "reviewer": reviewed["ingredient_role_review"]["reviewed_by"] if assigned else "",
                    "notes": "",
                    "requirement_json": json.dumps(resolution.get("requirement"), sort_keys=True) if resolution else "",
                    "normalization_status": resolution["status"] if resolution else "",
                })
            annotations.append({"original_line": line, "canonical_ingredients": canonical,
                                "mapping_status": "approved" if mapping else "pending",
                                "mapping_method": mapping.get("review_type", "owner_recorded_review") if mapping else None,
                                "mapping_reviewer": mapping.get("reviewed_by") if mapping else None})
            if resolution:
                annotations[-1]["requirement_resolution"] = resolution
        mapping_complete = bool(annotations) and all(a["mapping_status"] == "approved" for a in annotations)
        complete_mappings += mapping_complete
        if reviewed and (not mapping_complete or set(role_by_id) != all_ids):
            raise ValueError("Reviewed roles disagree with current approved ingredient identities")
        source = sources.get(rid)
        if source and source["ingredient_lines_sha256"] != digest(recipe["full_ingredients"]):
            raise ValueError("Recipe ingredients changed after source comparison")
        urls = sorted({s["source_url"] for s in recipe["sources"] if s.get("source_url")})
        if source:
            urls = sorted(set(urls + [source["source_url"]]))
        flags = []
        if len(annotations) <= 3:
            flags.append("short_list_check_not_proof_of_incompleteness")
        if any(re.search(r"\b\d+\s+recipe\b", a["original_line"], re.I) for a in annotations):
            flags.append("referenced_subrecipe_requires_check")
        if any(re.search(r"\bor\b", a["original_line"], re.I) for a in annotations):
            flags.append("alternative_or_usage_note_requires_check")
        if not urls:
            flags.append("original_recipe_url_missing")
        if requirement_resolutions is None and not mapping_complete:
            flags.append("ingredient_mapping_incomplete")
        elif requirement_resolutions is not None and any(
                a['requirement_resolution']['status'] not in {'resolved', 'non_ingredient'} for a in annotations):
            flags.append('ingredient_requirement_resolution_incomplete')
        source_issues = [a['original_line'] for a in annotations
                         if a.get('requirement_resolution', {}).get('status') == 'source_issue']
        if source_issues:
            flags.append('ingredient_source_issue_requires_correction')
        terminology_lines = [a['original_line'] for a in annotations
                             if a.get('requirement_resolution', {}).get('terminology_review_required')]
        if terminology_lines:
            flags.append('ingredient_terminology_review_required')
        flag_counts.update(flags)
        source_rows.append({"recipe_id": rid, "recipe_name": recipe["name"],
                            "source_urls": " | ".join(urls), "ingredient_line_count": len(annotations),
                            "flags": " | ".join(flags),
                            "status": source["status"] if source else "pending",
                            "checked_by": source["checked_by"] if source else "",
                            "filipino_scope_decision": "approved" if reviewed else "pending",
                            "notes": ""})
        corpus.append({"id": rid, "name": recipe["name"], "ingredients": annotations,
                       "approved_ingredient_ids": sorted(all_ids),
                       "mapping_complete": mapping_complete,
                       "major": reviewed["major"] if reviewed else [],
                       "supporting": reviewed["supporting"] if reviewed else [],
                       "optional": reviewed["optional"] if reviewed else [],
                       "ingredient_role_review": reviewed["ingredient_role_review"] if reviewed else None,
                       "source_check": source, "source_urls": urls,
                       "original_source_rows": [{"collection": s["collection"],
                           "csv_record_number": s["csv_record_number"]} for s in recipe["sources"]],
                       "quality_flags": flags, "ready_for_training": False})
        if requirement_resolutions is not None:
            corpus[-1]["requirement_resolution_complete"] = all(
                a["requirement_resolution"]["status"] in {"resolved", "non_ingredient"} for a in annotations)
            corpus[-1]['ingredient_source_issues'] = source_issues
            corpus[-1]['ingredient_terminology_review_lines'] = terminology_lines
    report = {"scope": "entire cleaned corpus; not a pilot or demo",
              "source_rows_preserved": sum(len(r["sources"]) for r in recipes),
              "recipes": len(recipes), "ingredient_line_occurrences": sum(vocabulary.values()),
              "distinct_ingredient_lines": len(vocabulary), "approved_mapping_entries": len(approved),
              "automated_mapping_entries": sum(m.get("review_type") == "automated_rule_acceptance" for m in approved.values()),
              "owner_recorded_mapping_entries": sum(m.get("review_type") != "automated_rule_acceptance" for m in approved.values()),
              "approved_mapping_occurrences": mapped_occurrences,
              "approved_mapping_coverage_percent": round(100 * mapped_occurrences / max(1, sum(vocabulary.values())), 2),
              "complete_ingredient_mappings": complete_mappings,
              "recipes_with_approved_roles": len(roles), "recipe_role_review_rows": len(role_rows),
              "recipes_with_source_comparison": len(sources),
              "recipes_with_source_url": sum(bool(r["source_urls"]) for r in corpus),
              "quality_flag_counts": dict(flag_counts),
              "ready_for_training": False, "model_training_performed": False,
              "pending": ["Complete ingredient identity review across the corpus",
                          "Check original recipe completeness and referenced subrecipes",
                          "Review essential/supporting/optional roles per recipe",
                          "Resolve ingredient alternatives and compatibility policies explicitly",
                          "Create and human-review realistic inventory ranking scenarios",
                          "Group related inventories into train/validation/test splits",
                          "Collect human relevance judgments and validate their coverage"],
              "note": "Mechanical preparation is complete for every record. Semantic review is incomplete; no labels or model accuracy are invented."}
    if requirement_resolutions is not None:
        statuses = Counter()
        for recipe in corpus:
            statuses.update(a['requirement_resolution']['status'] for a in recipe['ingredients'])
        report["structured_normalization_occurrence_counts"] = dict(statuses)
        report["structured_identity_resolution_percent"] = round(100*statuses["resolved"]/sum(vocabulary.values()), 2)
        report['food_identity_resolution_percent'] = round(100 * statuses['resolved'] / max(1, sum(statuses.values()) - statuses['non_ingredient']), 2)
        report["complete_requirement_representations"] = sum(r["requirement_resolution_complete"] for r in corpus)
        report['review_disposition_percent'] = round(100 * (sum(statuses.values()) - statuses['unresolved']) / sum(statuses.values()), 2)
        report['recipes_with_ingredient_source_issues'] = sum(bool(r['ingredient_source_issues']) for r in corpus)
        report['recipes_with_terminology_review_flags'] = sum(bool(r['ingredient_terminology_review_lines']) for r in corpus)
        if not statuses['unresolved'] and not statuses['source_issue']:
            report['pending'].remove('Complete ingredient identity review across the corpus')
        report['note'] = 'Full corpus and original source references retained. Structured normalization status is separate from role/source/relevance review; no labels or model accuracy are invented.'
        report["normalization_note"] = "Flat accepted mappings and structured any_of expressions have distinct counts. Non-ingredient fragments are accounted for but are not ingredient matches. No unknown text was forced into an ID."
    return corpus, mapping_rows, role_rows, source_rows, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "data" / "preparation" / "v1")
    parser.add_argument("--requirements", type=Path, help="Versioned structured ingredient-resolution JSON")
    args = parser.parse_args()
    if args.requirements:
        args.requirements = args.requirements.resolve()
    if args.output.exists():
        raise SystemExit("Use a new versioned output folder; review files are never overwritten.")
    inputs = {"recipes": ROOT / "data/processed/recipes.cleaned.json",
              "proposals": ROOT / "data/processed/ingredient_mapping.proposed.json",
              "approved": ROOT / "data/processed/ingredient_mapping.approved.json",
              "role_reviews": ROOT / "data/processed/recipes.pilot.roles.json",
              "source_checks": ROOT / "data/source_checks.json"}
    review_csv = ROOT / "data/processed/ingredient_review.batch01.csv"
    with review_csv.open(encoding="utf-8-sig", newline="") as stream:
        deferred_reviews = list(csv.DictReader(stream))
    group_csv = ROOT / "data/processed/ingredient_groups.review.csv"
    member_path = ROOT / "data/processed/ingredient_groups.members.json"
    if group_csv.exists():
        members = read(member_path)
        with group_csv.open(encoding="utf-8-sig", newline="") as stream:
            for group in csv.DictReader(stream):
                if group["decision"] == "defer":
                    deferred_reviews.extend({"ingredient_line": line, "decision": "defer", "notes": group["notes"]}
                                            for line in members[group["lookup_text"]])
        inputs["group_review_csv"] = group_csv
        inputs["group_members"] = member_path
    if args.requirements:
        inputs["requirement_resolutions"] = args.requirements
    corpus, mappings, roles, sources, report = assemble(
        **{key: read(inputs[key]) for key in ("recipes", "proposals", "approved", "role_reviews", "source_checks")},
        deferred_reviews=deferred_reviews,
        requirement_resolutions=read(args.requirements) if args.requirements else None)
    inputs["mapping_review_csv"] = review_csv
    args.output.mkdir(parents=True)
    write_json(args.output / "recipes.prepared.json", corpus)
    write_json(args.output / "readiness.json", report)
    write_csv(args.output / "ingredient_review.csv", list(mappings[0]), mappings)
    write_csv(args.output / "recipe_roles.review.csv", list(roles[0]), roles)
    write_csv(args.output / "source_quality.review.csv", list(sources[0]), sources)
    outputs = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in args.output.iterdir() if p.is_file()}
    write_json(args.output / "manifest.json", {
        "created_at": datetime.now(timezone.utc).isoformat(), "script": Path(__file__).name,
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "input_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs.values()},
        "output_sha256": outputs,
        "policy": "No training. No fabricated human reviews or relevance labels. Preserve original data and review provenance."})
    print(json.dumps(report, indent=2))
    print(f"\nSaved full-corpus preparation to: {args.output}")


if __name__ == "__main__":
    main()
