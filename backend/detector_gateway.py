"""FastAPI coordinator that merges results from the separate detector services."""
import asyncio
from contextlib import asynccontextmanager
import os

import httpx
from fastapi import FastAPI, File, Form, HTTPException, UploadFile

MAX_BYTES = 5_000_000
IOU_THRESHOLD = 0.50
DEFAULT_GENERAL_CONFIDENCE = 0.10
DEFAULT_PRODUCE_CONFIDENCE = 0.50
DEFAULT_IMAGE_SIZE = 640
ALLOWED_IMAGE_SIZES = {640, 960, 1280}
REQUEST_TIMEOUT = httpx.Timeout(120.0, connect=10.0)


def service_urls():
    return {
        'general': os.environ.get('GENERAL_MODEL_URL', '').strip().rstrip('/'),
        'produce': os.environ.get('PRODUCE_MODEL_URL', '').strip().rstrip('/'),
    }


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http = httpx.AsyncClient(timeout=REQUEST_TIMEOUT)
    yield
    await app.state.http.aclose()


app = FastAPI(title='TIMPLA ingredient detector coordinator', lifespan=lifespan)


async def check_service(role: str, url: str):
    if not url:
        return {'role': role, 'ready': False, 'detail': 'Service URL is not configured.'}
    try:
        response = await app.state.http.get(f'{url}/health')
        if not response.is_success:
            return {'role': role, 'ready': False, 'detail': f'Health check returned HTTP {response.status_code}.'}
        payload = response.json()
        return {
            'role': role,
            'ready': payload.get('ready') is True,
            'status': payload.get('status', 'idle'),
            'model': payload.get('model'),
            'detail': None if payload.get('ready') is True else 'Service is not ready.',
        }
    except (httpx.HTTPError, ValueError):
        return {'role': role, 'ready': False, 'detail': 'Service is unreachable or returned invalid JSON.'}


async def service_health():
    urls = service_urls()
    results = await asyncio.gather(*(check_service(role, url) for role, url in urls.items()))
    ready = all(item['ready'] for item in results)
    status = 'active' if any(item.get('status') == 'active' for item in results) else 'idle'
    payload = {'ready': ready, 'status': status, 'models': results}
    if not ready:
        raise HTTPException(503, detail=payload)
    return payload


@app.get('/health')
async def health():
    return await service_health()


@app.get('/status')
async def status():
    return await service_health()


async def request_model(role: str, url: str, content: bytes, filename: str,
                        content_type: str, confidence: float, image_size: int):
    try:
        response = await app.state.http.post(
            f'{url}/detect',
            files={'image': (filename, content, content_type)},
            data={'confidence': str(confidence), 'image_size': str(image_size)},
        )
    except httpx.HTTPError as error:
        raise RuntimeError(f'{role} model service is unavailable.') from error

    try:
        payload = response.json()
    except ValueError as error:
        raise RuntimeError(f'{role} model service returned an invalid response.') from error

    if not response.is_success:
        if 400 <= response.status_code < 500:
            detail = payload.get('detail') if isinstance(payload, dict) else None
            raise ValueError(detail if isinstance(detail, str) else f'{role} model rejected the photo.')
        raise RuntimeError(f'{role} model service returned HTTP {response.status_code}.')
    if not isinstance(payload, dict) or not isinstance(payload.get('detections'), list):
        raise RuntimeError(f'{role} model service returned an invalid detections list.')
    return payload


@app.post('/detect')
async def detect(
    image: UploadFile = File(...),
    general_confidence: float = Form(DEFAULT_GENERAL_CONFIDENCE),
    produce_confidence: float = Form(DEFAULT_PRODUCE_CONFIDENCE),
    image_size: int = Form(DEFAULT_IMAGE_SIZE),
):
    if not (image.content_type or '').startswith('image/'):
        await image.close()
        raise HTTPException(415, 'Choose an image file.')
    if not 0.01 <= general_confidence <= 0.99 or not 0.01 <= produce_confidence <= 0.99:
        await image.close()
        raise HTTPException(422, 'Both confidence values must be between 0.01 and 0.99.')
    if image_size not in ALLOWED_IMAGE_SIZES:
        await image.close()
        raise HTTPException(422, 'Image size must be 640, 960, or 1280.')

    try:
        content = await image.read(MAX_BYTES + 1)
        if not content or len(content) > MAX_BYTES:
            raise HTTPException(413, 'Photo must be nonempty and 5 MB or smaller.')

        urls = service_urls()
        if not all(urls.values()):
            raise HTTPException(503, 'Detector model service URLs are not configured.')

        results = await asyncio.gather(
            request_model('general', urls['general'], content, image.filename or 'ingredient-photo',
                          image.content_type or 'application/octet-stream', general_confidence, image_size),
            request_model('produce', urls['produce'], content, image.filename or 'ingredient-photo',
                          image.content_type or 'application/octet-stream', produce_confidence, image_size),
            return_exceptions=True,
        )
        failures = [(role, result) for role, result in zip(('general', 'produce'), results)
                    if isinstance(result, Exception)]
        if failures:
            if all(isinstance(error, ValueError) for _, error in failures):
                raise HTTPException(422, str(failures[0][1])) from failures[0][1]
            roles = ', '.join(role for role, _ in failures)
            raise HTTPException(502, f'Could not get a result from the {roles} detector service.')

        general_result, produce_result = results
        if general_result.get('width') != produce_result.get('width') or general_result.get('height') != produce_result.get('height'):
            raise HTTPException(502, 'The detector services returned different image dimensions.')

        detections = general_result['detections'] + produce_result['detections']
        ingredients = {}
        for item in sorted(detections, key=lambda detection: detection.get('confidence', 0), reverse=True):
            name = item.get('name')
            label = item.get('label')
            confidence = item.get('confidence')
            if not isinstance(name, str) or not isinstance(label, str) or not isinstance(confidence, (int, float)):
                raise HTTPException(502, 'A detector returned an invalid ingredient record.')
            key = name.strip().casefold()
            if not key:
                raise HTTPException(502, 'A detector returned an empty ingredient name.')
            if key not in ingredients:
                ingredients[key] = {
                    'name': name,
                    'label': label,
                    'confidence': confidence,
                    'source_model': item.get('source_model'),
                }

        return {
            'model': 'YOLOv8n + YOLOv8m',
            'models': [
                {'file': general_result.get('model'), 'role': 'All non-produce classes; produce classes filtered out'},
                {'file': produce_result.get('model'), 'role': 'Fruit and vegetable classes'},
            ],
            'width': general_result['width'],
            'height': general_result['height'],
            'image_size': image_size,
            'iou_threshold': IOU_THRESHOLD,
            'thresholds': {
                'general_non_produce': general_confidence,
                'produce': produce_confidence,
            },
            'detections': detections,
            'ingredients': list(ingredients.values()),
        }
    finally:
        await image.close()
