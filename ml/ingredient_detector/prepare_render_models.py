"""Validate bundled detector checkpoints during a Render build."""
import hashlib
from pathlib import Path
from zipfile import is_zipfile

ROOT = Path(__file__).resolve().parents[2]
TEAM_PATH = ROOT / "models" / "ingredient_detector" / "YOLOv12n_Best.pt"
TEAM_SIZE = 5_558_810
TEAM_SHA256 = "5eaa3205138c11d71cbbddda946a51aa92180bed8afeb7bbe0de23746aac9f2d"


def verify_team_checkpoint():
    if not TEAM_PATH.is_file():
        raise FileNotFoundError(f"Bundled team checkpoint is missing: {TEAM_PATH}")
    size = TEAM_PATH.stat().st_size
    digest = hashlib.sha256(TEAM_PATH.read_bytes()).hexdigest()
    if size != TEAM_SIZE or digest != TEAM_SHA256 or not is_zipfile(TEAM_PATH):
        raise RuntimeError("Bundled team checkpoint failed size, SHA-256, or PyTorch archive validation.")
    print(f"Verified bundled team detector checkpoint ({size:,} bytes).", flush=True)


def main():
    verify_team_checkpoint()
    from ml.ingredient_detector.download_produce import main as download_produce

    download_produce()
    print("Both Render detector checkpoints are ready.", flush=True)


if __name__ == "__main__":
    main()
