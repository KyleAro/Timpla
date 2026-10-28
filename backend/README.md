# Local team ingredient detector API





## Current machine





The model is downloaded and SHA-256 verified against the GitHub release. The actual checkpoint contains **66 classes**, despite the source README's 68-class claim. It is YOLOv12n, not YOLOv8. `model.names` is the source of truth.





The existing `.venv-model` environment was reused for this prototype (Python 3.9.13, PyTorch 2.5.1 CPU, Ultralytics 8.4.182). The classmate recommends Python 3.10–3.12 for new setups. Actual loading and inference are tested here rather than assumed from that recommendation.





From the project root:





```powershell


.\.venv-model\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000


```





Keep the service running while testing. The agent-started background instance logs to `tmp/ingredient-server-network.stderr.log` and `tmp/ingredient-server-network.stdout.log`. Avoid starting a second instance on the same port.





- Browser upload tester: http://localhost:8000


- Health and actual class mapping: http://localhost:8000/health


- API schema: http://localhost:8000/docs


- Current PC LAN upload tester: http://192.168.1.2:8000





## Test the app





The app's `.env.local` currently uses `EXPO_PUBLIC_DETECTOR_URL=http://192.168.1.2:8081/timpla-detector`. The phone and PC must be on the same reachable local network. If the PC address changes, update that variable and restart Expo. The IP address is not a credential. Preserve the Supabase settings.





```powershell


npx expo start --clear --lan


```





Use Scan or Upload photo. Camera captures are sent only after confirmation; library uploads are sent after selection/validation. The ingredient results show loading, model-confidence values, retry/rescan, and manual additions/removals. No ingredient predictions are planted and no placeholder recipes or local recipe-ranking rules are restored.





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





The model weights must be downloaded separately on another computer; see `models/ingredient_detector/manifest.json` for the release URL and expected SHA-256. For a new Python environment, install CPU-compatible PyTorch plus `backend/requirements.txt`; keep model/package versions with test records. Do not copy virtual environments between machines.



## Combined upload detector

Each upload now runs the team YOLOv12n (66 classes) and the restored author-trained YOLOv8m produce model (63 original classes, 61 usable). Weights remain separate; this is inference with two models, not retraining or merged weights. The produce source is https://github.com/henningheyen/Fruits-And-Vegetables-Detection-Dataset and its exact digest is in `models/produce/baseline-manifest.json`.

The API retains source model, raw label, and model-local class ID on boxes. Equivalent names are normalized (for example, eggplant to talong); ingredient names are deduplicated. Specialist routing assigns all labels covered by the old produce model to YOLOv8m, with a provisional confidence threshold of 0.50. The team model handles the other ingredient labels at 0.10, including meat, eggs, seafood and Filipino vegetables absent from the old model. There is no two-model agreement requirement. Team predictions for non-produce ingredients at 0.5 or above block conflicting produce boxes on the same area (IoU above 0.3); separate ingredients can coexist. Empty results remain valid. These thresholds are provisional and have not been calibrated on a held-out evaluation. Independent model confidence scores are not calibrated for direct comparison. The known invalid capitalized Tomato and Strawberry source classes are excluded. Distinct objects keep separate boxes. Users still review the results; this fusion policy can miss overlapping objects and does not guarantee correctness.

Restore the produce checkpoint on another computer with `.\.venv-model\Scripts\python.exe -m ml.ingredient_detector.download_produce`. The download verifies the previously recorded SHA-256. No training image dataset is required for uploads. The `/health` endpoint reports both models and the combined ingredient-name list.

## Phone connection through Expo

Expo Go now sends detection requests to `http://192.168.1.2:8081/timpla-detector/detect`. The Metro middleware in `metro.config.js` and `scripts/detectorProxy.cjs` forwards only POST /detect and GET /health to the Python service at 127.0.0.1:8000. This uses the same inbound connection that already serves the phone app. Browser development uses its current page origin. No extra firewall rule is needed for port 8000.

Keep both Python and Expo running. After changing Metro configuration, restart Expo; after changing the public detector URL, reload the phone app. On the phone, `http://192.168.1.2:8081/timpla-detector/health` checks the complete route. If Python is stopped, the app receives an explicit service-unavailable message. This proxy is only part of the development server; production builds require a deployed detector URL.

## SDK 57 phone photo uploads

Native uploads use `File` from `expo-file-system` and `fetch` from `expo/fetch`. SDK 57 installs Expo fetch by default. Its multipart serializer rejects the older React Native `{uri, name, type}` parts because they have no `bytes()` method; that serialization failure can look like a network error before any server request occurs. Client tests exercise the actual installed Expo serializer, verify File bytes and MIME headers, and reproduce rejection of the old URI object. Browser uploads continue to use browser fetch and Blob.

## Recipe model development

Recipe recommendations are disconnected while the team develops the model in `ml/recipe_recommendation/`. The scanner service only handles ingredient detection.
