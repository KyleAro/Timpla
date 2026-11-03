"""Train a YOLOv8 ingredient detector from an exported YOLO detection dataset."""
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, help='Extracted dataset data.yaml')
    parser.add_argument('--model', default='yolov8n.pt', help='Base weights or an existing detector checkpoint')
    parser.add_argument('--epochs', type=int, default=50)
    parser.add_argument('--imgsz', type=int, default=640)
    parser.add_argument('--batch', type=int, default=4)
    parser.add_argument('--device', default='cpu', help='cpu or CUDA GPU index, e.g. 0')
    parser.add_argument('--project', type=Path, default=Path(__file__).resolve().parent/'runs')
    parser.add_argument('--name', default='meat_seafood_v1')
    parser.add_argument('--check-only', action='store_true', help='Check dataset without training or downloading weights')
    parser.add_argument('--resume', type=Path, help='Resume an interrupted run from its weights/last.pt')
    args = parser.parse_args()
    if min(args.epochs,args.imgsz,args.batch) < 1:
        parser.error('epochs, imgsz and batch must be positive')
    try:
        from ultralytics import YOLO
        from ultralytics.data.utils import check_det_dataset
    except ImportError:
        parser.error('Install requirements with: python -m pip install -r ml/ingredient_detector/requirements-training.txt')
    if args.resume:
        if args.check_only:
            parser.error('--check-only requires --data and cannot be combined with --resume')
        checkpoint=args.resume.resolve()
        if not checkpoint.is_file():parser.error(f'Checkpoint not found: {checkpoint}')
        YOLO(str(checkpoint)).train(resume=True)
        return
    if args.data is None:
        parser.error('--data is required unless resuming')
    data=args.data.resolve()
    if not data.is_file():parser.error(f'Dataset YAML not found: {data}')
    if args.model.endswith(('-seg.pt','-cls.pt','-pose.pt','-obb.pt')):
        parser.error('Use detection weights such as yolov8n.pt, not segmentation/classification/pose/OBB weights')
    destination=args.project.resolve()/args.name
    if destination.exists() and not args.check_only:
        parser.error(f'Run exists: {destination}. Use a new --name or --resume its weights/last.pt')
    # Disable dataset download instructions. Images must already be extracted locally.
    info=check_det_dataset(str(data),autodownload=False)
    names=info['names']
    print('Dataset:',data,flush=True)
    print('Classes:',names,flush=True)
    print('Train:',info['train'],flush=True)
    print('Validation:',info['val'],flush=True)
    print('YAML paths checked. Annotation quality/class-ID mapping still requires inspection.',flush=True)
    if args.check_only:return
    model=YOLO(args.model,task='detect')
    if model.task!='detect':parser.error('Selected model must be an object detector')
    print(f'Training on {args.device}; first use may download base weights.',flush=True)
    model.train(data=str(data),epochs=args.epochs,imgsz=args.imgsz,batch=args.batch,
                device=args.device,workers=0,cache=False,project=str(args.project.resolve()),
                name=args.name,exist_ok=False,patience=15,seed=42,save=True)
    print('Training finished. Best weights:',Path(model.trainer.save_dir)/'weights/best.pt')
    print('Last checkpoint:',Path(model.trainer.save_dir)/'weights/last.pt')


if __name__=='__main__':
    from multiprocessing import freeze_support
    freeze_support()
    main()
