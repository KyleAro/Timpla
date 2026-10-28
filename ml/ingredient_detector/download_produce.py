"""Download the original author's public YOLOv8m produce baseline."""
import hashlib
import html
import json
from pathlib import Path
import re
from urllib.parse import urlparse
from zipfile import is_zipfile
import requests

ROOT = Path(__file__).resolve().parents[2]
FILE_ID = '1XALsPwM4850LkmqsXIfmGhPj8s_nhuiK'
EXPECTED_SIZE = 52089985

def main():
    folder = ROOT / 'models' / 'produce'
    folder.mkdir(parents=True, exist_ok=True)
    output = folder / 'author-yolov8m.pt'
    session = requests.Session()
    response = session.get('https://drive.google.com/uc', params={'export': 'download', 'id': FILE_ID}, stream=True, timeout=90)
    response.raise_for_status()
    if 'text/html' in response.headers.get('Content-Type', ''):
        page = response.text
        form = re.search(r'<form id="download-form" action="([^"]+)"[^>]*>(.*?)</form>', page, re.S)
        if not form or urlparse(html.unescape(form[1])).hostname != 'drive.usercontent.google.com':
            raise RuntimeError('Public model download is not available; no model file was saved.')
        fields = {html.unescape(name): html.unescape(value) for name, value in re.findall(r'<input[^>]*type="hidden"[^>]*name="([^"]+)"[^>]*value="([^"]*)"', form[2])}
        response.close()
        response = session.get(html.unescape(form[1]), params=fields, stream=True, timeout=90)
        response.raise_for_status()
    if 'text/html' in response.headers.get('Content-Type', ''):
        raise RuntimeError('Drive returned HTML instead of model weights.')
    digest = hashlib.sha256()
    size = 0
    partial = output.with_suffix('.pt.part')
    with response, partial.open('wb') as stream:
        for block in response.iter_content(1024 * 1024):
            stream.write(block)
            digest.update(block)
            size += len(block)
    if size != EXPECTED_SIZE or digest.hexdigest() != 'a18624d446e2fea08384949115de0b49446f0be2487fc954a37a9d962f71e5d3' or not is_zipfile(partial):
        raise RuntimeError(f'Unexpected checkpoint format or size: {size} bytes')
    partial.replace(output)
    manifest = {
        'source_repository': 'https://github.com/henningheyen/Fruits-And-Vegetables-Detection-Dataset',
        'source_folder': 'https://drive.google.com/drive/folders/1I4mtQK11C3p41pO9raR0trgPVj0eQ2yb',
        'source_file_id': FILE_ID, 'original_filename': 'yolo_fruits_and_vegetables_v1.pt',
        'file': output.name, 'bytes': size, 'sha256': digest.hexdigest(),
        'role': 'Author-trained baseline; not trained by Timpla', 'inference_verified': False,
    }
    # Provenance is recorded separately in baseline-manifest.json.
    print(json.dumps(manifest, indent=2), flush=True)

if __name__ == '__main__':
    main()
