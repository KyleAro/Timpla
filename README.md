# Timpla

Expo / React Native frontend for Filipino cooking, with authentication, account preferences, photo capture/upload and manual ingredient entry.

## Current scope

The interface, authentication and account settings remain. Photo upload and confirmed camera captures now call the team's local YOLOv12n ingredient detector. Detections can be corrected and supplemented manually. The checkpoint has 66 verified ingredient classes; its provenance and class mapping are under `models/ingredient_detector/`.

Recipe placeholders, catalog fetching and local recipe ranking remain removed. Recipe recommendation work is separate under `ml/recipe_recommendation/` and is not connected to the app yet.

See [detector setup and upload testing](backend/README.md), [project layout](docs/project-layout.md), and [authentication setup](docs/auth.md).

## Run

```powershell
npm ci
npx expo start --clear --lan
```

On a fresh checkout, copy `.env.example` to `.env.local` and configure Supabase. Preserve an existing `.env.local`. Restart Expo after configuration changes.

## Checks

```powershell
npm run lint
npm run typecheck
npm run test:detection
```
