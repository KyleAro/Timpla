"""Fetch checksum-verified LVIS produce archives. Never execute source code."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
from pathlib import Path
import shutil
import urllib.request
from zipfile import ZipFile
from dataset_io import file_sha256

REPO = 'https://media.githubusercontent.com/media/henningheyen/Fruits-And-Vegetables-Detection-Dataset/main/'
DATA = 'LVIS_Fruits_And_Vegetables'
PROJECT = Path(__file__).resolve().parents[1]

def fetch(source: Path, destination: Path, kind: str, split: str):
    relative = f'{DATA}/{kind}/{split}/{split}.zip'
    pointer = (source / relative).read_text()
    expected_hash = next(line.split(':', 1)[1] for line in pointer.splitlines() if line.startswith('oid sha256:'))
    expected_size = int(next(line.split()[1] for line in pointer.splitlines() if line.startswith('size ')))
    archive = destination / 'archives' / f'{kind}-{split}.zip'
    archive.parent.mkdir(parents=True, exist_ok=True)
    if archive.exists():
        if archive.stat().st_size != expected_size or file_sha256(archive) != expected_hash:
            raise ValueError(f'Existing archive checksum mismatch: {archive}')
    else:
        partial = archive.with_suffix('.zip.part')
        digest = hashlib.sha256()
        read = 0
        last_notice = 0
        request = urllib.request.Request(REPO + relative, headers={'User-Agent': 'Timpla-dataset-preparation'})
        with urllib.request.urlopen(request, timeout=90) as response, partial.open('wb') as output:
            while block := response.read(1024 * 1024):
                output.write(block)
                digest.update(block)
                read += len(block)
                if read - last_notice >= 50_000_000:
                    print(f'{kind}/{split}: {read / expected_size:.0%}', flush=True)
                    last_notice = read
        if read != expected_size or digest.hexdigest() != expected_hash:
            raise ValueError(f'Download verification failed for {relative}')
        partial.replace(archive)
    with ZipFile(archive) as zipped:
        bad = zipped.testzip()
        if bad:
            raise ValueError(f'Corrupt archive member: {bad}')
        out = destination / 'raw' / kind / split
        out.mkdir(parents=True, exist_ok=True)
        count = 0
        for entry in zipped.infolist():
            if entry.is_dir():
                continue
            name = Path(entry.filename).name
            if '__MACOSX' in Path(entry.filename).parts or name.startswith('._') or name == '.DS_Store':
                continue
            if Path(name).suffix.lower() not in ({'.jpg', '.jpeg', '.png'} if kind == 'images' else {'.txt'}):
                raise ValueError(f'Unexpected archive member: {entry.filename}')
            target = out / name
            if target.exists():
                with zipped.open(entry) as stream:
                    if target.read_bytes() != stream.read():
                        raise ValueError(f'Duplicate output filename: {name}')
            else:
                with zipped.open(entry) as stream, target.open('wb') as output:
                    shutil.copyfileobj(stream, output)
            count += 1
        print(f'Verified and extracted {kind}/{split}: {count} files', flush=True)
    return {'kind': kind, 'split': split, 'sha256': expected_hash, 'bytes': expected_size, 'files': count, 'url': REPO + relative}

def main():
    import json
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True, help='Extracted original GitHub repository')
    args = parser.parse_args()
    destination = PROJECT / 'datasets' / 'fruits_vegetables'
    destination.mkdir(parents=True, exist_ok=True)
    for name in ['README.md', 'LICENSE', 'fruits_vegetables_LVIS_dict.json']:
        shutil.copy2(args.source / name, destination / ('SOURCE_' + name))
    shutil.copy2(args.source / DATA / 'data.yaml', destination / 'source-data.yaml')
    for kind in ['images', 'labels']:
        shutil.copytree(args.source / DATA / kind / 'test', destination / 'raw' / kind / 'test', dirs_exist_ok=True)
    with ThreadPoolExecutor(max_workers=4) as pool:
        jobs = [pool.submit(fetch, args.source, destination, kind, split) for kind in ['images', 'labels'] for split in ['train', 'val']]
        records = [job.result() for job in jobs]
    (destination / 'downloads.json').write_text(json.dumps(records, indent=2) + '\n')

if __name__ == '__main__':
    main()
