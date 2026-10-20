# Timpla

An Expo / React Native app for identifying ingredients from photos and finding Filipino recipes.

## Run the app

```powershell
npm ci
Copy-Item .env.example .env.local
npx expo start --clear --lan
```

Set `EXPO_PUBLIC_API_URL` in `.env.local` to the detector's address, for example `http://YOUR_PC_LAN_IP:8000`. The phone and computer must use the same Wi-Fi for local testing. Restart Expo after changing this value.

## Run YOLOv8 detection

The current prototype uses an existing author-trained fruit and vegetable YOLOv8m model. It is not yet a Timpla-trained model. Model weights and datasets are downloaded separately and are excluded from Git.

```powershell
python -m venv .venv-model
.\.venv-model\Scripts\python.exe -m pip install -r backend\requirements.txt
.\.venv-model\Scripts\python.exe training\download_baseline.py
.\.venv-model\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000` to test photo uploads. The app's camera and upload flows use the same detector. See [backend setup and tests](backend/README.md) for details.

## Training data

See [datasets](datasets/README.md) for sources and preparation instructions. The Colab workflow is in [Timpla-YOLOv8-Colab.ipynb](training/Timpla-YOLOv8-Colab.ipynb). Dataset checks and sample reviews do not establish model accuracy; evaluation on independent images is still needed. Recipe matching currently uses a small local sample catalog.

## Checks

```powershell
npm run typecheck
npm run lint
```
