# Timpla recipe recommendation: human review first

This standalone Python workspace is separate from the mobile app and the team's YOLO detector. It prepares and trains a LightGBM LambdaRank model to order real Filipino recipes from a confirmed ingredient inventory.

## Current state

The additional 141-row filtered Filipino collection is also downloaded. Both source collections total 2,129 raw records and are indexed in `data/external/collections.json`. The overlap audit found 67 additional normalized titles and 56 matching normalized content records; see `data/external/README.md`. Raw rows are preserved separately rather than blindly concatenated.

An existing external Filipino recipe dataset has now been downloaded at `data/external/filipino_recipes_2k/`. The actual Parquet audit found 1,988 records and 1,890 unique recipe names, with full ingredients and instructions. This is the larger candidate collection to prepare next. It has not been assigned major/supporting roles or incorporated into training; publisher license metadata is unspecified. See its README, provenance manifest and audit. The six-record JSON below remains a small reviewed-workflow demonstration, not a substitute for the external collection.

Six source-backed recipe records are proposed for review, along with eight draft ingredient-inventory scenarios. This is a small seed collection, not a comprehensive or validated recipe dataset. No relevance labels have been invented. No production model has been trained and nothing is connected to the app.

Only ingredient facts, source links and proposed categories are stored. Full source instructions and photos are not copied. Source pages retain their rights; the JSON is not a license grant. This metadata alone is not a complete cooking-instruction catalog.

## Behavior

1. The user confirms YOLO ingredients, edits mistakes, and adds forgotten ingredients.
2. Every major ingredient must exist in that confirmed inventory before a recipe can be a candidate. No automatic purchase suggestions, ingredient substitutions, or raw-to-cooked conversions are made.
3. Supporting ingredients can be missing for candidate discovery, but are explicitly listed as requiring confirmation. Major availability does not guarantee that the dish can be cooked as written at no additional cost. Optional ingredients are separate. Quantities are not assessed.
4. Explicit ingredient exclusions filter recipes before ranking, including excluded supporting/optional ingredients. This is an ingredient exclusion feature, not a verified allergen ontology.
5. A trained model ranks only eligible candidates. It can learn preferences involving available-ingredient use, use-first ingredients, supporting ingredients, preparation time and region. Its score is not an accuracy percentage or probability.

Garlic, onion, sauces and similar ingredients have per-recipe roles. Soy sauce and vinegar are major ingredients in the proposed adobo record. Cooked rice is distinct from uncooked rice. A generic pork detection does not automatically satisfy a pork-belly requirement.

## Python setup

Python 3.11 or newer, from the project root:

```powershell
py -3.11 -m venv ml/recipe_recommendation/.venv
.\ml\recipe_recommendation\.venv\Scripts\python.exe -m pip install -r ml/recipe_recommendation/requirements.txt
```

Audit/preview/review-queue commands and unit tests use Python's standard library. Only training and learned recommendations need the installed packages.

```powershell
.\ml\recipe_recommendation\.venv\Scripts\python.exe ml/recipe_recommendation/cli.py audit
.\ml\recipe_recommendation\.venv\Scripts\python.exe ml/recipe_recommendation/cli.py preview --ingredients egg talong
```

`preview` is clearly labeled an unranked eligibility preview; it never claims to be model inference. It does not populate the app with placeholder recipes.

## Review workflow

1. Open `data/recipes.review.json`. Visit each source and review the major/supporting/optional assignments and recipe timing. Then fill `reviewed_by` and `reviewed_at` for each approved record. Revise uncertain records instead of guessing. All records must be reviewed before training.
2. Review `data/queries.review.json`. These are constructed research scenarios, not observed users. Replace/expand them with realistic cases and fill `reviewed_by`. Assign each query to `train`, `validation`, or `test`. Give related inventories the same `leakage_group`, and keep that group in one split. Exact inventories may not cross splits. The catalog itself stays available in all splits; these experiments evaluate ranking new inventory queries, not recognition of unseen recipes.
3. Create the candidate review CSV with `review-queue`. An initial blank queue is provided. The command refuses to overwrite existing reviewer work; use a new output path if recipe roles or queries change, then review the new queue.
4. Fill `relevance` and `reviewer` in every candidate row. Use 3 for highly useful, 2 for useful, 1 for weak, and 0 for unsuitable to that user's situation. Consider use-first items, missing supporting ingredients and preferences. Do not label automatically using the feature formula. Add a reason in `notes` where helpful. A query needs at least two eligible recipes with different judgments and at least one useful candidate.
5. Keep validation for model selection and test for the final evaluation. Do not tune based on repeatedly viewing test results. More independent queries and a larger reviewed recipe catalog are needed for credible conclusions.

```powershell
.\ml\recipe_recommendation\.venv\Scripts\python.exe ml/recipe_recommendation/cli.py review-queue --output ml/recipe_recommendation/data/relevance.next.csv
.\ml\recipe_recommendation\.venv\Scripts\python.exe ml/recipe_recommendation/cli.py train --output ml/recipe_recommendation/artifacts/v1
```

Training fails clearly on missing reviews, blank labels, unknown pairs, missing candidate judgments, uninformative groups, and split leakage. It saves a text-format model, input checksums, feature order, catalog fingerprint, query counts and metrics. Existing artifact folders are not overwritten.

Evaluation reports macro NDCG@5 and precision over up to five returned candidates (relevance >= 2), compared with an inventory-utilization baseline. Small-catalog results are not evidence of broad cooking suitability. The app's old percentage matcher has not been restored.

```powershell
.\ml\recipe_recommendation\.venv\Scripts\python.exe ml/recipe_recommendation/cli.py recommend --model ml/recipe_recommendation/artifacts/v1 --ingredients egg talong oil salt --use-first talong
.\ml\recipe_recommendation\.venv\Scripts\python.exe -m unittest discover -s ml/recipe_recommendation/tests -v
```

A trained model refuses a changed recipe catalog or alias mapping: version the data and retrain. Keep model and metadata together. No unsafe pickle loading is used.

## Sources

Source URLs and authors are stored per recipe in `data/recipes.review.json`. Ingredient role choices are our proposals, not claims by the source authors. No substitutions have been approved.

Model documentation: https://lightgbm.readthedocs.io/en/stable/pythonapi/lightgbm.LGBMRanker.html
