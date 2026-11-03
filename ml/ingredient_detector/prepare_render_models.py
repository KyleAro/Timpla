"""Fetch and verify detector checkpoints during a Render build."""
import hashlib
from pathlib import Path
from zipfile import is_zipfile

import requests

ROOT = Path(__file__).resolve().parents[2]
TEAM_URL = "https://github.com/rainbowmole/timpla/releases/download/YOLOv12n/YOLOv12n_Best.pt"
TEAM_PATH = ROOT / "models" / "ingredient_detector" / "YOLOv12n_Best.pt"
TEAM_SIZE = 5_558_810
TEAM_SHA256 = "5eaa3205138c11d71cbbddda946a51aa92180bed8afeb7bbe0de23746aac9f2d"


def download_team_checkpoint():
    TEAM_PATH.parent.mkdir(parents=True, exist_ok=True)
    partial = TEAM_PATH.with_suffix(".pt.part")
    digest = hashlib.sha256()
    size = 0
    with requests.get(TEAM_URL, stream=True, timeout=(20, 180)) as response:
        response.raise_for_status()
        with partial.open("wb") as output:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if not chunk:
                    continue
                size += len(chunk)
                if size > TEAM_SIZE:
                    raise RuntimeError("Team checkpoint download exceeded the expected file size.")
                digest.update(chunk)
                output.write(chunk)
    if size != TEAM_SIZE or digest.hexdigest() != TEAM_SHA256 or not is_zipfile(partial):
        partial.unlink(missing_ok=True)
        raise RuntimeError("Team checkpoint failed size, SHA-256, or PyTorch archive validation.")
    partial.replace(TEAM_PATH)
    print(f"Verified team detector checkpoint ({size:,} bytes).", flush=True)


def main():
    download_team_checkpoint()
    from ml.ingredient_detector.download_produce import main as download_produce

    download_produce()
    print("Both Render detector checkpoints are ready.", flush=True)


if __name__ == "__main__":
    main()
