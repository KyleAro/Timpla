"""Audit source files and build a separate conservative YOLO detection dataset."""
import argparse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil

from PIL import Image, ImageDraw, ImageOps

PROJECT = Path(__file__).resolve().parents[1]
BAD_SOURCE_CLASSES = {30, 35}  # Source README explicitly documents incorrect annotations.
EXTENSIONS = {'.jpg', '.jpeg', '.png'}
MANUAL_FILE = PROJECT / 'datasets' / 'fruits_vegetables' / 'manual-exclusions.json'
MANUAL_EXCLUSIONS = json.loads(MANUAL_FILE.read_text()) if MANUAL_FILE.exists() else {}

def inspect(pair):
    split, image, label, names = pair
    record = {'split': split, 'image': str(image), 'label': str(label), 'reasons': [], 'boxes': [], 'rounding_fixes': 0}
    manual_reason = MANUAL_EXCLUSIONS.get(f'{split}/{image.name}')
    if manual_reason:
        record['reasons'].append(manual_reason)
    try:
        with Image.open(image) as picture:
            picture.load()
            if picture.format not in {'JPEG', 'PNG'} or min(picture.size) <= 0:
                raise ValueError('Unsupported image')
            record['width'], record['height'] = picture.size
            pixels = picture.convert('RGB')
            record['pixel_sha256'] = hashlib.sha256(str(pixels.size).encode() + pixels.tobytes()).hexdigest()
            thumb = ImageOps.grayscale(pixels).resize((8, 8))
            values = list(thumb.getdata())
            average = sum(values) / 64
            record['average_hash'] = sum((value >= average) << i for i, value in enumerate(values))
    except Exception:
        record['reasons'].append('unreadable_image')
        return record
    if not label.exists():
        record['reasons'].append('missing_label')
        return record
    try:
        lines = label.read_text(encoding='utf-8-sig').splitlines()
    except (OSError, UnicodeError):
        record['reasons'].append('unreadable_label')
        return record
    seen = set()
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            tokens = line.split()
            if len(tokens) != 5 or not re.fullmatch(r'\d+', tokens[0]):
                raise ValueError('not_detection_box')
            cls = int(tokens[0])
            x, y, w, h = map(float, tokens[1:])
            if cls not in names:
                raise ValueError('unknown_class')
            if not all(math.isfinite(v) for v in (x, y, w, h)) or w <= 0 or h <= 0:
                raise ValueError('invalid_box')
            left, top, right, bottom = x - w / 2, y - h / 2, x + w / 2, y + h / 2
            if min(left, top) < -0.00002 or max(right, bottom) > 1.00002:
                raise ValueError('box_outside_image')
            if min(left, top) < 0 or max(right, bottom) > 1:
                left, top, right, bottom = max(0, left), max(0, top), min(1, right), min(1, bottom)
                x, y, w, h = (left + right) / 2, (top + bottom) / 2, right - left, bottom - top
                record['rounding_fixes'] += 1
            if cls in BAD_SOURCE_CLASSES:
                record['reasons'].append('source_documented_wrong_class')
            box = (cls, x, y, w, h)
            if box not in seen:
                record['boxes'].append(box)
                seen.add(box)
        except (ValueError, OverflowError) as error:
            record['reasons'].append(f'{error}:line_{number}')
    if not record['boxes']:
        # Empty source labels may be valid backgrounds, but require human approval.
        record['reasons'].append('empty_label_needs_review')
    record['reasons'] = sorted(set(record['reasons']))
    return record

