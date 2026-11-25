# Active plan: YOLOv12n meat and seafood

Produce uses the existing author-trained `models/produce/author-yolov8m.pt`; no produce training is planned. The previous YOLOv8n plan is superseded. Its downloaded produce dataset remains under `yolov8n-training/sources/produce` as reference material.

Fine-tune pretrained `yolo12n.pt` on chicken, pork, beef and seafood bounding-box annotations. `raw/` contains collection buckets, not finalized detection classes. Finalize supported classes and consistent annotation IDs before creating `dataset/data.yaml`. Keep related images in the same split to prevent leakage.

Only meat and seafood are target classes. Include reviewed produce-only negative images with empty target annotations; mixed images must label all target meat/seafood objects. Evaluate false positives on produce, mixed images and difficult raw cuts. Separate models do not guarantee zero false detections.

Initial experiment: maximum 50 epochs, 640-pixel training images, batch 4, seed 42 and early-stopping patience 15. These are proposed settings inherited from the training utility, not measured results. Record actual optimizer, learning rate, software versions, dataset version and completed epochs from the run.

From the repository root, after preparing labels:

```powershell
.venv-model/Scripts/python.exe ml/ingredient_detector/train_yolov8.py --data yolov12-training/dataset/data.yaml --model yolo12n.pt --epochs 50 --imgsz 640 --batch 4 --device 0 --project yolov12-training/runs --name meat_seafood_v1
```

The shared utility's historical filename does not choose architecture: `--model yolo12n.pt` does. Device 0 requires CUDA; use cpu otherwise. Training has not started.

The app detector remains disabled pending evaluation and integration. Future inference must restrict YOLOv8m to approved produce labels and the new YOLOv12n to approved meat/seafood labels, permit empty detections, preserve user correction, and validate confidence thresholds and overlap handling using held-out images. Report per-class precision, recall, mAP and false positives on negative images.

Model documentation: https://docs.ultralytics.com/models/yolo12/
