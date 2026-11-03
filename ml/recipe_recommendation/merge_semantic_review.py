"""Validate and merge a frozen semantic annotation pass. Never train a model."""
import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
ID = re.compile(r"[a-z][a-z0-9_]*")
STATUSES = {"resolved", "non_ingredient", "source_issue", "unresolved"}


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def validate_expression(value):
    if not isinstance(value, dict) or len(value) != 1:
        raise ValueError("Invalid requirement expression")
    key = next(iter(value))
    if key in {"ingredient_id", "equipment_id"}:
        if not isinstance(value[key], str) or not ID.fullmatch(value[key]):
            raise ValueError("Invalid ingredient or equipment ID")
    elif key in {"all_of", "any_of"}:
        if not isinstance(value[key], list) or not value[key]:
            raise ValueError("Invalid requirement children")
        for child in value[key]:
            validate_expression(child)
    else:
        raise ValueError("Unknown requirement operator")


def validate_record(record, *, allow_unresolved=True):
    allowed = STATUSES if allow_unresolved else STATUSES - {"unresolved"}
    if not isinstance(record, dict) or record.get("status") not in allowed or not record.get("basis", "").strip():
        raise ValueError("Invalid requirement resolution status or provenance")
    if record["status"] == "resolved":
        validate_expression(record.get("requirement"))
        if not any(kind == 'ingredient_id' for kind, _ in leaves(record['requirement'])):
            raise ValueError('Resolved food requirement contains only equipment')
    elif record.get("requirement") is not None:
        raise ValueError("Only resolved records can carry a food requirement")
    if record.get('equipment_requirement'):
        validate_expression(record['equipment_requirement'])
        if any(kind != 'equipment_id' for kind, _ in leaves(record['equipment_requirement'])):
            raise ValueError('Equipment metadata contains a food identity')


def project(record, recipe_id):
    """Select an exact recipe context; never union context-dependent meanings."""
    if record.get("status") != "contextual":
        return record
    if recipe_id not in record.get("per_recipe", {}):
        raise ValueError("Missing recipe context in semantic review")
    result = {k: v for k, v in record.items() if k not in {"per_recipe", "status", "requirement", "basis"}}
    result.update(record["per_recipe"][recipe_id])
    return result


def leaves(expression):
    """Walk retained requirements without erasing their logical operators."""
    if not expression:
        return
    key = next(iter(expression))
    if key in {'ingredient_id', 'equipment_id'}:
        yield key, expression[key]
    else:
        for child in expression[key]:
            yield from leaves(child)


def validate_scope(partitions, recipes):
    originals = {r['id']: r for r in recipes}
    references = {}
    counts = Counter()
    for recipe in recipes:
        for line in recipe['full_ingredients']:
            references.setdefault(line.casefold(), set()).add(recipe['id'])
            counts[line.casefold()] += 1
    for batch in partitions:
        for row in batch:
            line = row['ingredient_line']
            if (len({r['id'] for r in row['recipes']}) != len(row['recipes']) or
                    row['occurrences'] != counts[line] or {r['id'] for r in row['recipes']} != references.get(line)):
                raise ValueError('Partition does not match original ingredient occurrences')
            for context in row['recipes']:
                original = originals[context['id']]
                if context['full_ingredients'] != original['full_ingredients'] or context.get('instructions', []) != original.get('instructions', []):
                    raise ValueError('Partition recipe context differs from frozen source')
                expected = hashlib.sha256(json.dumps(original['full_ingredients'], ensure_ascii=False).encode('utf-8')).hexdigest()
                if context['ingredient_lines_sha256'] != expected:
                    raise ValueError('Invalid partition ingredient hash')


def align_decisions(batches, alignment):
    aliases = alignment['aliases']
    if not alignment.get('basis') or not alignment.get('reviewer'):
        raise ValueError('Identity alignment requires provenance')
    if any(not ID.fullmatch(k) or not ID.fullmatch(v) or v in aliases for k, v in aliases.items()):
        raise ValueError('Invalid or chained identity alignment')
    result = deepcopy(batches)
    def align_expression(expression, changes):
        if not expression:
            return
        for key, value in expression.items():
            if key == 'ingredient_id' and value in aliases:
                expression[key] = aliases[value]
                changes[value] = aliases[value]
            elif key in {'all_of', 'any_of'}:
                for child in value:
                    align_expression(child, changes)
    for batch in result:
        for record in batch:
            changes = {}
            original = deepcopy(record)
            if record['status'] == 'contextual':
                for child in record['per_recipe'].values():
                    align_expression(child.get('requirement'), changes)
            else:
                align_expression(record.get('requirement'), changes)
            if changes:
                record['identity_alignment'] = dict(changes=changes, basis=alignment['basis'], reviewer=alignment['reviewer'])
                record['before_identity_alignment'] = original
    return result


