"""Single-model FastAPI service used by the split TIMPLA detector deployment."""
from contextlib import asynccontextmanager
import hashlib
import os
from pathlib import Path
from threading import Lock

os.environ.setdefault('YOLO_CONFIG_DIR', '/tmp/ultralytics')
os.environ.setdefault('MPLCONFIGDIR', '/tmp/matplotlib')
os.environ.setdefault('YOLO_AUTOINSTALL', 'False')

import torch
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError
from starlette.concurrency import run_in_threadpool
from ultralytics import YOLO

from ml.ingredient_detector.detector import MAX_BYTES, decode_image, ingredient_name

ROOT = Path(__file__).resolve().parents[1]
GENERAL_CHECKPOINT = ROOT / 'models/ingredient_detector/YOLOv8n_merged_best.pt'
PRODUCE_CHECKPOINT = ROOT / 'models/produce/author-yolov8m.pt'
GENERAL_SHA256 = '93b271aa58c8841167fe1c244dd4c3f2d40babfe9164f740a1383d1ecb5e23d0'
PRODUCE_SHA256 = 'a18624d446e2fea08384949115de0b49446f0be2487fc954a37a9d962f71e5d3'
GENERAL_PRODUCE_LABELS = {
    'ampalaya', 'bell_pepper', 'cabbage', 'calamansi', 'carrot', 'chili', 'cucumber',
    'gabi', 'garlic', 'ginger', 'kalabasa', 'kangkong', 'lemon_grass', 'malunggay',
    'mushroom', 'okra', 'onion', 'papaya', 'pechay', 'potato', 'radish', 'red_onion',
    'sayote', 'sili', 'sili_haba', 'sili_labuyo', 'sitaw', 'spring_onions', 'talong',
    'taro_leaves', 'tomato', 'upo', 'white_onion',
}
PRODUCE_EXCLUDED_LABELS = {'Tomato', 'Strawberry'}
DEFAULT_IMAGE_SIZE = 640
IOU_THRESHOLD = 0.50
ALLOWED_IMAGE_SIZES = {640, 960, 1280}


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def checked_checkpoint(path: Path, expected_sha256: str) -> None:
    if not path.is_file():
        raise FileNotFoundError(f'Model checkpoint missing: {path}')
    if file_sha256(path) != expected_sha256:
        raise RuntimeError(f'Model checkpoint SHA-256 does not match: {path.name}')


def create_model_service(role: str) -> FastAPI:
    if role not in {'general', 'produce'}:
        raise RuntimeError('Set MODEL_ROLE to either general or produce for this service.')

    checkpoint = GENERAL_CHECKPOINT if role == 'general' else PRODUCE_CHECKPOINT
    expected_sha256 = GENERAL_SHA256 if role == 'general' else PRODUCE_SHA256
    default_confidence = 0.10 if role == 'general' else 0.50
    source_model = ('general YOLOv8n (non-produce)' if role == 'general'
                    else 'produce YOLOv8m')
    excluded_labels = sorted(GENERAL_PRODUCE_LABELS if role == 'general'
                             else PRODUCE_EXCLUDED_LABELS)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        checked_checkpoint(checkpoint, expected_sha256)
        torch.set_num_threads(1)
        try:
            torch.set_num_interop_threads(1)
        except RuntimeError:
            pass

        model = YOLO(str(checkpoint), task='detect')
        names = {int(key): value for key, value in model.names.items()}
        if role == 'general':
            if not GENERAL_PRODUCE_LABELS.issubset(set(names.values())):
                raise RuntimeError('The general checkpoint is missing configured produce labels.')
            class_ids = [key for key, label in names.items()
                         if label not in GENERAL_PRODUCE_LABELS]
        else:
            class_ids = [key for key, label in names.items()
                         if label not in PRODUCE_EXCLUDED_LABELS]
            if not class_ids:
                raise RuntimeError('No usable produce labels were found in the checkpoint.')

        app.state.model = model
        app.state.names = names
        app.state.class_ids = class_ids
        app.state.device = 0 if torch.cuda.is_available() else 'cpu'
        app.state.inference_lock = Lock()
        yield

    app = FastAPI(
        title=f'TIMPLA {role} ingredient detector',
        lifespan=lifespan,
    )

    @app.get('/health')
    def health():
        return {
            'ready': True,
            'status': 'active' if app.state.inference_lock.locked() else 'idle',
            'role': role,
            'model': checkpoint.name,
            'sha256': expected_sha256,
            'class_count': len(app.state.names),
            'included_class_count': len(app.state.class_ids),
            'excluded_labels': excluded_labels,
            'image_size': DEFAULT_IMAGE_SIZE,
            'default_confidence': default_confidence,
            'iou_threshold': IOU_THRESHOLD,
            'device': 'cuda' if app.state.device == 0 else 'cpu',
        }

    def infer(content: bytes, confidence: float, image_size: int):
        picture = decode_image(content)
        with app.state.inference_lock:
            result = app.state.model.predict(
                picture,
                imgsz=image_size,
                conf=confidence,
                iou=IOU_THRESHOLD,
                classes=app.state.class_ids,
                device=app.state.device,
                verbose=False,
            )[0]

        detections = []
        for box in result.boxes:
            class_id = int(box.cls.item())
            label = app.state.names[class_id]
            detections.append({
                'class_id': class_id,
                'label': label,
                'name': ingredient_name(label),
                'confidence': round(float(box.conf.item()), 4),
                'source_model': source_model,
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
            'role': role,
            'model': checkpoint.name,
            'source_model': source_model,
            'width': picture.width,
            'height': picture.height,
            'image_size': image_size,
            'confidence_threshold': confidence,
            'iou_threshold': IOU_THRESHOLD,
            'detections': detections,
            'ingredients': list(ingredients.values()),
        }

    @app.post('/detect')
    async def detect(
        image: UploadFile = File(...),
        confidence: float = Form(default_confidence),
        image_size: int = Form(DEFAULT_IMAGE_SIZE),
    ):
        if not (image.content_type or '').startswith('image/'):
            await image.close()
            raise HTTPException(415, 'Choose an image file.')
        if not 0.01 <= confidence <= 0.99:
            await image.close()
            raise HTTPException(422, 'Confidence must be between 0.01 and 0.99.')
        if image_size not in ALLOWED_IMAGE_SIZES:
            await image.close()
            raise HTTPException(422, 'Image size must be 640, 960, or 1280.')

        try:
            content = await image.read(MAX_BYTES + 1)
            if not content or len(content) > MAX_BYTES:
                raise HTTPException(413, 'Photo must be nonempty and 5 MB or smaller.')
            return await run_in_threadpool(infer, content, confidence, image_size)
        except (ValueError, OSError, UnidentifiedImageError,
                Image.DecompressionBombError, Image.DecompressionBombWarning) as error:
            raise HTTPException(422, 'Choose a valid supported still image under 40 megapixels.') from error
        finally:
            await image.close()

    return app


app = create_model_service(os.environ.get('MODEL_ROLE', '').strip().lower())
