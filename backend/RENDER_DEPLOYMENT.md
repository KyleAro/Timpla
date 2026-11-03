# Deploy the Timpla ingredient detector to Render

The detector API is a separate Python web service. It serves the existing team YOLOv12n checkpoint together with the fruit and vegetable YOLOv8m checkpoint. It does not train models or run recipe recommendations.

The same Render Blueprint also defines a separate `timpla-recipe-recommendation` service for the experimental LightGBM ranker. It runs only the already-trained inference artifact; its synthetic-label limitations are documented in [the recipe deployment notes](../ml/recipe_recommendation/RENDER_DEPLOYMENT.md).

## Render configuration

The repository-root `render.yaml` defines the service, health check, dependency installation, and startup command. During the build, `ml/ingredient_detector/prepare_render_models.py` downloads both public checkpoint files and verifies their expected byte size and SHA-256 before the service starts. Model weights stay out of Git.

Connect this repository to Render and create the Blueprint from `render.yaml`. Once the deploy is live, verify `https://<service>.onrender.com/health` reports `"ready": true` and lists both model files. The service listens on Render's injected `$PORT` and exposes `POST /detect` for multipart field `image`.

## Configure the Expo app

Set `EXPO_PUBLIC_DETECTOR_URL` to the service root, for example `https://<service>.onrender.com` (without `/detect`). For local Expo Go testing, put that URL in the ignored `.env.local` and restart Expo. For a published app, provide the same public URL to the EAS build environment before creating a new app build; the URL is embedded in the client bundle.

If the Expo web client is hosted separately, set Render's `DETECTOR_ALLOWED_ORIGINS` to its exact origin, such as `https://<app-host>`. Native iOS and Android requests do not use browser CORS. Keep any existing Supabase configuration separate from the detector URL.

## Runtime sizing and limits

The API loads two PyTorch models and keeps one worker to avoid loading duplicate model copies. Render's Free web service provides 512 MB RAM and 0.1 CPU, so it may not have enough memory or speed for this combined detector. Start with a plan that provides at least 2 GB RAM if the Free instance fails its health check or inference under memory pressure. A Free service also spins down after 15 minutes idle, so its first request can wait for startup. Check the current Render compute plan and pricing before selecting a paid service.

Uploaded photos are decoded in memory and are not saved by the API. The API limits uploads to 5 MB and serializes inference requests.
