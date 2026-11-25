"""Preserve and audit a downloaded YOLO ZIP; never silently change its labels."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import stat
import zipfile
import yaml
from audit_dataset import audit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--zip', type=Path, required=True, dest='archive')
    parser.add_argument('--name', required=True, help='Unique source/version identifier')
    parser.add_argument('--source-url', required=True)
    args = parser.parse_args()
    if Path(args.name).name != args.name or args.name in ('.', '..'):
        parser.error('Name must be a single directory name')
    target = Path(__file__).resolve().parent / 'sources' / args.name
    if target.exists():
        parser.error('Source already exists; choose a new version name')
    with zipfile.ZipFile(args.archive) as archive:
        root = (target / 'original').resolve()
        for entry in archive.infolist():
            if not (root / entry.filename).resolve().is_relative_to(root):
                parser.error('Archive contains a path outside extraction directory')
            if stat.S_ISLNK(entry.external_attr >> 16):
                parser.error('Archive symlinks are not supported')
        target.mkdir(parents=True)
        shutil.copy2(args.archive, target / 'export.zip')
        archive.extractall(root)
    candidates = list(root.rglob('data.yaml'))
    if len(candidates) != 1:
        raise ValueError(f'Expected one data.yaml, found {len(candidates)}; review preserved export')
    original = candidates[0]
    cfg = yaml.safe_load(original.read_text(encoding='utf-8'))
    # Roboflow exports frequently contain ../train paths intended for a
    # different working directory. Resolve only verified physical directories.
    normalized = {'names': cfg['names']}
    for split, aliases in [('train', ['train']), ('val', ['valid', 'val']), ('test', ['test'])]:
        folders = [original.parent / alias / 'images' for alias in aliases]
        folders = [p for p in folders if p.is_dir()]
        if len(folders) != 1:
            raise ValueError(f'Expected one {split} image directory; inspect export layout')
        normalized[split] = folders[0].resolve().as_posix()
    data = target / 'data.local.yaml'
    data.write_text(yaml.safe_dump(normalized, sort_keys=False), encoding='utf-8')
    provenance = {'source_url': args.source_url, 'imported_utc': datetime.now(timezone.utc).isoformat(),
                  'archive_sha256': hashlib.sha256((target / 'export.zip').read_bytes()).hexdigest(),
                  'original_data_yaml': str(original), 'labels_modified': False,
                  'license_status': 'Review original export license and source image provenance',
                  'scope': 'Source audit only; visual review and merged dataset review required'}
    (target / 'provenance.json').write_text(json.dumps(provenance, indent=2), encoding='utf-8')
    report = audit(data)
    (target / 'audit.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({'source': str(target), 'audit_passed': report['passed'],
                      'classes': report['classes'], 'errors': report['errors']}, indent=2))
    raise SystemExit(0 if report['passed'] else 1)


if __name__ == '__main__':
    main()
