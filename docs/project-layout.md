# Timpla project layout

| Folder | Current purpose |
| --- | --- |
| `src/` | Mobile screens, routes, components, auth, account state and service interfaces |
| `assets/` | App design images and icons; placeholder recipe assets removed |
| `supabase/` | Existing account/database migrations, email templates and policy checks |
| `tests/` | Detector client/state regression checks |
| `datasets/` | No produce image dataset installed |
| `ml/` | Separate ingredient-detection inference and recipe-recommendation workspaces |
| `backend/` | Local team ingredient upload API |
| `models/` | Verified team ingredient-detector weights and metadata |
| `docs/` | Project setup, design and requirements |
| `tmp/` | Ignored development outputs |

## Current application scope

The interface, authentication, account settings, camera/upload screens and manual ingredient entry remain. The two placeholder recipes, catalog adapter/fetching, built-in recipe scoring and match percentages have been removed. Recipe screens show an unavailable state until an ML recommendation service is integrated. Only a recipe result type and empty recommendation interface remain; no model or substitute matcher is installed.

The old external produce assets and training folder remain removed. The team ingredient detector is now integrated through `backend/` and `src/services/detection.ts`; see `backend/README.md`. `ml/ingredient_detector/` contains inference code, while `ml/recipe_recommendation/` contains the separate recommendation work.

No live Supabase data was modified during this cleanup. Historical applied migrations and database design files remain as records; their recipe seeds do not populate the app because the catalog fetch path is removed.

## Configuration and generated files

Root Expo/TypeScript/package configuration remains in place. `.env.local` holds local configuration. `node_modules/`, `.expo/`, `dist/`, `.venv-model/` and `__pycache__/` are dependencies or generated files, not active recipe or detector implementations.
