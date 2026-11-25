"""Audit a YOLO detection export without changing images, labels or splits."""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import yaml
from PIL import Image


def audit(data):
    cfg = yaml.safe_load(data.read_text(encoding='utf-8'))
    names = cfg['names']
    if isinstance(names, dict):
        if sorted(names) != list(range(len(names))):
            raise ValueError('Class IDs must be contiguous integers starting at zero')
        names = [names[i] for i in range(len(names))]
    if not isinstance(names, list) or not names or len(set(names)) != len(names):
        raise ValueError('Expected unique class names')
    root = Path(cfg.get('path', '.'))
    root = root if root.is_absolute() else data.parent / root
    report = {'data': str(data), 'classes': names, 'splits': {}, 'errors': [], 'warnings': []}
    hashes = {}
    fingerprints = []
    for split in ('train', 'val', 'test'):
        objects, images = Counter(), Counter()
        entry = cfg.get(split)
        if not entry:
            report['errors'].append(f'Missing {split} split')
            continue
        files = []
        for value in entry if isinstance(entry, list) else [entry]:
            path = Path(value)
            path = path if path.is_absolute() else root / path
            if not path.is_dir():
                report['errors'].append(f'{split}: expected image directory: {path}')
                continue
            files.extend(p for p in path.rglob('*') if p.suffix.lower() in ('.jpg', '.jpeg', '.png', '.webp', '.bmp'))
        negatives = 0
        for image in sorted(set(files)):
            try:
                with Image.open(image) as decoded:
                    decoded.verify()
            except Exception as error:
                report['errors'].append(f'Unreadable image: {image}: {error}')
                continue
            digest = hashlib.sha256(image.read_bytes()).hexdigest()
            if digest in hashes:
                old_split, old_image = hashes[digest]
                key = 'errors' if old_split != split else 'warnings'
                report[key].append(f'Duplicate: {old_image} and {image}')
            else:
                hashes[digest] = (split, str(image))
            parts = list(image.parts)
            if 'images' not in parts:
                report['errors'].append(f'No images path segment: {image}')
                continue
            parts[len(parts) - 1 - parts[::-1].index('images')] = 'labels'
            label = Path(*parts).with_suffix('.txt')
            if not label.is_file():
                report['errors'].append(f'Missing annotation: {label}')
                continue
            rows = label.read_text(encoding='utf-8').splitlines()
            fingerprints.append((split, digest, hashlib.sha256(label.read_bytes()).hexdigest()))
            seen = set()
            if not any(row.strip() for row in rows):
                negatives += 1
            for number, row in enumerate(rows, 1):
                if not row.strip():
                    continue
                try:
                    values = [float(v) for v in row.split()]
                    if len(values) != 5 or not all(math.isfinite(v) for v in values):
                        raise ValueError('expected class x y width height')
                    cls, x, y, w, h = values
                    if cls != int(cls) or not 0 <= cls < len(names):
                        raise ValueError('invalid class ID')
                    if not (0 < w <= 1 and 0 < h <= 1 and 0 <= x-w/2 and x+w/2 <= 1.00001 and 0 <= y-h/2 and y+h/2 <= 1.00001):
                        raise ValueError('box outside image or nonpositive size')
                    objects[names[int(cls)]] += 1
                    seen.add(names[int(cls)])
                except ValueError as error:
                    report['errors'].append(f'{label}:{number}: {error}')
            images.update(seen)
        for name in names:
            if not objects[name]:
                report['errors'].append(f'{split}: no objects for {name}')
        report['splits'][split] = {'images': len(set(files)), 'negative_images': negatives,
                                   'objects_by_class': dict(objects), 'images_by_class': dict(images)}
    report['warnings'].append('Exact hashes do not detect near-duplicates or related photo sessions. Review grouping and labels visually.')
    report['passed'] = not report['errors']
    report['annotated_dataset_sha256'] = hashlib.sha256(json.dumps(sorted(fingerprints)).encode()).hexdigest()
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.data.resolve())
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(f"Audit passed: {result['passed']}; errors: {len(result['errors'])}; report: {args.report}")
    raise SystemExit(0 if result['passed'] else 1)
