# Filipino Recipes 2K: raw dataset candidate

Source: https://huggingface.co/datasets/joackimagno/FILIPINO_RECIPES_2K

The downloaded Parquet file contains a public Filipino recipe dataset. Reading the downloaded Parquet confirmed **1,988 rows**, with recipe names, preparation/cooking/total times, servings, full ingredients, instructions, and shortened ingredient names. The exact downloaded revision, URL, size and SHA-256 are recorded in `manifest.json`; `source-metadata.json` preserves publisher metadata. The dataset viewer snapshots are also retained. `audit.json` records an actual Parquet read: 1,988 rows, 1,890 unique recipe names, no nulls in the eight columns and no empty full-ingredient fields. This is a structural check, not recipe validation. `recipes.csv` is a complete CSV export of the same rows for inspection.

This is a candidate source for the recipe recommendation model, not a trained model or an approved training dataset. No source/license declaration was found in the publisher metadata inspected at download. Public availability does not establish permission to redistribute the underlying recipe text; confirm provenance/terms before publishing it in the app.

## Data quality and suitability

- Use the full `ingredients` field for extraction. Shortened `ingredient_names` are not guaranteed complete and can collapse meat cuts or omit important ingredients.
- Major/supporting/optional ingredient roles still need definition and review.
- No per-recipe source URL column is present in the inspected schema.
- Time strings, duplicate dishes and recipe variations need cleaning.
- This dataset does not supply human preference/ranking judgments for confirmed ingredient inventories.
- Keep raw data unchanged. Do not silently replace the reviewed seed JSON or train on guessed ingredient roles/labels.

A smaller alternative with source URLs is https://huggingface.co/datasets/joackimagno/filtered-filipino-recipes (141 rows). The V2 dataset https://huggingface.co/datasets/joackimagno/FILIPINO_RECIPES_2K_V2 also exists, but sample shortened ingredient lists omit core ingredients; it should not be preferred automatically because of its version name.
