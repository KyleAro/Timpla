"""Run the downloaded YOLOv8 produce model on a real image (maximum 5 MB)."""
import argparse
import json
import io
import os
from pathlib import Path
import time

from PIL import Image, ImageOps
OPEN_IMAGE = Image.open  # Keep Pillow's decoder, before Ultralytics adds its lazy auto-installer.
ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault('YOLO_CONFIG_DIR', str(ROOT / 'tmp' / 'ultralytics'))
os.environ.setdefault('MPLCONFIGDIR', str(ROOT / 'tmp' / 'matplotlib'))
os.environ['YOLO_AUTOINSTALL'] = 'False'
import torch
from ultralytics import YOLO

MAX_BYTES = 5_000_000

class ProduceDetector:
    def __init__(self, weights=None):
        weights = Path(weights) if weights else ROOT / 'models' / 'produce' / 'author-yolov8m.pt'
        if not weights.is_file():
            raise FileNotFoundError(f'Model weights not found: {weights}')
        self.model = YOLO(str(weights), task='detect')
        torch.set_num_threads(min(4, os.cpu_count() or 1))
        self.names = dict(self.model.names)
        if len(self.names) not in (61, 63):
            raise ValueError('This checkpoint does not use the reviewed produce class taxonomy.')
        # Exclude source-documented wrong capitalized classes without shifting IDs.
        self.allowed = [idx for idx, name in self.names.items() if name not in {'Strawberry', 'Tomato'}]
        self.device = 0 if torch.cuda.is_available() else 'cpu'
        self.weights = weights.name

    def warmup(self):
        self.model.predict(Image.new('RGB', (64, 64)), imgsz=640, conf=0.35, classes=self.allowed, device=self.device, verbose=False)

    def predict(self, image_path, output_dir=None, confidence=0.35):
        image_path = Path(image_path)
        if not image_path.is_file() or not 0 < image_path.stat().st_size <= MAX_BYTES:
            raise ValueError('Choose a non-empty image file no larger than 5 MB.')
        return self.predict_bytes(image_path.read_bytes(), image_path.name, output_dir, confidence)

    def predict_bytes(self, content, filename='image.jpg', output_dir=None, confidence=0.35):
        if not 0 < len(content) <= MAX_BYTES:
            raise ValueError('Choose a non-empty image file no larger than 5 MB.')
        image_path = Path(filename).name
        with OPEN_IMAGE(io.BytesIO(content)) as source:
            if source.format not in {'JPEG', 'PNG', 'WEBP', 'BMP', 'TIFF', 'HEIF', 'AVIF'}:
                raise ValueError('Unsupported image format.')
            if source.width * source.height > 40_000_000:
                raise ValueError('Choose an image no larger than 40 megapixels.')
            if getattr(source, 'n_frames', 1) != 1:
                raise ValueError('Choose a still image.')
            source.load()
            picture = ImageOps.exif_transpose(source).convert('RGB')
        start = time.perf_counter()
        result = self.model.predict(picture, imgsz=640, conf=confidence, iou=0.5, classes=self.allowed, device=self.device, verbose=False)[0]
        detections = []
        for box in result.boxes:
            class_id = int(box.cls.item())
            name = self.names[class_id]
            detections.append({
                'class_id': class_id, 'source_name': name,
                'ingredient': name.split('/')[0],
                'confidence': round(float(box.conf.item()), 4),
                'bbox_xyxy': [round(float(v), 2) for v in box.xyxy[0].tolist()],
            })
        payload = {
            'model': self.weights, 'image': image_path,
            'width': picture.width, 'height': picture.height,
            'confidence_threshold': confidence,
            'inference_seconds': round(time.perf_counter() - start, 3),
            'detections': detections,
            'ingredients': sorted({item['ingredient'] for item in detections}),
        }
        if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            # Shorter display labels, preserving the checkpoint's actual class IDs.
            result.names = {idx: name.split('/')[0] for idx, name in result.names.items()}
            result.save(filename=str(output_dir / (Path(image_path).stem + '-detections.jpg')))
            (output_dir / (Path(image_path).stem + '.json')).write_text(json.dumps(payload, indent=2) + '\n')
        return payload

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('image', type=Path)
    parser.add_argument('--weights', type=Path)
    parser.add_argument('--output', type=Path, default=ROOT / 'models' / 'produce' / 'predictions')
    parser.add_argument('--confidence', type=float, default=0.35)
    args = parser.parse_args()
    if not 0 < args.confidence <= 1:
        parser.error('Confidence must be greater than 0 and at most 1.')
    detector = ProduceDetector(args.weights)
    print(json.dumps(detector.predict(args.image, args.output, args.confidence), indent=2), flush=True)

if __name__ == '__main__':
    main()
