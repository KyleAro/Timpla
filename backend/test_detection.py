"""Integration checks that use the actual downloaded YOLOv8 checkpoint."""
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[1]

def main():
    image = ROOT / 'datasets/fruits_vegetables/raw/images/train/000000000142.jpg'
    base = 'http://127.0.0.1:8000'
    with requests.Session() as client:
        health = client.get(base + '/health', timeout=10)
        assert health.status_code == 200 and health.json()['ready']
        assert health.json()['classes'] == 61
        with image.open('rb') as stream:
            response = client.post(base + '/detect', files={'image': ('banana.jpg', stream, 'image/jpeg')}, timeout=90)
        assert response.status_code == 200, response.text
        payload = response.json()
        assert payload['detections'] and 'banana' in payload['ingredients'], payload
        assert all(d['confidence'] >= 0.35 and d['class_id'] not in (30, 35) for d in payload['detections'])
        assert client.post(base + '/detect', files={'image': ('bad.jpg', b'not an image', 'image/jpeg')}, timeout=30).status_code == 422
        assert client.post(base + '/detect', files={'image': ('bad.txt', b'text', 'text/plain')}, timeout=30).status_code == 415
        assert client.post(base + '/detect', files={'image': ('empty.jpg', b'', 'image/jpeg')}, timeout=30).status_code == 413
        assert client.post(base + '/detect', files={'image': ('big.jpg', b'x' * 5_000_001, 'image/jpeg')}, timeout=30).status_code == 413
        assert client.post(base + '/detect', files={'image': ('huge.jpg', b'x' * 5_200_000, 'image/jpeg')}, timeout=30).status_code == 413
        # Valid JPEG at the exact 5 MB boundary (JPEG permits trailing bytes).
        exact = image.read_bytes()
        exact += b'\0' * (5_000_000 - len(exact))
        assert client.post(base + '/detect', files={'image': ('exact.jpg', exact, 'image/jpeg')}, timeout=90).status_code == 200
        assert client.get(base + '/', timeout=10).status_code == 200
        print('Passed: actual YOLO upload detection, health, corrupted/spoofed files, empty images, 5 MB boundary, oversized bodies, and browser test page.', flush=True)

if __name__ == '__main__':
    main()
