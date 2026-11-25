# Railway recipe service

Live API: https://timpla-recipes-production.up.railway.app

Project: `reasonable-expression` (`8eea7c2e-ae69-423d-9354-00a41f0e13e1`).
Service: `timpla-recipes` (`51b392bf-bb8c-45c8-88fd-82d74df14d41`).
Environment: production.

The Expo app uses `EXPO_PUBLIC_RECOMMENDATION_URL` with the API root above.
Restart Expo after changing it; distributed app builds must include that setting
at build/update time. The API runs independently of the local computer.

Deployment uses an isolated package in `output/railway-recipe`, containing only:
Dockerfile, railway.json, requirements-render.txt, quick_api.py, quick_train.py,
preference_filters.py, models/quick_v1/catalog.json, models/quick_v1/ranker.txt,
and data/recipe_families.json. No local environment files or detector weights
are uploaded. Refresh these copies from this directory before redeploying.

From that package directory, authenticated with Railway CLI:

```powershell
npx --yes @railway/cli up . --service timpla-recipes --path-as-root --detach
npx --yes @railway/cli deployment list --service timpla-recipes --json
```

The Python server reads Railway's PORT environment variable. GET /health returns
ready after the model loads; POST /recommendations applies saved preferences.
See PREFERENCES.md for filtering rules and verified-diet limitations.

Public HTTPS access was explicitly approved by the owner. This prototype API
does not authenticate callers and does not expose stored profile records.
The service is deployed from this package, not automatically from Git pushes.
Railway hosting availability remains subject to the account's plan and limits.
