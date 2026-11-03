"""Validate full-corpus Step 4 AI reviews and export human review worksheets."""
import argparse
from collections import Counter
from copy import deepcopy
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from prepare_full_dataset import read, write_json
from prepare_recipe_review import ROOT, ROLES, food_nodes

SCOPES = {'proposed_in_scope', 'proposed_out_of_scope', 'needs_review'}
COMPLETENESS = {'no_obvious_gap', 'gap_identified', 'needs_review'}
ISSUES = {'missing_ingredient', 'subrecipe_dependency', 'terminology', 'state_or_quantity', 'other'}
POLICY = {
    'version': 1,
    'status': 'proposed_for_project_review',
    'identity_matching': 'Exact canonical IDs after explicit approved alias alignment.',
    'all_of': 'All required branches must be met; role availability and quantities are checked separately.',
    'any_of': 'At least one explicitly offered branch; never require every alternative.',
    'generic_cut_compatibility': 'A generic meat detection does not establish every specific cut.',
    'preparation_state_compatibility': 'No automatic raw-to-cooked or whole-to-boneless equivalence. Source-supported preparation operations need explicit review.',
    'substitutions': 'Only source-explicit choices are represented. Other substitutions require separate approval.',
    'supporting_availability': 'Disclose and confirm. Missing supporting items prevent a claim that the recipe is cookable without purchases.',
    'derived_ingredients': 'Retained cooking liquids and prepared subrecipes need reviewed dependency links; they are not automatically separate purchases.',
    'quantities': 'Original amounts retained. No assertion that inventory quantities suffice.',
    'excluded_ingredients': 'Exclusions apply across all ingredient roles, including optional ingredients; no verified allergy ontology is implied.',
}


def validate_decision(draft, decision):
    if decision.get('annotation_type') != 'ai_recipe_semantic_review' or not decision.get('reviewer'):
        raise ValueError('Explicit AI recipe-review provenance required')
    scope = decision.get('cuisine_scope', {})
    complete = decision.get('internal_completeness', {})
    if scope.get('decision') not in SCOPES or not str(scope.get('basis', '')).strip():
        raise ValueError('Recipe scope needs a permitted decision and actual basis')
    if complete.get('status') not in COMPLETENESS or not str(complete.get('basis', '')).strip():
        raise ValueError('Internal completeness needs a permitted decision and actual basis')
    issues = complete.get('issues', [])
    if not isinstance(issues, list):
        raise ValueError('Completeness issues must be a list')
    if complete['status'] == 'gap_identified' and not issues:
        raise ValueError('A claimed gap needs specific evidence')
    for issue in issues:
        if (not isinstance(issue, dict) or issue.get('kind') not in ISSUES or
                not str(issue.get('item', '')).strip() or not str(issue.get('evidence', '')).strip()):
            raise ValueError('Completeness issue needs item, kind and evidence')
    seen = set()
    for override in decision.get('role_overrides', []):
        number = override.get('line_number')
        identity = override.get('ingredient_id')
        if isinstance(number, bool) or not isinstance(number, int) or not 1 <= number <= len(draft['lines']):
            raise ValueError('Role override refers to an unknown line')
        matches = [r for r in draft['lines'][number - 1]['roles'] if r['ingredient_id'] == identity]
        if not matches or override.get('role') not in ROLES or not str(override.get('basis', '')).strip():
            raise ValueError('Role override must refer to an existing food leaf with a valid role and reason')
        key = number, identity
        if key in seen:
            raise ValueError('Duplicate role override')
        seen.add(key)
        if draft.get('prior_owner_role_review') and any(r['proposed_role'] != override['role'] for r in matches):
            raise ValueError('AI review cannot overwrite owner-approved roles')
    for key in ('dependency_notes', 'notes'):
        if not isinstance(decision.get(key, []), list) or any(not isinstance(s, str) for s in decision.get(key, [])):
            raise ValueError(f'{key} must be a list of strings')


