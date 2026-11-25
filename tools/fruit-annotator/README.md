# Timpla Annotate

Standalone, dependency-free browser application. It is separate from the Expo app.
Serve `dist/` from a static HTTPS or localhost origin; IndexedDB and secure-context
file APIs provide local workspace storage. The hosted Site is owner-private.

## Features

- Collapsible ingredient categories: Fruits, Vegetables, Chicken, Pork, Beef,
  Seafood, and custom categories. Seafood includes nested Fish, Shrimp & Prawns,
  Crabs & Lobsters, Shellfish, and Squid & Octopus groups. Category search opens
  matching groups automatically. Expand/collapse choices are kept during the session.
- JSON category values accept a list or an object of named subgroups, for example
  `{"seafood":{"Shrimp & Prawns":["White shrimp","Tiger prawn"]}}`.
- Add ingredients from a JSON/text file or pasted JSON. Preview lists new folders
  and skipped duplicates before one atomic settings write; existing IDs/images/boxes
  are preserved. Names ignore capitalization and extra spaces; export-name collisions
  are skipped. See `dist/ingredients-example.json` for the input format.
- Images uploaded inside an ingredient folder automatically use its class for new boxes.
- Multi-file and folder uploads; SHA-256 deduplication; originals stored in IndexedDB.
- Class assignment on import (not automatic ground-truth boxes).
- Draw, move, resize, relabel and delete boxes; per-image undo/redo; keyboard shortcuts.
- Label editor with names, export names, colors, usage counts and reassignment before deletion.
- Reviewed / pending / skipped / explicit background states; searchable paginated dataset.
- YOLO ZIP with reviewed originals, normalized labels, deterministic train/val/test splits and YAML.
- Full project ZIP backup and merge restore. ZIP exports stream directly to disk in supporting
  browsers; other browsers use a memory-backed download with a 650 MB safety limit.
- Optional compatible external `/detect` API for suggested boxes. Requires explicit consent,
  matching class names and API CORS permission. Every suggestion remains pending review.

No image-count limit is imposed. Storage and per-file decoding remain limited by the browser
and device. Keep backups: clearing site data deletes the local workspace. Each browser/device
has an independent workspace; this version does not synchronize images to a cloud account.
The illustrated practice sample is excluded from YOLO training exports.

Run `npm test` and `npm run check` here. The main repository's lint and typecheck also apply.
No training job is started by annotating or exporting. Review data quality, class balance,
and leakage between related images before starting a supervised model experiment.
