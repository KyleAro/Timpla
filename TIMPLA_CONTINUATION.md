# Timpla continuation notes — 2 November 2026

Current Codex chat: **Set up laptop for model training**.

## Product goal

Help users find multiple workable Filipino or Filipino-style meals from ingredients they already have. Maximize useful ingredient use and reduce waste and additional spending. Suggestions may adapt established recipes or describe sensible home-style preparations not present verbatim in the recipe collection. Do not force every ingredient into every meal or silently introduce missing ingredients.

Example inventory: egg, chicken breast, soy sauce, sayote. Desired possibilities include ginisang sayote with chicken and egg, tortang sayote with chicken, and chicken and sayote with soy sauce. Clearly distinguish suggested preparations from published recipes.

## Current implementation and confirmed gap

- Expo frontend; Python ingredient detector; separate recipe service on port 8001.
- Recipe collection: 2,074 records displayed as 1,864 conservative dish groups. Not 2,074 independently verified distinct dishes. 76 records contain Kawaling Pinoy links; many original publisher links are missing.
- `ml/recipe_recommendation/quick_train.py` ranks candidates with LightGBM using synthetic rule-derived labels. It only admits recipes whose essential ingredient requirements match before scoring.
- Audit reproduced zero eligible candidates for egg alone; egg + chicken breast + soy sauce + sayote; and chicken legs + papaya + sayote.
- Current ranker cannot generate or adapt recipes. Its training primarily reproduces ingredient-coverage rules, not human preferences.
- A generative recommendation flow has NOT been implemented. The current ranker remains active; no removal or retraining has been performed.

## Discussed next approach — not yet implemented

1. Confirm scanned/entered inventory; optional user-designated ingredients to use first.
2. Retrieve related Filipino cooking references using partial matches.
3. Generate several distinct workable meal options.
4. Validate ingredients and instruction consistency; make pantry assumptions explicit; reject invalid suggestions.
5. Display valid options with ingredients used, unused ingredients, adapted instructions, and source/type labels.

User requires FREE AI, not a paid API. Provider/model is undecided. Investigate actual account-specific hosted free-tier availability or a local model on the PC before selecting one. Do not claim unlimited free hosting or verified model quality.

The user challenged duplicate ranking: if generation already optimizes ingredient fit, the present LightGBM adds little distinct value. Discussed leaving it out of a future generative path, preserving the experiment, and only considering learned personalization after collecting relevant human feedback. This is a discussion, not an implemented migration. External API use is not training our own model.

Keep the app and existing user flow; change recommendation behavior incrementally. First test backend suggestions with manually entered inventory, then connect Results. Do not redesign or rebuild everything at once.

## UI and other decisions

- Preserve Timpla logo, wordmark, and branding assets.
- Recipe browser has photo-led cards, search, ingredient-based filter pills, and source versions inside each dish.
- Recipes are read-only ingredient/instruction pages, with top favorite button and bottom cooked-history action.
- Favorites and cooked history persist per account locally, not cross-device cloud sync.
- Detail photo fixed behind the rounded scrolling panel; back/save controls fixed above it.
- Two recipe versions split available width; more versions scroll horizontally.
- Small-card title size is consistent, two lines with trailing ellipsis; captions aligned.
- Ingredient count directly under single-version title removed.
- Four generated dish illustrations; shared neutral kitchen fallback for other dishes. Not unique photos for every dish.
- Search completeness audit was requested but interrupted before implementation. Current search uses case-insensitive title substring across grouped versions plus current filter. Do not claim comprehensive alias/token matching was added.

## Nutrition discussion — not implemented

Calculate from each ingredient's amount, preparation state, and a matched food composition record; sum contributions. Per-100g ingredient data can be the reference basis. Per-serving recipe values require known yield; per-100g finished-dish values require finished weight. Do not invent quantities or confuse nutrient totals with a health score. USDA FoodData Central proposed; PhilFCT local reference; no provider integration yet.

## Documentation request

Later document the five recommendation steps above, model choice/comparison, data preparation reasons and process, and measured progress. Distinguish proposed versus implemented behavior and synthetic supervision versus human labels.

Next conversation: decide a free generation approach and its actual hardware/quota constraints, clarify academic trained-model requirements, then implement and evaluate one backend slice. Do not run training without the user's instruction.
