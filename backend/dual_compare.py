"""Comparison-only FastAPI app for routing meat and produce to specialists."""
from contextlib import asynccontextmanager
import hashlib
from pathlib import Path
from threading import Lock

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from starlette.concurrency import run_in_threadpool
import torch
from ultralytics import YOLO

from ml.ingredient_detector.detector import decode_image, ingredient_name, MAX_BYTES

ROOT = Path(__file__).resolve().parents[1]
MEAT_WEIGHTS = ROOT / 'models/ingredient_detector/YOLOv8n_merged_best.pt'
MEAT_SHA256 = '93b271aa58c8841167fe1c244dd4c3f2d40babfe9164f740a1383d1ecb5e23d0'
PRODUCE_WEIGHTS = ROOT / 'models/produce/author-yolov8m.pt'
PRODUCE_SHA256 = 'a18624d446e2fea08384949115de0b49446f0be2487fc954a37a9d962f71e5d3'
GENERAL_PRODUCE_LABELS = {
    'ampalaya', 'bell_pepper', 'cabbage', 'calamansi', 'carrot', 'chili', 'cucumber',
    'gabi', 'garlic', 'ginger', 'kalabasa', 'kangkong', 'lemon_grass', 'malunggay',
    'mushroom', 'okra', 'onion', 'papaya', 'pechay', 'potato', 'radish', 'red_onion',
    'sayote', 'sili', 'sili_haba', 'sili_labuyo', 'sitaw', 'spring_onions', 'talong',
    'taro_leaves', 'tomato', 'upo', 'white_onion',
}
PRODUCE_MODEL_EXCLUDED_LABELS = {'Tomato', 'Strawberry'}
IOU = 0.5


def checked_checkpoint(path: Path, expected: str) -> None:
    if not path.is_file():
        raise FileNotFoundError(f'Model checkpoint missing: {path}')
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise RuntimeError(f'Model checkpoint checksum mismatch: {path.name}')


@asynccontextmanager
async def lifespan(app):
    checked_checkpoint(MEAT_WEIGHTS, MEAT_SHA256)
    checked_checkpoint(PRODUCE_WEIGHTS, PRODUCE_SHA256)
    torch.set_num_threads(1)
    try:
        torch.set_num_interop_threads(1)
    except RuntimeError:
        pass
    app.state.meat_model = YOLO(str(MEAT_WEIGHTS), task='detect')
    app.state.produce_model = YOLO(str(PRODUCE_WEIGHTS), task='detect')
    app.state.meat_names = {int(key): value for key, value in app.state.meat_model.names.items()}
    app.state.produce_names = {int(key): value for key, value in app.state.produce_model.names.items()}
    app.state.general_ids = [key for key, value in app.state.meat_names.items()
                             if value not in GENERAL_PRODUCE_LABELS]
    app.state.produce_ids = [key for key, value in app.state.produce_names.items()
                             if value not in PRODUCE_MODEL_EXCLUDED_LABELS]
    if not GENERAL_PRODUCE_LABELS.issubset(set(app.state.meat_names.values())):
        raise RuntimeError('The general checkpoint is missing one or more configured produce labels.')
    if not app.state.produce_ids:
        raise RuntimeError('No valid produce labels were found in the produce checkpoint.')
    app.state.device = 0 if torch.cuda.is_available() else 'cpu'
    app.state.lock = Lock()
    yield


app = FastAPI(title='TIMPLA two-model detector comparison', lifespan=lifespan)


@app.get('/')
def page():
    return FileResponse(ROOT / 'backend/dual_compare.html')


@app.get('/health')
def health():
    return {
        'ready': True,
        'status': 'active' if app.state.lock.locked() else 'idle',
        'device': app.state.device,
        'general_model': MEAT_WEIGHTS.name,
        'general_classes': [app.state.meat_names[key] for key in app.state.general_ids],
        'general_excluded_produce_labels': sorted(GENERAL_PRODUCE_LABELS),
        'produce_model': PRODUCE_WEIGHTS.name,
        'produce_class_count': len(app.state.produce_ids),
        'excluded_produce_labels': sorted(PRODUCE_MODEL_EXCLUDED_LABELS),
    }


def infer(content: bytes, image_size: int, general_confidence: float, produce_confidence: float):
    picture = decode_image(content)
    detections = []
    with app.state.lock:
        for model, names, class_ids, confidence, source in (
            (app.state.meat_model, app.state.meat_names, app.state.general_ids,
             general_confidence, 'general YOLOv8n (non-produce)'),
            (app.state.produce_model, app.state.produce_names, app.state.produce_ids,
             produce_confidence, 'produce YOLOv8m'),
        ):
            result = model.predict(
                picture, imgsz=image_size, conf=confidence, iou=IOU,
                classes=class_ids, device=app.state.device, verbose=False,
            )[0]
            for box in result.boxes:
                class_id = int(box.cls.item())
                label = names[class_id]
                detections.append({
                    'class_id': class_id,
                    'label': label,
                    'name': ingredient_name(label),
                    'confidence': round(float(box.conf.item()), 4),
                    'source_model': source,
                    'bbox_xyxy': [round(float(value), 2) for value in box.xyxy[0].tolist()],
                })
    ingredients = {}
    for item in sorted(detections, key=lambda detection: detection['confidence'], reverse=True):
        if item['name'] not in ingredients:
            ingredients[item['name']] = {
                'name': item['name'],
                'label': item['label'],
                'confidence': item['confidence'],
                'source_model': item['source_model'],
            }
    return {
        'models': [
            {'file': MEAT_WEIGHTS.name, 'role': 'All non-produce classes; produce classes filtered out'},
            {'file': PRODUCE_WEIGHTS.name, 'role': 'Fruit and vegetable classes'},
        ],
        'width': picture.width,
        'height': picture.height,
        'image_size': image_size,
        'iou_threshold': IOU,
        'thresholds': {'general_non_produce': general_confidence, 'produce': produce_confidence},
        'detections': detections,
        'ingredients': list(ingredients.values()),
    }


@app.post('/detect')
async def detect(
    image: UploadFile = File(...),
    general_confidence: float = Form(0.10),
    produce_confidence: float = Form(0.60),
    image_size: int = Form(640),
):
    if not (image.content_type or '').startswith('image/'):
        raise HTTPException(415, 'Choose an image file.')
    if image_size not in {640, 960, 1280}:
        raise HTTPException(422, 'Image size must be 640, 960 or 1280.')
    if not 0.01 <= general_confidence <= 0.99 or not 0.01 <= produce_confidence <= 0.99:
        raise HTTPException(422, 'Both confidence values must be between 0.01 and 0.99.')
    content = await image.read(MAX_BYTES + 1)
    await image.close()
    if not content or len(content) > MAX_BYTES:
        raise HTTPException(413, 'Photo must be nonempty and 5 MB or smaller.')
    try:
        return await run_in_threadpool(infer, content, image_size, general_confidence, produce_confidence)
    except (ValueError, OSError) as error:
        raise HTTPException(422, 'Choose a valid supported still image under 40 megapixels.') from error
