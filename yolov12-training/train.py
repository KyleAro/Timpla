"""Audited, versioned YOLO12n training and same-class fine-tuning."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

from audit_dataset import audit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, required=True)
    parser.add_argument('--name', required=True, help='New experiment name; existing runs are never overwritten')
    parser.add_argument('--model', default='yolo12n.pt', help='Official base weights or verified previous best.pt')
    parser.add_argument('--device', default='cpu', help='CPU by default; select 0 only after CUDA verification')
    parser.add_argument('--batch', type=int, default=2, help='Small initial batch; adjust after measuring memory and epoch time')
    parser.add_argument('--epochs', type=int, default=50)
    parser.add_argument('--imgsz', type=int, default=640)
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args()
    if Path(args.name).name != args.name or args.name in ('.', '..'):
        parser.error('Use a single directory name for --name')
    if min(args.batch, args.epochs, args.imgsz) < 1:
        parser.error('Batch, epochs and image size must be positive')
    data = args.data.resolve()
    destination = Path(__file__).resolve().parent / 'runs' / args.name
    if destination.exists():
        parser.error('Run already exists; choose a new name')
    report = audit(data)
    if not report['passed']:
        print(json.dumps(report, indent=2))
        sys.exit('Dataset audit failed; resolve errors before training')
    if args.check_only:
        print(json.dumps(report, indent=2))
        return
    import torch
    import ultralytics
    from ultralytics import YOLO
    if args.device != 'cpu' and not torch.cuda.is_available():
        sys.exit('CUDA unavailable; configure CUDA or explicitly select --device cpu')
    model = YOLO(args.model, task='detect')
    architecture = str(model.model.yaml.get('yaml_file', '')).lower()
    if '12' not in architecture:
        sys.exit(f'Expected YOLO12 architecture, got {architecture!r}')
    destination.mkdir(parents=True)
    # Leave evidence on disk even if training is interrupted.
    settings = dict(epochs=args.epochs, imgsz=args.imgsz, batch=args.batch,
                    device=args.device, workers=0, cache=False, patience=15,
                    seed=42, save=True)
    source_weights = Path(args.model)
    metadata = {'started_utc': datetime.now(timezone.utc).isoformat(), 'data': str(data),
                'dataset_yaml_sha256': hashlib.sha256(data.read_bytes()).hexdigest(),
                'initial_weights': args.model, 'architecture': architecture,
                'initial_weights_sha256': hashlib.sha256(source_weights.read_bytes()).hexdigest() if source_weights.is_file() else None,
                'torch': torch.__version__, 'ultralytics': ultralytics.__version__,
                'settings': settings, 'audit': report}
    (destination / 'experiment.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')
    model.train(data=str(data), project=str(destination.parent), name=args.name,
                exist_ok=True, **settings)
    print('Best checkpoint:', destination / 'weights' / 'best.pt')


if __name__ == '__main__':
    from multiprocessing import freeze_support
    freeze_support()
    main()
