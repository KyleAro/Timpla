"""Apply recorded human-review exclusions to an existing prepared snapshot."""
import csv
import json
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
root = PROJECT / 'datasets' / 'fruits_vegetables'
reports = PROJECT / 'datasets' / 'reports'

def main():
    exclusions = json.loads((root / 'manual-exclusions.json').read_text())
    summary = json.loads((reports / 'produce-summary.json').read_text())
    quarantine = json.loads((reports / 'produce-quarantine.json').read_text())
    with (reports / 'produce-class-counts.csv').open(newline='') as stream:
        rows = list(csv.DictReader(stream))
    removed = 0
    for key, reason in exclusions.items():
        split, filename = key.split('/')
        image = (root / 'prepared' / 'images' / split / filename).resolve()
        label = (root / 'prepared' / 'labels' / split / (Path(filename).stem + '.txt')).resolve()
        assert (root / 'prepared').resolve() in image.parents
        assert (root / 'prepared').resolve() in label.parents
        if not image.exists():
            continue
        for line in label.read_text().splitlines():
            class_id = int(line.split()[0])
            row = next(r for r in rows if int(r['id']) == class_id)
            row[f'{split}_boxes'] = str(int(row[f'{split}_boxes']) - 1)
        image.unlink()
        label.unlink()
        quarantine.append({'split': split, 'image': str(root / 'raw' / 'images' / split / filename), 'reasons': [reason]})
        summary['prepared_images'][split] -= 1
        summary['excluded_images'] += 1
        summary['exclusion_reasons'][reason] = summary['exclusion_reasons'].get(reason, 0) + 1
        removed += 1
    summary['manual_review_exclusions'] = len(exclusions)
    summary['label_accuracy'] = 'Visual sample review found incomplete annotations and a nonculinary fungus example; recorded examples were quarantined. Remaining labels are not exhaustively verified.'
    with (reports / 'produce-class-counts.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (reports / 'produce-summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    (reports / 'produce-quarantine.json').write_text(json.dumps(quarantine, indent=2) + '\n')
    print(f'Applied {removed} additional recorded manual exclusions.', flush=True)

if __name__ == '__main__':
    main()
