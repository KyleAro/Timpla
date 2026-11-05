"""Fetch and verify only the checkpoint required by a split detector service."""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen
from zipfile import is_zipfile

ROOT = Path(__file__).resolve().parents[2]
GENERAL_MANIFEST = ROOT / 'models/ingredient_detector/YOLOv8n_merged_best.manifest.json'
GENERAL_PATH = ROOT / 'models/ingredient_detector/YOLOv8n_merged_best.pt'
PRODUCE_MANIFEST = ROOT / 'models/produce/baseline-manifest.json'
PRODUCE_PATH = ROOT / 'models/produce/author-yolov8m.pt'


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def read_manifest(path: Path) -> dict:
    if not path.is_file():
        raise FileNotFoundError(f'Model manifest missing: {path}')
    with path.open(encoding='utf-8') as source:
        return json.load(source)


def verify_checkpoint(path: Path, manifest: dict) -> None:
    if not path.is_file():
        raise FileNotFoundError(f'Model checkpoint download did not create: {path}')
    if path.stat().st_size != manifest['bytes']:
        raise RuntimeError(f'Unexpected model checkpoint size: {path.name}')
    if sha256_file(path) != manifest['sha256'] or not is_zipfile(path):
        raise RuntimeError(f'Model checkpoint failed SHA-256 or PyTorch archive validation: {path.name}')
    print(f'Verified {path.name} ({path.stat().st_size:,} bytes).', flush=True)


def download_general(manifest: dict) -> None:
    if manifest.get('file') != GENERAL_PATH.name or not manifest.get('download_url'):
        raise RuntimeError('The general-model manifest does not match the configured checkpoint.')
    if GENERAL_PATH.exists():
        verify_checkpoint(GENERAL_PATH, manifest)
        return

    GENERAL_PATH.parent.mkdir(parents=True, exist_ok=True)
    partial = GENERAL_PATH.with_suffix(GENERAL_PATH.suffix + '.part')
    request = Request(manifest['download_url'], headers={'User-Agent': 'TIMPLA-model-setup'})
    digest = hashlib.sha256()
    size = 0
    try:
        with urlopen(request, timeout=120) as response, partial.open('wb') as target:
            while True:
                block = response.read(1024 * 1024)
                if not block:
                    break
                target.write(block)
                digest.update(block)
                size += len(block)
        if size != manifest['bytes'] or digest.hexdigest() != manifest['sha256'] or not is_zipfile(partial):
            raise RuntimeError('Downloaded general-model checkpoint failed validation.')
        partial.replace(GENERAL_PATH)
    finally:
        if partial.exists():
            partial.unlink()
    verify_checkpoint(GENERAL_PATH, manifest)


def download_produce(manifest: dict) -> None:
    if manifest.get('file') != PRODUCE_PATH.name:
        raise RuntimeError('The produce-model manifest does not match the configured checkpoint.')
    if not PRODUCE_PATH.exists():
        from ml.ingredient_detector.download_produce import main as download_author_checkpoint
        download_author_checkpoint()
    verify_checkpoint(PRODUCE_PATH, manifest)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--role', choices=('general', 'produce'), required=True)
    role = parser.parse_args().role
    if role == 'general':
        download_general(read_manifest(GENERAL_MANIFEST))
    else:
        download_produce(read_manifest(PRODUCE_MANIFEST))


if __name__ == '__main__':
    main()