def merge(baseline, partitions, decisions):
    result = deepcopy(baseline)
    seen = set()
    for batch, rows in zip(partitions, decisions, strict=True):
        expected = {r["ingredient_line"]: r for r in batch}
        if len(expected) != len(batch) or seen & expected.keys():
            raise ValueError("Duplicate or overlapping input partition")
        actual = {r["ingredient_line"]: r for r in rows}
        if len(actual) != len(rows) or actual.keys() != expected.keys():
            raise ValueError("Semantic decisions must cover each assigned line exactly once")
        for line, record in actual.items():
            if line not in baseline or baseline[line]["status"] != "unresolved":
                raise ValueError("Semantic review may only replace frozen unresolved lines")
            if record.get("annotation_type") != "ai_semantic_annotation" or not record.get("reviewer"):
                raise ValueError("AI annotation provenance is required")
            contexts = {r["id"] for r in expected[line]["recipes"]}
            if record.get("status") == "contextual":
                if set(record.get("per_recipe", {})) != contexts:
                    raise ValueError("Contextual decisions must cover exact assigned recipe contexts")
                for child in record["per_recipe"].values():
                    validate_record(child, allow_unresolved=False)
            else:
                validate_record(record, allow_unresolved=False)
            replacement = {k: v for k, v in record.items() if k != "ingredient_line"}
            replacement["previous_resolution"] = deepcopy(baseline[line])
            replacement["context_ingredient_hashes"] = {
                r["id"]: r["ingredient_lines_sha256"] for r in expected[line]["recipes"]}
            replacement["context_instruction_hashes"] = {
                r["id"]: hashlib.sha256(json.dumps(r.get("instructions", []), ensure_ascii=False).encode("utf-8")).hexdigest()
                for r in expected[line]["recipes"]}
            result[line] = replacement
        seen.update(expected)
    if seen != {k for k, v in baseline.items() if v["status"] == "unresolved"}:
        raise ValueError("Review does not cover all frozen unresolved lines")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review", type=Path, default=ROOT / "data/normalization/review_20261029")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit("Use a new output version; existing review snapshots are retained")
    frozen = read(args.review / "manifest.json")
    for name, expected in frozen["input_sha256"].items():
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f"Frozen input changed: {name}")
    inputs = [args.review / "baseline_requirements.json", args.review / "manifest.json"]
    batches, judgments = [], []
    for index in range(1, 4):
        source = args.review / f"partition_{index:02d}.json"
        decision = args.review / f"partition_{index:02d}.decisions.json"
        inputs.extend([source, decision])
        batches.append(read(source))
        judgments.append(read(decision))
    recipes = read(ROOT / "data/processed/recipes.cleaned.json")
    validate_scope(batches, recipes)
    baseline = read(inputs[0])
    alignment_path = args.review / 'identity_alignment.json'
    if alignment_path.exists():
        inputs.append(alignment_path)
        judgments = align_decisions(judgments, read(alignment_path))
    merged = merge(baseline, batches, judgments)
    counts = Counter(project(merged[line.casefold()], r["id"])["status"]
                     for r in recipes for line in r["full_ingredients"])
    unresolved = counts["unresolved"]
    total = sum(counts.values())
    report = {"recipes": len(recipes), "ingredient_line_occurrences": total,
              "occurrence_counts": dict(counts),
              'semantic_annotation_distinct_lines': sum(len(batch) for batch in batches),
              'semantic_annotation_occurrences': sum(row['occurrences'] for batch in batches for row in batch),
              'frozen_inputs_verified': True,
              'prior_resolutions_preserved': sum(record['status'] != 'unresolved' for record in baseline.values()),
              'baseline_occurrence_counts': dict(Counter(baseline[line.casefold()]['status']
                                                    for recipe in recipes for line in recipe['full_ingredients'])),
              "review_disposition_percent": round(100 * (total - unresolved) / total, 2),
              "identity_resolution_percent_of_all_lines": round(100 * counts["resolved"] / total, 2),
              "note": "Review disposition includes explicit source issues and non-food fragments; it is not training readiness or independent human validation.",
              "ready_for_training": False, "model_training_performed": False}
    issues, registry, terminology = [], {}, []
    for recipe in recipes:
        for index, line in enumerate(recipe['full_ingredients'], start=1):
            decision = project(merged[line.casefold()], recipe['id'])
            if decision['status'] == 'source_issue':
                issues.append({'recipe_id': recipe['id'], 'recipe_name': recipe['name'],
                               'line_number': index, 'ingredient_line': line, 'basis': decision['basis'],
                               'sources': recipe['sources']})
            if decision.get('terminology_review_required'):
                terminology.append({'recipe_id': recipe['id'], 'recipe_name': recipe['name'],
                                    'line_number': index, 'ingredient_line': line,
                                    'requirement': decision.get('requirement'), 'source_gloss': decision.get('source_gloss'),
                                    'basis': decision['basis']})
            for kind, identity in set(leaves(decision.get('requirement'))):
                entry = registry.setdefault((kind, identity), {'kind': kind, 'id': identity,
                                            'line_occurrences': 0, 'examples': []})
                entry['line_occurrences'] += 1
                if len(entry['examples']) < 4 and line not in entry['examples']:
                    entry['examples'].append(line)
    report['recipes_with_source_issues'] = len({row['recipe_id'] for row in issues})
    report['terminology_flag_occurrences'] = len(terminology)
    report['recipes_with_terminology_flags'] = len({row['recipe_id'] for row in terminology})
    report['food_identity_resolution_percent'] = round(100 * counts['resolved'] / max(1, total - counts['non_ingredient']), 2)
    report['complete_requirement_representations'] = sum(all(
        project(merged[line.casefold()], recipe['id'])['status'] in {'resolved', 'non_ingredient'}
        for line in recipe['full_ingredients']) for recipe in recipes)
    args.output.mkdir(parents=True)
    for name, data in [("ingredient_requirements.json", merged), ("report.json", report),
                       ('source_issues.json', issues), ('terminology_review.json', terminology),
                       ('identity_registry.json', sorted(registry.values(), key=lambda r: (r['kind'], r['id'])))]:
        (args.output / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    outputs = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in args.output.iterdir()}
    manifest = {"input_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
                "output_sha256": outputs, "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "model_training_performed": False}
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
