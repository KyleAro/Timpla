"""Isolated, single-checkpoint test page for the released 68-class YOLOv8 model."""
from contextlib import asynccontextmanager
import hashlib
import io
from pathlib import Path
from threading import Lock

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from PIL import Image, ImageOps, UnidentifiedImageError
from ultralytics import YOLO

ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT = ROOT / 'models/ingredient_detector/YOLOv8n_merged_best.pt'
EXPECTED_SHA256 = '93b271aa58c8841167fe1c244dd4c3f2d40babfe9164f740a1383d1ecb5e23d0'
MAX_BYTES = 5_000_000
MAX_PIXELS = 40_000_000
IMAGE_SIZE = 640
CONFIDENCE = 0.10
IOU = 0.5


@asynccontextmanager
async def lifespan(app):
    if not CHECKPOINT.is_file():
        raise FileNotFoundError(f'Released YOLOv8 checkpoint missing: {CHECKPOINT}')
    digest = hashlib.sha256(CHECKPOINT.read_bytes()).hexdigest()
    if digest != EXPECTED_SHA256:
        raise RuntimeError('YOLOv8 checkpoint SHA-256 does not match the inspected release.')
    app.state.model = YOLO(str(CHECKPOINT), task='detect')
    app.state.lock = Lock()
    yield


app = FastAPI(title='TIMPLA single-model YOLOv8 test', lifespan=lifespan)


@app.get('/')
def page():
    return FileResponse(ROOT / 'backend/replica_v8.html')


@app.get('/health')
def health():
    model = app.state.model
    return {
        'ready': True,
        'status': 'active' if app.state.lock.locked() else 'idle',
        'model': CHECKPOINT.name,
        'sha256': EXPECTED_SHA256,
        'class_count': len(model.names),
        'image_size': IMAGE_SIZE,
        'confidence': CONFIDENCE,
        'iou': IOU,
        'device': 'cuda' if __import__('torch').cuda.is_available() else 'cpu',
    }


@app.post('/detect')
async def detect(
    image: UploadFile = File(...),
    confidence: float = Form(CONFIDENCE),
    image_size: int = Form(IMAGE_SIZE),
):
    if not 0.01 <= confidence <= 0.99:
        raise HTTPException(422, 'Confidence must be between 0.01 and 0.99.')
    if image_size not in {640, 960, 1280}:
        raise HTTPException(422, 'Image size must be 640, 960, or 1280.')
    if not (image.content_type or '').startswith('image/'):
        raise HTTPException(415, 'Choose an image file.')
    content = await image.read(MAX_BYTES + 1)
    await image.close()
    if not content or len(content) > MAX_BYTES:
        raise HTTPException(413, 'Photo must be nonempty and 5 MB or smaller.')
    try:
        with Image.open(io.BytesIO(content)) as source:
            if source.width * source.height > MAX_PIXELS or getattr(source, 'n_frames', 1) != 1:
                raise HTTPException(422, 'Choose a still image no larger than 40 megapixels.')
            source.load()
            picture = ImageOps.exif_transpose(source).convert('RGB')
    except (UnidentifiedImageError, OSError) as error:
        raise HTTPException(422, 'Choose a valid image file.') from error
    with app.state.lock:
        result = app.state.model.predict(
            picture, imgsz=image_size, conf=confidence, iou=IOU,
            device=0 if __import__('torch').cuda.is_available() else 'cpu', verbose=False,
        )[0]
    detections = []
    for box in result.boxes:
        class_id = int(box.cls.item())
        detections.append({
            'class_id': class_id,
            'label': app.state.model.names[class_id],
            'confidence': round(float(box.conf.item()), 4),
            'bbox_xyxy': [round(float(value), 2) for value in box.xyxy[0].tolist()],
        })
    ingredients = {}
    for item in sorted(detections, key=lambda detection: detection['confidence'], reverse=True):
        name = item['label'].replace('_', ' ').strip().lower()
        if name not in ingredients:
            ingredients[name] = {
                'name': name,
                'label': item['label'],
                'confidence': item['confidence'],
            }
    return {
        'model': CHECKPOINT.name,
        'architecture': 'YOLOv8n (released merged checkpoint; 68 classes)',
        'width': picture.width,
        'height': picture.height,
        'image_size': image_size,
        'confidence_threshold': confidence,
        'iou_threshold': IOU,
        'detections': detections,
        'ingredients': list(ingredients.values()),
    }