def merge(drafts, partitions, decisions):
    expected_all = {r['id']: r for r in drafts}
    if not drafts or len(expected_all) != len(drafts):
        raise ValueError('Nonempty full corpus with unique recipe IDs required')
    annotations = {}
    for batch, judgments in zip(partitions, decisions, strict=True):
        expected = {r['id']: r for r in batch}
        actual = {r['recipe_id']: r for r in judgments}
        if len(expected) != len(batch) or len(actual) != len(judgments) or set(expected) != set(actual):
            raise ValueError('Every assigned recipe must be reviewed exactly once')
        if set(expected) & set(annotations):
            raise ValueError('Review partitions overlap')
        for rid, source in expected.items():
            if source != expected_all.get(rid):
                raise ValueError('Partition differs from the frozen draft')
            validate_decision(source, actual[rid])
        annotations.update(actual)
    if set(annotations) != set(expected_all):
        raise ValueError('Review must cover the entire corpus')
    result = []
    for draft in drafts:
        record = deepcopy(draft)
        decision = annotations[draft['id']]
        overrides = {(r['line_number'], r['ingredient_id']): r for r in decision.get('role_overrides', [])}
        for line in record['lines']:
            for role in line['roles']:
                replacement = overrides.get((line['line_number'], role['ingredient_id']))
                if replacement:
                    role['before_semantic_review'] = {'proposed_role': role['proposed_role'], 'basis': role['basis']}
                    role['proposed_role'] = replacement['role']
                    role['basis'] = replacement['basis']
            # Revalidate exact node coverage. Roles do not change the logical expression.
            expected_leaves = [(path, identity) for path, identity in food_nodes(line['requirement'])]
            if [(r['path'], r['ingredient_id']) for r in line['roles']] != expected_leaves:
                raise ValueError('Role annotations no longer match the requirement tree')
        record['cuisine_scope'] = deepcopy(decision['cuisine_scope'])
        record['internal_completeness'] = deepcopy(decision['internal_completeness'])
        record['semantic_review'] = deepcopy(decision)
        record['role_annotation_status'] = 'owner_approved_preserved' if record.get('prior_owner_role_review') else 'ai_semantic_review_pending_human_adjudication'
        record['human_review_status'] = draft['human_review_status']
        record['ready_for_training'] = False
        result.append(record)
    return result


