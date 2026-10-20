"""Local YOLOv8 API shared by phone camera, image upload and browser testing."""
from contextlib import asynccontextmanager
import json
from pathlib import Path
import sys
from threading import Lock

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from starlette.concurrency import run_in_threadpool

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'training'))
from predict_produce import ProduceDetector, MAX_BYTES

try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    pass

@asynccontextmanager
async def lifespan(app):
    app.state.detector = ProduceDetector()
    app.state.lock = Lock()
    await run_in_threadpool(app.state.detector.warmup)
    yield

app = FastAPI(title='Timpla YOLOv8', version='0.1.0', lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origin_regex=r'https?://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+)(:\d+)?', allow_methods=['GET', 'POST'], allow_headers=['Content-Type'])

class UploadLimit:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http' or scope.get('method') != 'POST':
            return await self.app(scope, receive, send)
        body = bytearray()
        while True:
            message = await receive()
            if message['type'] == 'http.disconnect':
                return
            body.extend(message.get('body', b''))
            if len(body) > MAX_BYTES + 100_000:
                payload = json.dumps({'detail': 'Photo must be 5 MB or smaller.'}).encode()
                await send({'type': 'http.response.start', 'status': 413, 'headers': [(b'content-type', b'application/json')]})
                await send({'type': 'http.response.body', 'body': payload})
                return
            if not message.get('more_body', False):
                break
        replayed = False
        async def replay():
            nonlocal replayed
            if not replayed:
                replayed = True
                return {'type': 'http.request', 'body': bytes(body), 'more_body': False}
            return await receive()
        await self.app(scope, replay, send)

app.add_middleware(UploadLimit)

@app.get('/')
def demo():
    return FileResponse(ROOT / 'backend' / 'demo.html')

@app.get('/health')
def health():
    detector = app.state.detector
    return {'ready': True, 'model': detector.weights, 'task': 'fruit_and_vegetable_detection', 'classes': len(detector.allowed)}

@app.post('/detect')
async def detect(image: UploadFile = File(...)):
    try:
        if not (image.content_type or '').startswith('image/'):
            raise HTTPException(415, 'Choose an image file.')
        content = await image.read(MAX_BYTES + 1)
        if not content or len(content) > MAX_BYTES:
            raise HTTPException(413, 'Photo must be non-empty and 5 MB or smaller.')
        def predict():
            with app.state.lock:
                return app.state.detector.predict_bytes(content, 'image.jpg')
        try:
            return await run_in_threadpool(predict)
        except (ValueError, OSError) as error:
            raise HTTPException(422, 'Choose a valid supported image.') from error
    finally:
        await image.close()
