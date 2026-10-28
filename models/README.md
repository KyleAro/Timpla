# Model artifacts



`ingredient_detector/YOLOv12n_Best.pt` is the team checkpoint published by rainbowmole/timpla. Its download URL, release digest and provenance are in `ingredient_detector/manifest.json`.



The checkpoint was inspected directly: YOLOv12n, 66 ingredient classes. `classes.json` is its actual internal mapping. The upstream README/release describes 68 classes; use the checkpoint mapping until the team resolves that discrepancy. Never substitute the old produce taxonomy.



Weights are ignored by Git. `smoke-test.json` records actual test-photo predictions when the API integration test runs. Those tests demonstrate function, not held-out accuracy.


## Combined upload detector

Each upload now runs the team YOLOv12n (66 classes) and the restored author-trained YOLOv8m produce model (63 original classes, 61 usable). Weights remain separate; this is inference with two models, not retraining or merged weights. The produce source is https://github.com/henningheyen/Fruits-And-Vegetables-Detection-Dataset and its exact digest is in `models/produce/baseline-manifest.json`.

The API retains source model, raw label, and model-local class ID on boxes. Equivalent names are normalized (for example, eggplant to talong); ingredient names are deduplicated. Specialist routing assigns all labels covered by the old produce model to YOLOv8m, with a provisional confidence threshold of 0.50. The team model handles the other ingredient labels at 0.10, including meat, eggs, seafood and Filipino vegetables absent from the old model. There is no two-model agreement requirement. Team predictions for non-produce ingredients at 0.5 or above block conflicting produce boxes on the same area (IoU above 0.3); separate ingredients can coexist. Empty results remain valid. These thresholds are provisional and have not been calibrated on a held-out evaluation. Independent model confidence scores are not calibrated for direct comparison. The known invalid capitalized Tomato and Strawberry source classes are excluded. Distinct objects keep separate boxes. Users still review the results; this fusion policy can miss overlapping objects and does not guarantee correctness.

Restore the produce checkpoint on another computer with `.\.venv-model\Scripts\python.exe -m ml.ingredient_detector.download_produce`. The download verifies the previously recorded SHA-256. No training image dataset is required for uploads. The `/health` endpoint reports both models and the combined ingredient-name list.
