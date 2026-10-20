"""Verify the downloaded checkpoint and record real sample predictions."""
import json
from pathlib import Path
import re
from predict_produce import ProduceDetector, ROOT
from dataset_io import file_sha256

def main():
    detector = ProduceDetector()
    source = (ROOT / 'datasets' / 'fruits_vegetables' / 'source-data.yaml').read_text()
    expected = {int(i): name.strip() for i, name in re.findall(r'^\s+(\d+):\s*(.+)$', source, re.M)}
    assert detector.names == expected, 'Downloaded model class names do not match the source dataset.'
    assert 30 not in detector.allowed and 35 not in detector.allowed
    folder = ROOT / 'models' / 'produce'
    samples = ['000000000142.jpg', '000000000196.jpg']
    train = ROOT / 'datasets' / 'fruits_vegetables' / 'raw' / 'images' / 'train'
    results = []
    for name in samples:
        payload = detector.predict(train / name, folder / 'predictions', 0.35)
        assert payload['detections'], f'Model returned no detections on sample {name}'
        for item in payload['detections']:
            x1, y1, x2, y2 = item['bbox_xyxy']
            assert 0 <= x1 < x2 <= payload['width'] + 0.01
            assert 0 <= y1 < y2 <= payload['height'] + 0.01
            assert 0.35 <= item['confidence'] <= 1
        results.append(payload)
        print(name, payload['ingredients'], payload['inference_seconds'], flush=True)
    manifest = json.loads((folder / 'baseline-manifest.json').read_text())
    assert file_sha256(folder / manifest['file']) == manifest['sha256']
    manifest.update({'inference_verified': True, 'architecture': detector.model.model.yaml.get('yaml_file', 'YOLOv8'), 'class_count': len(detector.names), 'sample_count': len(results), 'test_scope': 'Source-data smoke test only; not a held-out accuracy measurement.'})
    (folder / 'baseline-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    (folder / 'smoke-test.json').write_text(json.dumps(results, indent=2) + '\n')
    print('Checkpoint loaded, class mapping verified, real detections returned, and prediction images saved.', flush=True)

if __name__ == '__main__':
    main()
