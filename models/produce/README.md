# Working produce detector

`author-yolov8m.pt` is the existing trained YOLOv8 model supplied by the fruit-and-vegetable dataset author. It was not trained by Timpla. The original public download and local SHA-256 are recorded in `baseline-manifest.json`.

The checkpoint loads with 63 original class IDs. The API excludes the two capitalised classes documented as incorrect by the source, leaving 61 supported labels. The prepared training dataset remaps these labels; its IDs must not be applied directly to this existing checkpoint.

Actual source-image smoke tests produced detections, confidence values and boxes. Predictions and annotated photos are under `predictions/`; the JSON summary is in `smoke-test.json`. The test banana image returned a highest confidence of 0.9679. This is a confidence score, not a model accuracy measurement.

The running API at `http://localhost:8000` accepts your own image uploads. On the same Wi-Fi, its current phone address is `http://192.168.1.5:8000`. See `backend/README.md` for launch and Expo instructions.

This is a usable baseline for the consultation, with errors still possible on new photos. Users can correct detected ingredients in Results. Meat and chicken-part recognition are outside this checkpoint's classes. No independently collected Timpla phone-photo accuracy evaluation has been completed yet.
