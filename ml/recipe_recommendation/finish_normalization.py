"""Apply conservative rules across all groups, preserving owner reviews; no training."""
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from propose_batch_mappings import propose, clean

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data/processed'


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def expand(groups, members, proposals, approved, timestamp):
    """Pure transformation, validated completely before any file is written."""
    proposals_by_line = {p['ingredient_line']: p for p in proposals}
    if len(proposals_by_line) != len(proposals):
        raise ValueError('Duplicate vocabulary lines')
    flattened = [line for lines in members.values() for line in lines]
    if len(flattened) != len(set(flattened)) or set(flattened) != set(proposals_by_line):
        raise ValueError('Membership does not cover the entire vocabulary exactly once')
    keys = [g['lookup_text'] for g in groups]
    if len(keys) != len(set(keys)) or set(keys) != set(members):
        raise ValueError('Group review and membership disagree')
    for key, lines in members.items():
        if any(proposals_by_line[line]['lookup_text'] != key for line in lines):
            raise ValueError('Stale group membership')
    updated = dict(approved)
    result = []
    exceptions = []
    accepted = 0
    trusted_roots = {}
    for row in groups:
        if row['decision'] == 'approve':
            ids = row['approved_ingredients'].split(';')
            if len(ids) == 1 and ids[0]:
                trusted_roots[clean(row['lookup_text'])] = ids[0]
    for original in groups:
        row = dict(original)
        key = row['lookup_text']
        if row['decision'].strip():
            # Preserve ALL explicit owner approvals and deferrals, including notes.
            result.append(row)
            if row['decision'] == 'defer':
                exceptions.append(dict(row, exception_reason='Existing owner deferral: ' + row['notes']))
            continue
        ids, basis = propose(key, trusted_roots)
        if not ids:
            exceptions.append(dict(row, exception_reason=basis))
            result.append(row)
            continue
        previous = {tuple(sorted(approved[line]['canonical_ingredients']))
                    for line in members[key] if line in approved}
        if previous and previous != {tuple(sorted(ids))}:
            exceptions.append(dict(row, exception_reason='Rule conflicts with an existing individual approval; owner decision preserved.'))
            result.append(row)
            continue
        for line in members[key]:
            if line not in updated:
                updated[line] = {
                    'canonical_ingredients': ids,
                    'reviewed_by': 'Codex automated rules (user-authorized takeover)',
                    'reviewed_at': timestamp, 'review_type': 'automated_rule_acceptance',
                    'notes': basis + ' Not an independent human review or substitution decision.',
                    'review_file': 'ingredient_groups.review.csv', 'lookup_group': key,
                    'rule_source': 'propose_batch_mappings.py',
                }
        row['approved_ingredients'] = ';'.join(ids)
        row['suggested_ingredients'] = ';'.join(ids)
        row['decision'] = 'approve'
        row['notes'] = 'AUTOMATED RULE ACCEPTANCE; Codex, user-authorized. ' + basis
        accepted += 1
        result.append(row)
    for line, record in approved.items():
        if updated[line] != record:
            raise AssertionError('An existing approval was modified')
    occurrences = {p['ingredient_line']: p['occurrences'] for p in proposals}
    def coverage(mapping):
        return sum(occurrences[line] for line in mapping)
    report = {
        'created_at': timestamp, 'total_groups': len(groups), 'total_distinct_lines': len(proposals),
        'total_occurrences': sum(occurrences.values()),
        'before_mapping_entries': len(approved), 'after_mapping_entries': len(updated),
        'new_automated_mapping_entries': len(updated)-len(approved), 'new_accepted_groups': accepted,
        'before_mapped_occurrences': coverage(approved), 'after_mapped_occurrences': coverage(updated),
        'after_combined_coverage_percent': round(100*coverage(updated)/sum(occurrences.values()), 2),
        'exception_groups': len(exceptions),
        'human_review_claimed_for_new_records': False, 'model_training_performed': False,
        'scope': 'Entire 8,606-group vocabulary; original text and all owner decisions retained.',
    }
    return result, updated, exceptions, report


def main():
    master = DATA / 'ingredient_groups.review.csv'
    approved_path = DATA / 'ingredient_mapping.approved.json'
    with master.open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames
        groups = list(reader)
    timestamp = datetime.now(timezone.utc)
    rows, approved, exceptions, report = expand(groups,
        read_json(DATA/'ingredient_groups.members.json'),
        read_json(DATA/'ingredient_mapping.proposed.json'), read_json(approved_path), timestamp.isoformat())
    first_report = dict(report)
    passes = 1
    while report['new_accepted_groups']:
        if passes >= 20:
            raise ValueError('Rules did not converge; no files were changed.')
        rows, approved, exceptions, report = expand(rows,
            read_json(DATA/'ingredient_groups.members.json'),
            read_json(DATA/'ingredient_mapping.proposed.json'), approved, timestamp.isoformat())
        passes += 1
    report.update({
        'before_mapping_entries': first_report['before_mapping_entries'],
        'before_mapped_occurrences': first_report['before_mapped_occurrences'],
        'new_automated_mapping_entries': report['after_mapping_entries']-first_report['before_mapping_entries'],
        'new_accepted_groups': sum(r['decision']=='approve' for r in rows)-sum(r['decision']=='approve' for r in groups),
        'passes_including_convergence_check': passes,
        'rules_converged': True,
    })
    run = ROOT / 'data/automation_runs' / timestamp.strftime('%Y%m%dT%H%M%S%fZ')
    run.mkdir(parents=True)
    for source in [master, approved_path]:
        (run / (source.name+'.before')).write_bytes(source.read_bytes())
    rule_path = ROOT / 'propose_batch_mappings.py'
    report['rule_sha256'] = hashlib.sha256(rule_path.read_bytes()).hexdigest()
    report['additional_rule_sha256'] = hashlib.sha256((ROOT/'contextual_normalization.py').read_bytes()).hexdigest()
    report['input_sha256'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in [master, approved_path, DATA/'ingredient_groups.members.json', DATA/'ingredient_mapping.proposed.json']}
    # Each replacement is atomic; recovery copies preserve the original approvals.
    temp = run / 'approved.next.json'
    temp.write_text(json.dumps(approved, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    temp.replace(approved_path)
    temp = run / 'groups.next.csv'
    with temp.open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    temp.replace(master)
    with (run/'exceptions.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields+['exception_reason'])
        writer.writeheader()
        writer.writerows(exceptions)
    (run/'report.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
    print(f'Backups, report and exceptions: {run}')


if __name__ == '__main__':
    main()