def csv_file(path, fields, rows):
    with path.open('x', newline='', encoding='utf-8-sig') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def export(folder, records):
    roles, overview, issues = [], [], []
    for recipe in records:
        rid = recipe['id']
        by_role = {r: set() for r in ROLES}
        for line in recipe['lines']:
            for role in line['roles']:
                by_role[role['proposed_role']].add(role['ingredient_id'])
                roles.append({'recipe_id': rid, 'recipe_name': recipe['name'], 'line_number': line['line_number'],
                              'ingredient_line': line['original_line'], 'leaf_path': json.dumps(role['path']),
                              'ingredient_id': role['ingredient_id'], 'proposed_role': role['proposed_role'],
                              'basis': role['basis'], 'requirement_json': json.dumps(line['requirement']),
                              'owner_role_approval_preserved': bool(recipe.get('prior_owner_role_review')),
                              'approved_role': '', 'decision': '', 'reviewer': '', 'reviewed_at': '', 'notes': ''})
        conflicts = sorted(set.union(*by_role.values()) - {value for value in set.union(*by_role.values())
                           if sum(value in group for group in by_role.values()) == 1})
        complete = recipe['internal_completeness']
        scope = recipe['cuisine_scope']
        priority = 'high' if complete['status'] == 'gap_identified' or conflicts or not by_role['essential'] else (
            'medium' if complete['status'] == 'needs_review' or scope['decision'] != 'proposed_in_scope' or recipe['quality_flags'] else 'normal')
        overview.append({'recipe_id': rid, 'recipe_name': recipe['name'], 'review_priority': priority,
                         'proposed_cuisine_scope': scope['decision'], 'scope_basis': scope['basis'],
                         'internal_completeness': complete['status'], 'completeness_basis': complete['basis'],
                         'source_comparison_status': 'existing_record_preserved' if recipe['preserved_source_check'] else 'pending',
                         'source_urls': ' | '.join(recipe['source_urls']),
                         'essential_leaf_ids_display_only': ';'.join(sorted(by_role['essential'])),
                         'supporting_leaf_ids_display_only': ';'.join(sorted(by_role['supporting'])),
                         'optional_leaf_ids_display_only': ';'.join(sorted(by_role['optional'])),
                         'cross_line_role_conflicts': ';'.join(conflicts),
                         'dependency_notes': ' | '.join(recipe['semantic_review'].get('dependency_notes', [])),
                         'quality_flags': ';'.join(recipe['quality_flags']),
                         'approved_scope': '', 'approved_completeness': '', 'decision': '', 'reviewer': '', 'reviewed_at': '', 'notes': ''})
        for issue in complete.get('issues', []):
            issues.append(dict(recipe_id=rid, recipe_name=recipe['name'], **{key: issue[key] for key in ('item','evidence','kind')}))
    write_json(folder/'recipes.reviewed.json', records)
    write_json(folder/'compatibility_policy.review.json', POLICY)
    csv_file(folder/'recipe_review.csv', list(overview[0]), overview)
    csv_file(folder/'ingredient_roles.review.csv', list(roles[0]), roles)
    csv_file(folder/'source_issues.review.csv', ['recipe_id','recipe_name','item','evidence','kind'], issues)
    counts = Counter(r['internal_completeness']['status'] for r in records)
    scope_counts = Counter(r['cuisine_scope']['decision'] for r in records)
    report = {'recipes': len(records), 'ai_review_coverage_percent': 100.0,
              'original_source_rows_preserved': sum(len(r['original_source_rows']) for r in records),
              'ingredient_line_occurrences': sum(len(r['lines']) for r in records),
              'food_requirement_leaf_role_rows': len(roles),
              'proposed_role_counts': dict(Counter(r['proposed_role'] for r in roles)),
              'internal_completeness_counts': dict(counts), 'proposed_cuisine_scope_counts': dict(scope_counts),
              'identified_issue_rows': len(issues),
              'review_priority_counts': dict(Counter(r['review_priority'] for r in overview)),
              'cross_line_role_conflict_recipes': sum(bool(r['cross_line_role_conflicts']) for r in overview),
              'owner_role_reviews_preserved': sum(bool(r['prior_owner_role_review']) for r in records),
              'original_source_comparisons_preserved': sum(bool(r['preserved_source_check']) for r in records),
              'new_human_approvals': 0, 'new_external_source_checks': 0,
              'human_recipe_adjudications_pending': len(records),
              'recipe_records_deleted': 0, 'ready_for_training': False, 'model_training_performed': False,
              'note': 'Full-corpus AI-assisted proposals with internal consistency review. Human recipe-level scope/completeness adjudication is pending; source comparisons are not fabricated. Flat role-ID lists are display only; use the retained requirement trees for logic.'}
    write_json(folder/'report.json', report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--review', type=Path, default=ROOT/'data/recipe_review/v1')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit('Use an unused snapshot folder; never overwrite reviewer work')
    manifest = read(args.review/'manifest.json')
    for name, expected in manifest['input_sha256'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest() != expected:
            raise ValueError(f'Frozen original input changed: {name}')
    for name, expected in manifest['output_sha256'].items():
        if hashlib.sha256((args.review/name).read_bytes()).hexdigest() != expected:
            raise ValueError(f'Frozen review draft changed: {name}')
    inputs = [args.review/'manifest.json', args.review/'recipes.draft.json', args.review/'REVIEW_POLICY.md']
    partitions, judgments = [], []
    for i in range(1,4):
        source, decision = [args.review/f'partition_{i:02d}{suffix}.json' for suffix in ('', '.decisions')]
        inputs.extend([source,decision])
        partitions.append(read(source))
        judgments.append(read(decision))
    records = merge(read(args.review/'recipes.draft.json'), partitions, judgments)
    args.output.mkdir(parents=True)
    report = export(args.output, records)
    write_json(args.output/'manifest.json', {'created_at': datetime.now(timezone.utc).isoformat(),
               'input_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
               'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               'output_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in args.output.iterdir() if p.is_file()},
               'model_training_performed': False})
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
