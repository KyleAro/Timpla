"""Local upload API for the team's ingredient detector."""
from contextlib import asynccontextmanager
import json
import logging
from threading import Lock

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from starlette.concurrency import run_in_threadpool
from PIL import Image, UnidentifiedImageError
from ml.ingredient_detector.detector import IngredientDetector, MAX_BYTES, ROOT, FUSION_POLICY


@asynccontextmanager
async def lifespan(app):
    app.state.detector=IngredientDetector()
    app.state.inference_lock=Lock()
    await run_in_threadpool(app.state.detector.warmup)
    yield


app=FastAPI(title='Timpla team ingredient detector',lifespan=lifespan)
app.add_middleware(CORSMiddleware,
    allow_origin_regex=r'https?://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+|172\.(1[6-9]|2\d|3[01])\.\d+\.\d+)(:\d+)?',
    allow_methods=['GET','POST'],allow_headers=['Content-Type'])


class LimitUploadBody:
    def __init__(self,app): self.app=app
    async def __call__(self,scope,receive,send):
        if scope['type']!='http' or scope.get('method')!='POST':
            return await self.app(scope,receive,send)
        body=bytearray()
        while True:
            message=await receive()
            if message['type']=='http.disconnect': return
            body.extend(message.get('body',b''))
            if len(body)>MAX_BYTES+100_000:
                payload=json.dumps({'detail':'Photo must be 5 MB or smaller.'}).encode()
                await send({'type':'http.response.start','status':413,'headers':[(b'content-type',b'application/json')]})
                await send({'type':'http.response.body','body':payload})
                return
            if not message.get('more_body',False): break
        delivered=False
        async def replay():
            nonlocal delivered
            if not delivered:
                delivered=True
                return {'type':'http.request','body':bytes(body),'more_body':False}
            return await receive()
        await self.app(scope,replay,send)


app.add_middleware(LimitUploadBody)


@app.get('/')
def upload_test():
    return FileResponse(ROOT/'backend/upload.html')


@app.get('/health')
def health():
    detector=app.state.detector
    return {'ready':True,'model':'YOLOv12n_Best.pt','architecture':'YOLOv12n + YOLOv8m',
            'classes':len(detector.names),'class_names':detector.names,'models':detector.models,
            'supported_ingredients':len(detector.supported_names),'ingredient_names':detector.supported_names,
            'fusion_policy':FUSION_POLICY}


@app.post('/detect')
async def detect(image: UploadFile=File(...)):
    try:
        if not (image.content_type or '').startswith('image/'):
            raise HTTPException(415,'Choose an image file.')
        content=await image.read(MAX_BYTES+1)
        if not 0<len(content)<=MAX_BYTES:
            raise HTTPException(413,'Photo must be nonempty and 5 MB or smaller.')
        def predict():
            with app.state.inference_lock:
                return app.state.detector.predict(content)
        try:
            return await run_in_threadpool(predict)
        except (ValueError,OSError,UnidentifiedImageError,Image.DecompressionBombError,Image.DecompressionBombWarning) as error:
            raise HTTPException(422,'Choose a valid supported still image under 40 megapixels.') from error
        except Exception as error:
            logging.getLogger(__name__).exception('Ingredient detection failed')
            raise HTTPException(500,'The detector could not process this photo. Try another photo or retry.') from error
    finally:
        await image.close()
