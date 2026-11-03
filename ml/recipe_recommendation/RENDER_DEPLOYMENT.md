# Render recipe recommendation service

This service runs the experimental LightGBM LambdaRank model in `models/quick_v1`. It is a small API for the model already trained with synthetic, rule-generated labels; it does not train during deployment and does not use the YOLO detector. Its metrics measure agreement with synthetic rules, not real-user recommendation quality.

The root `render.yaml` deploys this API as `timpla-recipe-recommendation`. The health check is `GET /health`; recommendations use `POST /recommendations` with JSON such as `{"available":["egg","eggplant","cooking_oil","salt"],"limit":5}`. The service requires only LightGBM at runtime and loads its model/catalog once at startup.

The recipe API and the ingredient detector are separate services. Set Expo's `EXPO_PUBLIC_RECOMMENDATION_URL` to this service's `https://<service>.onrender.com` root URL after Render assigns it. The Expo app appends `/recommendations` automatically. Free Render instances may spin down when idle, so the first request can be delayed.