def copy_image(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    # Avoid duplicate 1.4 GB storage on NTFS; ZIP export still contains actual files.
    if not target.exists():
        try:
            os.link(source, target)
        except OSError:
            shutil.copy2(source, target)

def contact_sheet(records, names, target):
    picked = []
    seen = set()
    for record in sorted(records, key=lambda r: (r['split'] != 'val', r['image'])):
        classes = {box[0] for box in record['boxes']}
        if classes - seen or len(picked) < 4:
            picked.append(record)
            seen.update(classes)
        if len(picked) == 16:
            break
    sheet = Image.new('RGB', (1440, 1120), 'white')
    draw = ImageDraw.Draw(sheet)
    for index, record in enumerate(picked):
        with Image.open(record['image']) as picture:
            preview = picture.convert('RGB')
            overlay = ImageDraw.Draw(preview)
            width, height = picture.size
            for cls, x, y, w, h in record['boxes']:
                bounds = ((x - w / 2) * width, (y - h / 2) * height, (x + w / 2) * width, (y + h / 2) * height)
                overlay.rectangle(bounds, outline='red', width=max(2, width // 250))
                overlay.text((max(0, bounds[0]), max(0, bounds[1])), names[cls].split('/')[0], fill='white', stroke_fill='black', stroke_width=2)
            preview.thumbnail((352, 240))
            x0, y0 = (index % 4) * 360, (index // 4) * 280
            sheet.paste(preview, (x0 + (352 - preview.width) // 2, y0))
            caption = f"{record['split']} | {Path(record['image']).name[:36]}"
            draw.text((x0 + 4, y0 + 244), caption, fill='black')
    target.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(target)
    return [dict(image=r['image'], split=r['split'], classes=sorted({names[b[0]] for b in r['boxes']})) for r in picked]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=PROJECT / 'datasets' / 'fruits_vegetables')
    args = parser.parse_args()
    root = args.root.resolve()
    raw = root / 'raw'
    prepared = root / 'prepared'
    if (prepared / 'data.yaml').exists():
        raise SystemExit('Prepared output already exists. Use a new output directory or review it before replacing it.')
    source_yaml = (root / 'source-data.yaml').read_text()
    names = {int(key): value.strip() for key, value in re.findall(r'^\s+(\d+):\s*(.+)$', source_yaml, re.M)}
    if set(names) != set(range(63)) or names[30] != 'Strawberry' or names[35] != 'Tomato':
        raise ValueError('Source class map differs from the reviewed dataset. Stop for review.')
    jobs = []
    orphan_labels = []
    ignored_metadata = 0
    for split in ['train', 'val', 'test']:
        candidates = list((raw / 'images' / split).iterdir())
        ignored_metadata += sum(p.name.startswith('._') or p.name == '.DS_Store' for p in candidates)
        images = sorted(p for p in candidates if p.suffix.lower() in EXTENSIONS and not p.name.startswith('._'))
        stems = [p.stem for p in images]
        if len(stems) != len(set(stems)):
            raise ValueError(f'Duplicate image stems in {split}')
        for image in images:
            jobs.append((split, image, raw / 'labels' / split / (image.stem + '.txt'), names))
        image_stems = set(stems)
        orphan_labels.extend(str(p) for p in (raw / 'labels' / split).glob('*.txt') if p.stem not in image_stems and not p.name.startswith('._'))
    print(f'Checking {len(jobs)} images and annotation files...', flush=True)
    fingerprint = hashlib.sha256(''.join(f'{split}:{image.name}:{image.stat().st_size}:{image.stat().st_mtime_ns}:{label.stat().st_size if label.exists() else -1}:{label.stat().st_mtime_ns if label.exists() else -1}' for split, image, label, _ in jobs).encode()).hexdigest()
    cache_file = raw / 'inspection-cache.json'
    cached = json.loads(cache_file.read_text()) if cache_file.exists() else {}
    if cached.get('fingerprint') == fingerprint:
        records = cached['records']
        print('Using unchanged-file inspection cache', flush=True)
    else:
        with ThreadPoolExecutor(max_workers=8) as pool:
            records = []
            for count, record in enumerate(pool.map(inspect, jobs), 1):
                records.append(record)
                if count % 1000 == 0:
                    print(f'Inspected {count}/{len(jobs)} image-label pairs', flush=True)
        cache_file.write_text(json.dumps({'fingerprint': fingerprint, 'records': records}))
    # Keep exact copies together: prioritize held-out test, then val, then train.
    by_hash = defaultdict(list)
    for r in records:
        if 'pixel_sha256' in r:
            by_hash[r['pixel_sha256']].append(r)
    duplicates = []
    priority = {'test': 0, 'val': 1, 'train': 2}
    for group in by_hash.values():
        if len(group) <= 1:
            continue
        signatures = {tuple(sorted(tuple(b) for b in r['boxes'])) for r in group}
        if len(signatures) != 1:
            for r in group:
                r['reasons'].append('duplicate_image_conflicting_annotations')
        else:
            # Never retain a duplicate if its retained copy already has a label issue.
            ordered = sorted(group, key=lambda r: (priority[r['split']], r['image']))
            for r in ordered[1:]:
                r['reasons'].append('duplicate_image')
        duplicates.append([r['image'] for r in group])
    # Similar thumbnails are review candidates, not automatically deleted.
    similar = defaultdict(list)
    for r in records:
        if not r['reasons']:
            similar[r['average_hash']].append(r)
    near_groups = [[r['image'] for r in group] for group in similar.values() if len({r['split'] for r in group}) > 1]
    class_map = {old: new for new, old in enumerate(k for k in names if k not in BAD_SOURCE_CLASSES)}
    new_names = {class_map[old]: name for old, name in names.items() if old in class_map}
    counts = {split: Counter() for split in ['train', 'val', 'test']}
    retained = []
    excluded = []
    for r in records:
        if r['reasons']:
            excluded.append({'split': r['split'], 'image': r['image'], 'reasons': sorted(set(r['reasons']))})
            continue
        retained.append(r)
        target = prepared / 'images' / r['split'] / Path(r['image']).name
        copy_image(Path(r['image']), target)
        label = prepared / 'labels' / r['split'] / (target.stem + '.txt')
        label.parent.mkdir(parents=True, exist_ok=True)
        content = '\n'.join(f'{class_map[b[0]]} ' + ' '.join(f'{v:.10f}' for v in b[1:]) for b in r['boxes']) + '\n'
        if not label.exists() or label.read_text() != content:
            label.write_text(content)
        counts[r['split']].update(class_map[b[0]] for b in r['boxes'])
    if not all(any(r['split'] == split for r in retained) for split in ['train', 'val', 'test']):
        raise ValueError('An output split is empty; stop before writing a training config.')
    # No absolute machine paths: this dataset works after extraction in Colab.
    text = 'train: images/train\nval: images/val\ntest: images/test\nnames:\n'
    text += ''.join(f'  {idx}: {json.dumps(name)}\n' for idx, name in new_names.items())
    (prepared / 'data.yaml').write_text(text)
    report_dir = PROJECT / 'datasets' / 'reports'
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / 'produce-quarantine.json').write_text(json.dumps(excluded, indent=2) + '\n')
    (report_dir / 'produce-duplicates.json').write_text(json.dumps({'exact': duplicates, 'cross_split_similar_thumbnail_candidates': near_groups}, indent=2) + '\n')
    (root / 'class-remap.json').write_text(json.dumps({old: {'new_id': new, 'name': names[old]} for old, new in class_map.items()}, indent=2) + '\n')
    with (report_dir / 'produce-class-counts.csv').open('w', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(['id', 'class', 'train_boxes', 'val_boxes', 'test_boxes'])
        for idx, name in new_names.items():
            writer.writerow([idx, name, *(counts[split][idx] for split in ['train', 'val', 'test'])])
    preview = report_dir / 'previews' / 'produce-boxes.jpg'
    picked = contact_sheet(retained, names, preview)
    (report_dir / 'produce-preview-index.json').write_text(json.dumps(picked, indent=2) + '\n')
    summary = {
        'status': 'structurally_checked_not_fully_ground_truth_verified',
        'raw_images': dict(Counter(r['split'] for r in records)),
        'prepared_images': dict(Counter(r['split'] for r in retained)),
        'excluded_images': len(excluded), 'output_classes': len(new_names),
        'removed_source_class_ids': sorted(BAD_SOURCE_CLASSES),
        'exclusion_reasons': dict(Counter(reason.split(':')[0] for r in excluded for reason in r['reasons'])),
        'rounding_only_box_clamps': sum(r['rounding_fixes'] for r in retained),
        'orphan_labels': len(orphan_labels),
        'ignored_macos_metadata_files': ignored_metadata,
        'exact_duplicate_groups': len(duplicates),
        'cross_split_similar_thumbnail_groups_for_review': len(near_groups),
        'classes_absent_from_training': [new_names[k] for k in new_names if counts['train'][k] == 0],
        'classes_with_fewer_than_20_training_boxes': [new_names[k] for k in new_names if counts['train'][k] < 20],
        'label_accuracy': 'Sample review only. Exhaustive manual annotation verification is still required.',
        'prepared_config': str(prepared / 'data.yaml'),
    }
    (report_dir / 'produce-summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2), flush=True)

if __name__ == '__main__':
    main()
