# Superseded plan

Active training plan: ../yolov12-training/README.md. Produce training is cancelled; retain YOLOv8m for produce. Contents below are historical.

# TIMPLA YOLOv8n training workspace

The current detector connection is disabled locally through `EXPO_PUBLIC_DETECTOR_ENABLED=false` in `.env.local`. Reload the app after changing this value. Existing checkpoints are retained as references; no YOLOv8n ingredient model has been trained yet.

`raw/` organizes source images by ingredient category and proposed cut. These folders are collection buckets, not a finalized detection class list. Fruits and vegetables currently have unassigned buckets for incoming datasets. Seafood separates fish, shellfish (mollusks), crustaceans and cephalopods.

`dataset/images/{train,val,test}` and `dataset/labels/{train,val,test}` are the final YOLO detection layout. Every image needs bounding-box annotations with consistent class IDs. Putting photos into named folders alone does not create an object detection dataset. Preserve original dataset splits and keep near-duplicate photos in the same split.

The existing produce checkpoint's recorded source is https://github.com/henningheyen/Fruits-And-Vegetables-Detection-Dataset . Its training images are distributed at https://www.kaggle.com/datasets/henningheyen/lvis-fruits-and-vegetables-dataset . Model weights do not contain the source images. Keep the downloaded source with its original annotations under `sources/produce/`; remap class IDs when combining it with meat datasets. The source author documents erroneous Tomato and Strawberry classes; inspect these before importing.

Do not train until a reviewed class list, bounding-box labels and `dataset/data.yaml` exist. Use the existing training utility from the repository root:

```powershell
.venv-model/Scripts/python.exe ml/ingredient_detector/train_yolov8.py --data yolov8n-training/dataset/data.yaml --model yolov8n.pt --epochs 50 --imgsz 640 --batch 4 --device 0 --project yolov8n-training/runs --name ingredients_v1
```

`--device 0` requires a compatible CUDA GPU; use `--device cpu` otherwise. Training duration and detection quality have not been established. Final weights will be connected only after training and evaluation.
