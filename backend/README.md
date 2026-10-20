# Timpla YOLOv8 photo testing

This local prototype runs the dataset author's already-trained YOLOv8m checkpoint. It performs actual inference; it does not use planted ingredient results. It covers fruit/vegetable classes and does not detect meat or chicken cuts. The model file, source URL and checksum are in `models/produce/baseline-manifest.json`.

## Start the detector

From the project directory in PowerShell:

```powershell
.\.venv-model\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Keep that terminal running. On this PC, open http://localhost:8000 for an actual upload tester. `/health` reports model readiness and `/docs` documents the image endpoint.

## Test on the phone

The phone and PC must use the same Wi-Fi. `.env.local` currently points Expo at `http://192.168.1.5:8000`; update the address if this PC's LAN address changes. This is a public local endpoint address, not a secret or API key. Restart Expo after changing it:

```powershell
npx expo start --clear --lan
```

In Timpla, open Scan → upload a photo, or capture → confirm. Both flows send the confirmed photo to the same `/detect` endpoint. Results fills from model detections and stores the confidence values with the scan. Recipe matching still uses the small local recipe catalog. The app provides a retry action if the server cannot be reached.

You can also open `http://192.168.1.5:8000` in the phone browser to try Upload photo or Take photo independently of Expo. The browser camera option depends on the device's file picker.

If Windows displays a Python firewall prompt, permit private-network access for this local test. No router port forwarding or public deployment is needed. This is a local consultation prototype, not an authenticated production API.

## Image contract

`POST /detect`, multipart field **image**. Only actual, decodable still images of **1–5,000,000 bytes** are accepted. JPEG, PNG, WebP, BMP, TIFF, HEIF and AVIF are supported by the configured Pillow decoders. The API also caps input resolution at 40 megapixels. Uploads are processed in memory and are not stored by the API.

Response fields: `detections` (ingredient name, model confidence, source class ID and pixel bounding box), deduplicated `ingredients`, image dimensions and inference time. A confidence score is a model score, not an independently calibrated accuracy percentage.

The downloaded model retains its **63 original class IDs**. Incorrect source classes `Strawberry` and `Tomato` are filtered by name. The prepared training dataset has **61 remapped class IDs**; its class map must not be substituted into the existing baseline.

## Tests and CLI

```powershell
.\.venv-model\Scripts\python.exe training\smoke_test_model.py
.\.venv-model\Scripts\python.exe -m backend.test_detection
.\.venv-model\Scripts\python.exe training\predict_produce.py "C:\path\to\photo.jpg"
```

The CLI saves actual boxes and JSON under `models/produce/predictions/`. The smoke tests use source images and verify function only. Generalisation must be assessed on your own new phone photos; these checks do not establish a held-out accuracy score.

## Recreate the environment

```powershell
python -m venv --system-site-packages .venv-model
.\.venv-model\Scripts\python.exe -m pip install -r backend\requirements.txt
python training\download_baseline.py
```

Source code license and original model provenance are retained in the dataset folder. The source model uses Ultralytics' licensing terms; record those terms with your consultation materials.
