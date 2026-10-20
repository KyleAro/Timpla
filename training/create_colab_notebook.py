"""Create a reproducible Colab notebook; does not launch training."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main():
    cells = []
    def markdown(text):
        cells.append({'cell_type': 'markdown', 'metadata': {}, 'source': text.splitlines(keepends=True)})
    def code(text):
        cells.append({'cell_type': 'code', 'execution_count': None, 'metadata': {}, 'outputs': [], 'source': text.splitlines(keepends=True)})
    markdown('''# Timpla — YOLOv8 produce training
Use a GPU runtime: **Runtime → Change runtime type → T4 GPU** (or another available GPU).

This notebook fine-tunes a new YOLOv8n model using the prepared **61-class** dataset. The separate author's baseline uses **63 original classes**; do not replace its class names with this dataset's remapped IDs. Data preparation quarantines known defects, but exhaustive manual annotation approval is still pending. Report validation metrics as preliminary.

Upload `timpla-produce-colab.zip` and its `bundle.json` to `MyDrive/Timpla/datasets/`. Keep the notebook output, class names and trained weights together.''')
    code('''%pip install -q "ultralytics==8.4.182" "PyYAML==6.0.3"
''')
    code('''from google.colab import drive
drive.mount('/content/drive')
from pathlib import Path
import hashlib, json, shutil, zipfile
import torch, yaml, ultralytics
from ultralytics import YOLO
assert torch.cuda.is_available(), 'Select a GPU runtime before training.'
print('GPU:', torch.cuda.get_device_name(0))
print('Ultralytics:', ultralytics.__version__, '| Torch:', torch.__version__)
DRIVE = Path('/content/drive/MyDrive/Timpla')
ARCHIVE = DRIVE / 'datasets/timpla-produce-colab.zip'
MANIFEST = DRIVE / 'datasets/bundle.json'
assert ARCHIVE.is_file() and MANIFEST.is_file(), 'Upload the prepared ZIP and bundle.json to MyDrive/Timpla/datasets.'
manifest = json.loads(MANIFEST.read_text())
digest = hashlib.sha256()
with ARCHIVE.open('rb') as stream:
    for block in iter(lambda: stream.read(1024 * 1024), b''):
        digest.update(block)
assert digest.hexdigest() == manifest['sha256'], 'ZIP checksum does not match bundle.json.'
LOCAL_ZIP = Path('/content/timpla-produce-colab.zip')
shutil.copyfile(ARCHIVE, LOCAL_ZIP)
with zipfile.ZipFile(LOCAL_ZIP) as archive:
    for member in archive.infolist():
        target = (Path('/content') / member.filename).resolve()
        assert Path('/content') in target.parents, 'Unexpected archive path.'
    archive.extractall('/content')
DATASET = Path('/content/timpla_produce')
config = yaml.safe_load((DATASET / 'data.yaml').read_text())
config['path'] = str(DATASET)
assert config['train'] != config['val'] != config['test']
for split in ('train', 'val', 'test'):
    assert list((DATASET / 'images' / split).glob('*')), f'{split} is empty'
DATA = DATASET / 'colab-data.yaml'
DATA.write_text(yaml.safe_dump(config, sort_keys=False))
print('Classes:', len(config['names']))
''')
    markdown('''## Quick training check
Run two epochs on a small fraction first to verify that the data and GPU work. This is a smoke test, not the final trained model. If GPU memory runs out, reduce `batch` to 4.''')
    code('''smoke = YOLO('yolov8n.pt')
smoke.train(data=str(DATA), epochs=2, fraction=0.05, imgsz=640, batch=8,
            device=0, workers=2, cache=False, seed=42,
            project='/content/timpla-smoke', name='check', exist_ok=False)
''')
    markdown('''## Full training
Start from pretrained weights (`.pt`), not a new architecture YAML. Run outputs go to Drive so checkpoints survive a Colab disconnect; images stay on local runtime storage for faster reads. Each run gets a new folder.''')
    code('''from datetime import datetime, timezone
RUN_NAME = 'produce-yolov8n-' + datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
RUN_DIR = DRIVE / 'runs' / RUN_NAME
model = YOLO('yolov8n.pt')
model.train(data=str(DATA), epochs=50, imgsz=640, batch=8, device=0,
            workers=2, patience=12, cache=False, seed=42, save=True,
            project=str(DRIVE / 'runs'), name=RUN_NAME, exist_ok=False)
BEST = RUN_DIR / 'weights/best.pt'
assert BEST.is_file()
print('Best checkpoint:', BEST)
''')
    markdown('''## Validate and test
Inspect precision, recall, mAP50, mAP50–95 and individual class results. Confidence on one detection is not an accuracy percentage. The source contains similar-image candidates and incomplete annotations, so these metrics are preliminary until that review is complete.''')
    code('''best = YOLO(str(BEST))
validation = best.val(data=str(DATA), split='val', imgsz=640, batch=8, device=0,
                      project=str(RUN_DIR), name='validation')
test = best.val(data=str(DATA), split='test', imgsz=640, batch=8, device=0,
                project=str(RUN_DIR), name='test')
report = {'validation': validation.results_dict, 'test': test.results_dict,
          'classes': best.names, 'ultralytics': ultralytics.__version__,
          'torch': torch.__version__, 'dataset_zip_sha256': manifest['sha256'],
          'evaluation_note': 'Preliminary source splits; not a benchmark on independently collected Timpla phone photos.'}
(RUN_DIR / 'evaluation.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
''')
    markdown('''## Try your own phone photos
Use clear photos of supported ingredients. Your own new photos are more informative than the source images the model may already have seen.''')
    code('''from google.colab import files
from IPython.display import display, Image as DisplayImage
uploaded = files.upload()
for filename in uploaded:
    assert Path(filename).stat().st_size <= 5_000_000, 'Use an image no larger than 5 MB.'
    result = best.predict(filename, conf=0.35, imgsz=640, device=0, verbose=False)[0]
    output = Path('/content') / (Path(filename).stem + '-detections.jpg')
    result.save(filename=str(output))
    display(DisplayImage(filename=str(output)))
''')
    markdown('''## Save the trained model
The ZIP contains the trained checkpoint and its exact class map. This new 61-class checkpoint is distinct from the existing author's 63-class baseline.''')
    code('''export = DRIVE / 'exports' / RUN_NAME
export.mkdir(parents=True, exist_ok=True)
shutil.copy2(BEST, export / 'best.pt')
(export / 'classes.json').write_text(json.dumps(best.names, indent=2))
shutil.copy2(RUN_DIR / 'evaluation.json', export / 'evaluation.json')
archive_path = shutil.make_archive(str(export), 'zip', export)
print('Saved to Drive:', archive_path)
files.download(archive_path)
''')
    markdown('''## Optional: resume an interrupted run
After reconnecting, rerun installation, Drive mounting and dataset extraction. Set `LAST` to the interrupted run's `weights/last.pt`, then execute the code below only when resuming an unfinished run.''')
    code('''# LAST = Path('/content/drive/MyDrive/Timpla/runs/YOUR_RUN/weights/last.pt')
# YOLO(str(LAST)).train(resume=True, data=str(DATA), device=0)
''')
    notebook = {'cells': cells, 'metadata': {'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}, 'language_info': {'name': 'python'}, 'colab': {'name': 'Timpla-YOLOv8-Colab.ipynb'}}, 'nbformat': 4, 'nbformat_minor': 5}
    path = ROOT / 'training' / 'Timpla-YOLOv8-Colab.ipynb'
    path.write_text(json.dumps(notebook, indent=2) + '\n')
    for cell in cells:
        if cell['cell_type'] == 'code':
            source = ''.join(cell['source'])
            if not source.startswith('%'):
                compile(source, str(path), 'exec')
    print(f'Created and syntax-checked {path}', flush=True)

if __name__ == '__main__':
    main()
