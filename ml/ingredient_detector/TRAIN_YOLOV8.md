# Train the meat / chicken-part / seafood detector

This trains YOLOv8 detection, separate from the recipe ranking model. You run
training. No datasets are downloaded or combined by this setup.

## 1. Download and extract a dataset

On Roboflow select a published dataset version, Download Dataset, YOLOv8 format.
Extract the ZIP, for example into:

```text
datasets/meat_seafood/
  data.yaml
  train/images/
  train/labels/
  valid/images/
  valid/labels/
  test/images/       (if supplied)
  test/labels/       (if supplied)
```

The classes actually present in data.yaml determine what the model learns.
A chicken-parts dataset alone does not teach fish, pork or shrimp. For multiple
datasets, remap all class IDs into a shared vocabulary before merging; copying
different label files together unchanged is insufficient.

## 2. Open PowerShell at the project root

```powershell
Set-Location "C:\Users\User\OneDrive - Innobyte\Desktop\Timpla"
.\ml\recipe_recommendation\.venv\Scripts\python.exe -m venv ml/ingredient_detector/.venv
$py = ".\ml\ingredient_detector\.venv\Scripts\python.exe"
& $py -m pip install -r ml/ingredient_detector/requirements-training.txt
```

Create the environment only once. In a new terminal set $py again. Environment
activation and PowerShell execution-policy changes are not necessary.
The command reuses your existing working Python to create an independent detector
environment. If that interpreter is unavailable on another computer, use
`py -3.11 -m venv ml/ingredient_detector/.venv` with its installed Python3.11.

## 3. Check the extracted dataset

```powershell
& $py ml/ingredient_detector/train_yolov8.py --data "datasets/meat_seafood/data.yaml" --check-only
```

Use your actual data.yaml location. This checks YAML/split paths without training
or downloading weights; it does not certify box correctness. If paths are wrong,
edit data.yaml to point to the extracted folders. An absolute `path` with
`train: train/images`, `val: valid/images`, and optional `test: test/images` avoids
ambiguity. Preserve the downloaded `names` mapping and matching label class IDs.

## 4. Run a short CPU test

```powershell
& $py ml/ingredient_detector/train_yolov8.py --data "datasets/meat_seafood/data.yaml" --epochs 1 --imgsz 320 --batch 2 --device cpu --name meat_smoke_v1
```

This is a setup test, not a finished-quality model. First use may download the
standard pretrained yolov8n.pt weights and requires Internet access.

## 5. Train a longer run

```powershell
& $py ml/ingredient_detector/train_yolov8.py --data "datasets/meat_seafood/data.yaml" --epochs 50 --imgsz 640 --batch 4 --device cpu --name meat_seafood_v1
```

For the previously described 6GB-RAM laptop, start with batch2 and imgsz416 if
memory is tight. CPU training can be slow. Radeon610M is not a CUDA GPU; the
default here is CPU. If the PC has a working CUDA-enabled NVIDIA/PyTorch setup,
use `--device 0`. Check availability rather than assuming it:

```powershell
& $py -c "import torch; print('CUDA available:', torch.cuda.is_available())"
```

Default base model is yolov8n.pt. To fine-tune a different compatible checkpoint,
pass `--model "path/to/best.pt"`. Meat-only fine-tuning can degrade old produce
classes; retaining both in one detector requires a correctly merged training
dataset and evaluation of both groups.

## 6. Find your trained weights

```text
ml/ingredient_detector/runs/meat_seafood_v1/weights/best.pt
ml/ingredient_detector/runs/meat_seafood_v1/weights/last.pt
```

Use best.pt for prediction. Keep last.pt to resume an interrupted run. Results and
validation plots are in the run folder. Evaluate per-class metrics and your own
held-out phone photos before replacing the detector used by the app.

## 7. Test a photo

```powershell
& $py -c "from ultralytics import YOLO; m=YOLO('ml/ingredient_detector/runs/meat_seafood_v1/weights/best.pt'); m.predict(source='C:/path/to/chicken.jpg', conf=0.25, save=True, device='cpu')"
```

Replace the sample image path. The command prints and saves predictions. A model
can return no detections; do not force an ingredient label for every photo.

## 8. Resume after interruption

```powershell
& $py ml/ingredient_detector/train_yolov8.py --resume "ml/ingredient_detector/runs/meat_seafood_v1/weights/last.pt"
```

Resume uses the checkpoint's training settings. For a separate fresh run choose
a new --name such as meat_seafood_v2. Never overwrite earlier runs accidentally.

## Troubleshooting

- YAML not found: use the real extracted data.yaml path, quoted if it has spaces.
- Images not found: fix YAML paths; ensure the ZIP was extracted.
- Wrong classes: inspect names and label IDs; do not relabel by changing names alone.
- Out of memory: lower batch to1–2, lower imgsz and close other applications.
- CUDA unavailable: use cpu or install the appropriate PyTorch GPU build for your PC.
- Existing run: choose a new name, or resume last.pt.
- Dataset is classification/segmentation: download bounding-box detection data
  or deliberately convert annotations; this trainer expects a detection dataset.

Official references:
- https://docs.ultralytics.com/models/yolov8/
- https://docs.ultralytics.com/modes/train/
