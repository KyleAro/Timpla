# External Filipino recipe collections

| Collection | Raw records | Local file |
| --- | ---: | --- |
| joackimagno/FILIPINO_RECIPES_2K | 1,988 | `filipino_recipes_2k/train.parquet`, with `recipes.csv` export |
| joackimagno/filtered-filipino-recipes | 141 | `filtered_filipino_recipes/recipes.csv` |

Total: **2,129 source records**, not 2,129 distinct recipes. Across both collections there are 1,952 distinct normalized titles; that is not a verified dish/recipe count. The filtered collection adds 67 normalized titles. An overlap audit found 56 matching normalized title/ingredient/instruction records across the sources.

`collections.json` indexes the exact source revisions, checksums and row counts. `overlap-report.json` records overlap without deleting or changing raw records. Each collection has a source manifest, source metadata, README and audit. The larger collection's CSV is an export of its Parquet file, not another independent dataset.

These are raw candidates for the team's model, separate from the six-recipe workflow demonstration at `../recipes.review.json`. No recipe collection has been silently connected to the mobile app. Source recipe data does not supply major/supporting ingredient roles or reviewed inventory-to-recipe ranking judgments. Clean, classify roles, deduplicate variants and review before training. Publisher license metadata was unspecified for both collections.
