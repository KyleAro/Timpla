# Adding data and improving specificity

1. Keep original exports and their source terms unchanged. Register each version in source-inventory.csv with actual download date and provenance. Do not copy historical license claims without checking the export.
2. Review source class names before mapping. Keep pata/hock separate from belly; keep beef cuts and organs separate when annotations support them. Never manufacture specific labels from a generic beef/chicken/pork annotation.
3. Create a new dataset version for every merge. Keep stable class IDs for unchanged classes and record any new class IDs. Rebuild and audit all annotations when the class list changes.
4. Assign related captures and duplicates as groups before splitting. Freeze a representative test set and record hashes; collect additional evaluation examples for genuinely new classes. Use validation for threshold and model selection, not the final test set.
5. Run `python yolov12-training/audit_dataset.py --data PATH/data.yaml --report PATH/audit.json`. This checks directory-based YOLO exports, box geometry, class IDs, missing class coverage and exact duplicate leakage. It does not prove semantic annotation correctness; review box previews and near-duplicates separately.
6. For additional examples of the same classes, fine-tune the previous best checkpoint on a combined dataset containing old and new examples. Training only new examples risks forgetting previous classes. Use a new run name; preserve every previous checkpoint and report.
7. For new classes, create a reviewed dataset/class-map version and start a separate experiment. Ultralytics may reinitialize incompatible detection-head parameters; verify actual transfer logs and all old/new classes. Do not use resume for a changed dataset or taxonomy. Resume is for continuing the same interrupted experiment.
8. Compare new and previous models on the same held-out evaluation data. Record per-class precision/recall/mAP, confusion cases, produce-only false positives and latency. Deploy only after review of regressions and weak classes. No fixed accuracy target is guaranteed by image count or epochs.

Training entry point: `ml/ingredient_detector/train_yolov8.py --model yolo12n.pt` (historical filename). For same-class fine-tuning replace the model argument with a verified prior `best.pt`, and use a new project/run name. Keep produce inference separate with the existing YOLOv8m checkpoint.

Current blocker: the supplied project includes scripts/reports, not meat image exports. No Roboflow API key was available during setup. No meat training has started.
