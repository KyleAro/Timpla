# Local TIMPLA FastAPI ingredient detector





## Current machine





The current app scanner uses the released 68-class `YOLOv8n_merged_best.pt` checkpoint at 640 inference size, confidence 0.10 and IoU 0.50. Its manifest and SHA-256 are recorded in `models/ingredient_detector/YOLOv8n_merged_best.manifest.json`. The separate `backend.main:app` endpoint still contains the earlier dual-model experiment; the app proxy is pointed at the single-model service below.





The existing `.venv-model` environment was reused for this prototype (Python 3.9.13, PyTorch 2.5.1 CPU, Ultralytics 8.4.182). The classmate recommends Python 3.10–3.12 for new setups. Actual loading and inference are tested here rather than assumed from that recommendation.





From the project root:





```powershell


.\.venv-model\Scripts\python.exe -m uvicorn backend.replica_v8:app --host 0.0.0.0 --port 8003


```





Keep the service running while testing. The single-model FastAPI service loads the same checkpoint as the upload comparison page. Avoid starting a second instance on port 8003.





- Browser upload tester and comparison controls: http://localhost:8003


- Health and model settings: http://localhost:8003/health


- API schema: http://localhost:8003/docs


- Current PC LAN upload tester: http://192.168.1.3:8003





## Test the app





The app's `.env.local` currently enables detection and uses `EXPO_PUBLIC_DETECTOR_URL=http://192.168.1.3:8081/timpla-detector`. The phone and PC must be on the same reachable local network. If the PC address changes, update that variable and restart Expo. The IP address is not a credential. Preserve the Supabase settings.





```powershell


npx expo start --clear --lan


```





Use Scan or Upload photo. Camera captures are sent only after confirmation; library uploads are sent after selection/validation. Results show editable ingredient names, with manual additions/removals. Model architecture and confidence scores stay off the app screen. Recipe requests and cards are paused while LightGBM work continues. No ingredient predictions are planted.





If Windows asks about Python firewall access, allow the private network used for this test. This is a local prototype service, not a production deployment. No router port forwarding is needed. A phone cannot use localhost to refer to the PC.





## Contract





`POST /detect`, multipart field `image`, actual decodable still JPEG/PNG/WebP/HEIF/AVIF/BMP/TIFF up to 5,000,000 bytes and 40 megapixels. HEIF and AVIF decoders are included in the pinned requirements. AVIF uses pillow-avif-plugin with Pillow 11.2.1. Invalid images return JSON validation errors; unexpected inference failures return a readable JSON error. The browser tester also handles non-JSON server errors. The API enforces file/body limits and serializes model inference. Uploaded photos are decoded in memory and not saved by the API.





Response: checkpoint name, architecture, decoded dimensions, inference time, bounding boxes with raw source label and confidence, and a deduplicated ingredient list. Source class names are never reconstructed from an external ID list. Confidence is not an accuracy percentage.





## Checks





```powershell


npm run test:detection


npm run lint


npm run typecheck


.\.venv-model\Scripts\python.exe -m backend.test_detection


```





The Python integration checks use the actual checkpoint and two attributed public photos under `tmp/ingredient-detector-samples`. They verify request/response behavior, invalid/oversized files and actual predictions. AVIF encode/upload, corrupt-image rejection, and JSON error handling have regression coverage. They are not a model-accuracy evaluation. The client tests cover multipart upload, invalid responses, manual corrections, stale scan results and account reset.





The current single-model weight and its checksum are recorded in `models/ingredient_detector/YOLOv8n_merged_best.manifest.json`. The prior YOLOv12n experiment's weight is documented separately in `models/ingredient_detector/manifest.json`. For a new Python environment, install CPU-compatible PyTorch plus `backend/requirements.txt`; keep model/package versions with test records. Do not copy virtual environments between machines.



## Earlier dual-model experiment

`backend.main:app` retains the earlier team YOLOv12n (66 classes) plus author-trained produce YOLOv8m (63 original classes, 61 usable) experiment. The current app proxy no longer targets that dual-model service. Its thresholds and fusion policy below describe that prior experiment, not the active single-model scanner.

The API retains source model, raw label, and model-local class ID on boxes. Equivalent names are normalized (for example, eggplant to talong); ingredient names are deduplicated. Specialist routing assigns all labels covered by the old produce model to YOLOv8m, with a provisional confidence threshold of 0.50. The team model handles the other ingredient labels at 0.10, including meat, eggs, seafood and Filipino vegetables absent from the old model. There is no two-model agreement requirement. Team predictions for non-produce ingredients at 0.5 or above block conflicting produce boxes on the same area (IoU above 0.3); separate ingredients can coexist. Empty results remain valid. These thresholds are provisional and have not been calibrated on a held-out evaluation. Independent model confidence scores are not calibrated for direct comparison. The known invalid capitalized Tomato and Strawberry source classes are excluded. Distinct objects keep separate boxes. Users still review the results; this fusion policy can miss overlapping objects and does not guarantee correctness.

Restore the produce checkpoint on another computer with `.\.venv-model\Scripts\python.exe -m ml.ingredient_detector.download_produce`. The download verifies the previously recorded SHA-256. No training image dataset is required for uploads. The `/health` endpoint reports both models and the combined ingredient-name list.

## Phone connection through Expo

Expo Go now sends detection requests to `http://192.168.1.3:8081/timpla-detector/detect`. The Metro middleware in `metro.config.js` and `scripts/detectorProxy.cjs` forwards POST /detect and GET /health to the single-model FastAPI service at 127.0.0.1:8003. The `/health` response includes the detector's `active` or `idle` state, so browser and phone development use the local proxy route.

Keep both Python and Expo running. Restart Expo after the proxy or `.env.local` changes. On the phone, `http://192.168.1.3:8081/timpla-detector/health` checks the complete route. If Python is stopped, the app receives an explicit service-unavailable message. This proxy is only part of the development server; production builds require a deployed detector URL.

## SDK 57 phone photo uploads

Native uploads use `File` from `expo-file-system` and `fetch` from `expo/fetch`. SDK 57 installs Expo fetch by default. Its multipart serializer rejects the older React Native `{uri, name, type}` parts because they have no `bytes()` method; that serialization failure can look like a network error before any server request occurs. Client tests exercise the actual installed Expo serializer, verify File bytes and MIME headers, and reproduce rejection of the old URI object. Browser uploads continue to use browser fetch and Blob.

## Recipe model development

Recipe recommendations are disconnected while the team develops the model in `ml/recipe_recommendation/`. The scanner service only handles ingredient detection.
