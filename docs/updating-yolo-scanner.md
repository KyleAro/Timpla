# Updating the YOLO ingredient scanner

The app has two detector paths. An installable Android build runs the bundled ONNX model on the phone. Expo Go and the web app use a Python detector service. Updating only one path will leave the other on the older model.

## What to hand over with a new checkpoint

- The trained `best.pt` checkpoint, its YOLO architecture/version, training image size, and the complete class names **in class ID order**.
- A SHA-256 checksum, checkpoint size, dataset version, train/validation/test split, per-class results, and sample photos with expected detections. Keep test photos separate from training data.
- The intended confidence and IoU thresholds. Check whether existing recipe ingredient names need aliases for renamed or new classes.

Do not commit the `.pt` checkpoint to Git. Put it in a versioned release or another stable download location and record its URL, size, and SHA-256 in `models/ingredient_detector/YOLOv8n_merged_best.manifest.json` (or rename that manifest and all references together). The downloader is `ml/ingredient_detector/prepare_split_models.py`.

## Python scanner and Railway

The local single-model API is `backend/replica_v8.py`. Update its checkpoint path, expected SHA-256, and inference settings. The split Railway general-model service is `backend/split_model_service.py`; update its checkpoint path, SHA-256, and `GENERAL_PRODUCE_LABELS` if the class list changes. The separate produce model remains in that split deployment, so check that the new general model does not duplicate produce detections. The comparison page has its own model path and label exclusions in `backend/dual_compare.py`. See `backend/RAILWAY_SPLIT_SERVICES.md` for deployment commands.

Run the downloader and `/health` and `/detect` checks with representative photos before changing the public service. Verify that returned labels map to the app's ingredient names.

## Offline Android scanner

The phone uses `assets/models/ingredients_68.onnx`, loaded by `src/services/offlineDetection.ts`. Its class ID mapping is `src/data/offlineDetectorLabels.json`. The current preprocessing uses RGB floats, letterboxing to **512 × 512**, and input shape `[1, 3, 512, 512]`. The output parser expects `[1, N, 6]` rows of `[x1, y1, x2, y2, confidence, classId]`, with boxes in model-image pixels and NMS already applied. These are code contracts, not properties of every YOLO export.

Export the new checkpoint to an ONNX model compatible with ONNX Runtime React Native and that input/output contract, or update `src/services/offlineDetection.ts` to match its actual shapes, preprocessing, output layout, and NMS. Replace the bundled ONNX file and update `src/data/offlineDetectorLabels.json` in exact class ID order. If the class count changes, rename the ONNX asset and update its static `require` path and `metro.config.js` as needed. Check aliases in `src/services/offlineDetection.ts` and the ingredient matching in `src/services/offlineRecommendations.ts`.

Validate the ONNX model with a local ONNX Runtime inference and compare detections against the `.pt` checkpoint on the same held-out photos. Build a new Android release APK; an already installed APK cannot use a new bundled model until it is updated. Expo Go cannot run the native ONNX module. Use `docs/offline-android-demo.md` to test a cold launch, camera scan, gallery upload, and recipe results in airplane mode on the actual presentation phone.
