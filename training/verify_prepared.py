"""Independent structural/leakage checks on prepared YOLO boxes (not raw IDs)."""
from collections import Counter
import json
import math
from pathlib import Path
import re
from dataset_io import file_sha256

ROOT = Path(__file__).resolve().parents[1] / 'datasets' / 'fruits_vegetables' / 'prepared'

def main():
    config = (ROOT / 'data.yaml').read_text()
    names = {int(key): json.loads(value) for key, value in re.findall(r'^  (\d+): (.+)$', config, re.M)}
    assert set(names) == set(range(len(names)))
    assert 'Strawberry' not in names.values() and 'Tomato' not in names.values()
    hashes = {}
    counts = {}
    for split in ('train', 'val', 'test'):
        images = list((ROOT / 'images' / split).iterdir())
        labels = list((ROOT / 'labels' / split).glob('*.txt'))
        assert {p.stem for p in images} == {p.stem for p in labels}, f'Unpaired files in {split}'
        assert images, f'Empty split: {split}'
        classes = Counter()
        for image in images:
            digest = file_sha256(image)
            assert digest not in hashes, f'Duplicate image in prepared data: {image}, {hashes.get(digest)}'
            hashes[digest] = image
            lines = (ROOT / 'labels' / split / (image.stem + '.txt')).read_text().splitlines()
            assert lines, f'Empty annotation: {image}'
            for line in lines:
                fields = line.split()
                assert len(fields) == 5
                cls = int(fields[0])
                assert cls in names
                x, y, w, h = map(float, fields[1:])
                assert all(math.isfinite(v) for v in (x, y, w, h))
                assert w > 0 and h > 0
                assert min(x - w / 2, y - h / 2) >= -1e-8
                assert max(x + w / 2, y + h / 2) <= 1 + 1e-8
                classes[cls] += 1
        counts[split] = {'images': len(images), 'boxes': sum(classes.values())}
    print(json.dumps({'result': 'passed', 'classes': len(names), 'splits': counts}, indent=2))

if __name__ == '__main__':
    main()
