# Timpla datasets

Dataset scope: **fruits and vegetables only**. A separate local backend runs the author's existing YOLOv8 baseline for photo testing. The Colab notebook prepares a new fine-tuning run; no new model training has been executed here.

## Prepared source

[LVIS Fruits and Vegetables](https://github.com/henningheyen/Fruits-And-Vegetables-Detection-Dataset) supplies YOLO detection annotations. Its GitHub source archive contains Git LFS pointers for the large training files; `training/download_produce.py` fetches the real archives and verifies every archive against its published size and SHA-256.

```text
datasets/
  fruits_vegetables/
    archives/                Original verified source ZIPs
    raw/                     Original images and labels
    prepared/                Separate, filtered YOLO detection layout
      data.yaml
      images/{train,val,test}/
      labels/{train,val,test}/
    source-data.yaml          Original configuration, retained for provenance
    class-remap.json         Original IDs -> prepared IDs
    downloads.json           Download URLs, byte sizes and checksums
    timpla-produce-colab.zip  Portable prepared files, created after audit
    bundle.json              ZIP size and checksum
  reports/
    produce-summary.json
    produce-class-counts.csv
    produce-quarantine.json
    produce-duplicates.json
    produce-preview-index.json
    previews/produce-boxes.jpg
  meat/                      Deferred; no validated downloads
  chicken_cuts/              Deferred; candidate review only
  philippine_ingredients/    Deferred; no validated downloads
```

## Preparation rules

- Preserve raw source files and all source metadata.
- Ignore macOS resource-fork files (`._*`); these are not photographs.
- Decode every image; check for a corresponding label file.
- Require YOLO detection rows: `class_id center_x center_y width height`.
- Validate class IDs, finite numbers, positive dimensions, and image boundaries.
- Only clamp rounding errors smaller than 0.00002; quarantine larger errors.
- Quarantine entire images carrying source-documented incorrect classes 30 (`Strawberry`) or 35 (`Tomato`). Do not guess replacement labels or silently merge them with valid strawberry/tomato classes.
- Remap the remaining 61 class IDs consistently and preserve the mapping.
- Quarantine empty annotation files for human background-image review.
- Detect exact decoded-image duplicates, including differently encoded copies. Remove redundant copies and quarantine conflicting annotations. Prefer test over validation over train when keeping an otherwise valid duplicate.
- Write separate train, validation and test paths. The original config incorrectly points validation at test images.
- Report class imbalance and similar-thumbnail groups across splits for manual review.

Raw images can contain several ingredient types. Keep all accepted object annotations together; do not put a mixed photo into a fruit-only folder while dropping its vegetable labels.

## Accuracy and review

Structural checks establish that the files and boxes can be used by YOLO; they do **not** establish that every object has the right name or every visible object has been labelled. The preview sheet is a sample, not exhaustive annotation approval. Similar-thumbnail groups are candidates for review, not proof of duplicates. A grouped near-duplicate review is still needed before claiming a clean final benchmark split.

The source is a broad produce dataset, not a complete collection of Philippine ingredients. Unsupported foods need additional labelled examples later. Dataset validity is separate from trained-model accuracy, which must be measured on held-out examples.

Source attribution, repository license, original names and download checksums are retained. The repository license does not replace the underlying LVIS/COCO image provenance.

## Reproduce on this machine

Use Python 3.9 or newer and `pip install -r training/requirements-data.txt` if Pillow is unavailable.

```powershell
python training/download_produce.py --source 'C:/Users/User/Downloads/Fruits-And-Vegetables-Detection-Dataset-main/Fruits-And-Vegetables-Detection-Dataset-main'
python training/prepare_produce.py
python training/verify_prepared.py
python training/bundle_produce.py
```

The preparation script refuses to replace a completed prepared config. Review an existing output before regenerating it.

For Colab later, upload `timpla-produce-colab.zip` to Drive, extract it into local runtime storage, and use `timpla_produce/data.yaml`. The ZIP retains annotations and filenames with the correct class remapping; do not combine it directly with other datasets that use different class IDs.
