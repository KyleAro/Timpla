"""Read-only checks before full-corpus training; never fit or export a model."""
import csv
import hashlib
from importlib import metadata
import json
from pathlib import Path

from ranker import FEATURES, read_json, training_groups


def check_preparation(folder, recipe_review_folder=None):
    folder = Path(folder)
    blockers = []
    report = {
        "algorithm": "LightGBM LambdaRank",
        "scope": "full prepared recipe corpus",
        "preparation_directory": str(folder),
        "feature_names": FEATURES,
        "model_training_performed": False,
    }
    try:
        manifest = read_json(folder / "manifest.json")
        for name, expected in manifest["output_sha256"].items():
            # A manifest must refer only to direct files in this snapshot.
            if Path(name).name != name:
                raise ValueError("Invalid snapshot filename")
            actual = hashlib.sha256((folder / name).read_bytes()).hexdigest()
            if actual != expected:
                raise ValueError(f"Snapshot file changed: {name}; regenerate to preserve provenance")
        recipes = read_json(folder / "recipes.prepared.json")
        report["recipes"] = len(recipes)
        counts = {
            "ingredient_mapping_incomplete": sum(not r["mapping_complete"] for r in recipes),
            "recipe_roles_unreviewed": sum(not r.get("ingredient_role_review") or
                r["ingredient_role_review"].get("status") != "approved" for r in recipes),
            "source_comparison_pending": sum(not r.get("source_check") for r in recipes),
        }
        if recipes and "requirement_resolution_complete" in recipes[0]:
            counts.pop("ingredient_mapping_incomplete")
            counts["ingredient_requirement_resolution_incomplete"] = sum(not r["requirement_resolution_complete"] for r in recipes)
            counts['ingredient_source_issues'] = sum(bool(r.get('ingredient_source_issues')) for r in recipes)
        report["pending_recipe_counts"] = counts
        for key, count in counts.items():
            if count:
                blockers.append(f"{key}: {count} recipes")

        if recipe_review_folder is not None:
            review_folder = Path(recipe_review_folder)
            review_manifest = read_json(review_folder / 'manifest.json')
            for name, expected in review_manifest['output_sha256'].items():
                if Path(name).name != name or hashlib.sha256((review_folder / name).read_bytes()).hexdigest() != expected:
                    raise ValueError(f'Recipe review snapshot changed: {name}')
            reviewed = read_json(review_folder / 'recipes.reviewed.json')
            originals = {r['id']: r for r in recipes}
            if len(reviewed) != len(originals) or {r['id'] for r in reviewed} != set(originals):
                raise ValueError('Step 4 review must cover the exact full corpus')
            for record in reviewed:
                original = originals[record['id']]
                if [line['original_line'] for line in record['lines']] != [a['original_line'] for a in original['ingredients']]:
                    raise ValueError('Original ingredient lines changed in Step 4')
                if record.get('prior_owner_role_review') != original.get('ingredient_role_review'):
                    raise ValueError('Step 4 changed an existing owner review')
                if [line['requirement'] for line in record['lines']] != [a['requirement_resolution'].get('requirement') for a in original['ingredients']]:
                    raise ValueError('Step 4 changed normalized requirement logic')
            report['step4_recipe_review'] = read_json(review_folder / 'report.json')
            report['step4_recipe_review']['snapshot_directory'] = str(review_folder)
            # AI proposals provide useful review coverage, not human judgments or source verification.
            blockers.append('Step 4 AI recipe proposals require human scope/completeness and role adjudication')

        required = ["recipes.training.json", "aliases.json", "queries.review.json", "relevance.review.csv"]
        missing = [name for name in required if not (folder / name).is_file()]
        report["missing_supervised_training_files"] = missing
        if missing:
            blockers.append("Reviewed supervised training files are not yet prepared")
        else:
            training_recipes = read_json(folder / "recipes.training.json")
            if {r["id"] for r in training_recipes} != {r["id"] for r in recipes}:
                raise ValueError("Training export does not cover the full corpus; audit exclusions explicitly before changing scope")
            # Pure data validation; does not import or invoke LightGBM.
            groups = training_groups(training_recipes, read_json(folder / "queries.review.json"),
                                     folder / "relevance.review.csv", read_json(folder / "aliases.json"))
            report["validated_query_groups"] = {key: len(value) for key, value in groups.items()}
    except (OSError, ValueError, KeyError, TypeError, csv.Error) as error:
        blockers.append(f"Data validation: {error}")

    versions = {}
    for package in ("lightgbm", "numpy", "scikit-learn"):
        try:
            versions[package] = metadata.version(package)
        except metadata.PackageNotFoundError:
            versions[package] = None
            blockers.append(f"Training dependency not installed: {package}")
    report["installed_training_packages"] = versions
    report["data_and_dependency_checks_passed"] = not blockers
    report["blockers"] = blockers
    report["note"] = "Passing preflight validates inputs, not model quality or package API compatibility. It does not start training."
    return report


def print_preflight(folder, recipe_review_folder=None):
    report = check_preparation(folder, recipe_review_folder)
    print(json.dumps(report, indent=2))
    return 0 if report["data_and_dependency_checks_passed"] else 1
