# TIMPLA split detector services

This setup keeps the existing ingredient-recognition behavior and separates deployment only. The general YOLOv8n service excludes its configured fruit and vegetable labels. The existing author-trained YOLOv8m service supplies the produce labels, excluding the two source labels already excluded by the comparison API. The coordinator runs no model; it sends the same image to both services in parallel and combines their returned detections into the existing `/detect` response shape for the app's ingredient review.

This does not add recommendation, substitution, feedback, dataset collection, or model-training behavior. It implements the existing conceptual-framework path from captured ingredient image through ingredient recognition to the detected ingredient list for user validation.

## Files and checkpoint handling

The model checkpoints are excluded from Git. Each model service's build command downloads only its assigned checkpoint and verifies it against the repository manifest before startup. Commit `models/ingredient_detector/YOLOv8n_merged_best.manifest.json` with the service code; do not commit either `.pt` file. The produce downloader and its attribution metadata are already in `ml/ingredient_detector/` and `models/produce/`.

## Local run

Run the following in three PowerShell windows from the repository root. Install the model-service requirements once if this environment does not already have them:

```powershell
.\.venv-model\Scripts\python.exe -m pip install -r backend\requirements-model-service.txt
```

General model service, port 8005:

```powershell
$env:MODEL_ROLE = 'general'
.\.venv-model\Scripts\python.exe -m ml.ingredient_detector.prepare_split_models --role general
.\.venv-model\Scripts\python.exe -m uvicorn backend.split_model_service:app --host 0.0.0.0 --port 8005
```

Produce model service, port 8006:

```powershell
$env:MODEL_ROLE = 'produce'
.\.venv-model\Scripts\python.exe -m ml.ingredient_detector.prepare_split_models --role produce
.\.venv-model\Scripts\python.exe -m uvicorn backend.split_model_service:app --host 0.0.0.0 --port 8006
```

Coordinator, port 8007:

```powershell
$env:GENERAL_MODEL_URL = 'http://127.0.0.1:8005'
$env:PRODUCE_MODEL_URL = 'http://127.0.0.1:8006'
.\.venv-model\Scripts\python.exe -m uvicorn backend.detector_gateway:app --host 0.0.0.0 --port 8007
```

Open `http://localhost:8007/health` to confirm both model services are ready, then use `http://localhost:8007/docs` to send an image to `/detect`. The coordinator returns one JSON response with the merged `detections` and de-duplicated `ingredients`. Its defaults remain general confidence `0.10`, produce confidence `0.50`, image size `640`, and IoU `0.50`.

## Railway setup steps

The project has an Expo `package.json` and an existing Node service at its root, so leave root language detection alone. For each of the three Python detector services, set the service variable `RAILPACK_CONFIG_FILE=railway/railpack-python.json`; this selects Python 3.11 only for those services. Keep their root directory at the repository root so they can access the shared `backend/`, `ml/`, and `models/` files. Use custom build and start commands for each Railway service.

1. Commit and push `railway/railpack-python.json`, `backend/split_model_service.py`, `backend/detector_gateway.py`, `backend/requirements-model-service.txt`, `backend/requirements-gateway.txt`, `ml/ingredient_detector/prepare_split_models.py`, `backend/RAILWAY_SPLIT_SERVICES.md`, and `models/ingredient_detector/YOLOv8n_merged_best.manifest.json`. Do not use `git add .`: the workspace also contains local training and output files. Do not commit model `.pt` weights.
2. Create one Railway project from the TIMPLA GitHub repository. Keep the repository root as the root directory.
3. Create the **general model** service from the same repository. Set its build command to:

   ```sh
   python -m pip install --no-cache-dir -r backend/requirements-model-service.txt && python -m ml.ingredient_detector.prepare_split_models --role general
   ```

   Set its start command to:

   ```sh
   uvicorn backend.split_model_service:app --host 0.0.0.0 --port $PORT
   ```

   Add variables `MODEL_ROLE=general` and `RAILPACK_CONFIG_FILE=railway/railpack-python.json`; set its health check path to `/health`.
4. Create the **produce model** service from the same repository. Use the same build command but change the last argument to `--role produce`. Use the same start command, set `MODEL_ROLE=produce` and `RAILPACK_CONFIG_FILE=railway/railpack-python.json`, and set health check path to `/health`.
5. Keep both model services on Railway's private network. Do not generate public domains for them.
6. Wait until both model services report healthy in Railway before creating the coordinator.
7. Create the **coordinator** service from the same repository. Set its build command to:

   ```sh
   python -m pip install --no-cache-dir -r backend/requirements-gateway.txt
   ```

   Set its start command to:

   ```sh
   uvicorn backend.detector_gateway:app --host 0.0.0.0 --port $PORT
   ```

   Set health check path to `/health`. Add `RAILPACK_CONFIG_FILE=railway/railpack-python.json` and these service-reference variables, changing the service names only if you named the two model services differently:

   ```text
   GENERAL_MODEL_URL=http://${{timpla-general-model.RAILWAY_PRIVATE_DOMAIN}}:${{timpla-general-model.PORT}}
   PRODUCE_MODEL_URL=http://${{timpla-produce-model.RAILWAY_PRIVATE_DOMAIN}}:${{timpla-produce-model.PORT}}
   ```

8. Generate a public domain for the coordinator only. Open its `/health` endpoint and confirm both entries under `models` show `ready: true`. Open `/docs` and send a sample image to `/detect` to confirm the final combined response.
9. Check memory and CPU metrics for each model service after inference. They each hold one checkpoint, but model runtime memory is larger than the checkpoint file. If a service is restarted or reports an out-of-memory failure, raise that service's memory allocation before testing again.

Stop after the coordinator works. The Expo app URL is intentionally not changed here; connecting the app to the Railway coordinator is the next separate step.
