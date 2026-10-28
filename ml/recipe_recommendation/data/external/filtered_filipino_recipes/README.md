# Filtered Filipino Recipes: additional raw collection

Source: https://huggingface.co/datasets/joackimagno/filtered-filipino-recipes

Downloaded at the exact revision recorded in `manifest.json`, which also contains the source URL, byte size, retrieval time, and SHA-256. `source-metadata.json` preserves publisher metadata.

## Actual CSV inspection

- 141 records; 140 unique normalized recipe names.
- Every row has a nonempty full-ingredient field and instructions.
- 76 rows have source URLs; 65 have no source URL.
- Fields include name, times, servings, ingredient names, full ingredients, instructions, tools, description, URL, and source guideline flags.

See `audit.json` for the inspected schema and missing-URL records. The guideline flags are not human recommendation relevance labels or Timpla ingredient-role approval.

## Relationship to the larger collection

`../overlap-report.json` records overlap with the 1,988-row Filipino Recipes 2K collection: 73 shared normalized names, 67 additional normalized names, and 56 rows matching normalized title/full ingredients/instructions. Normalization ignores punctuation and case, so those are review candidates rather than an automatic deletion decision. Similar names can represent different recipes or variants.

Raw collections remain separate and unchanged. No automatic training merge or data split has been made. Deduplicate and group related variants before creating evaluation queries. Preserve source provenance when consolidating.

No dataset license was declared in the inspected publisher metadata. Confirm provenance and reuse terms before publishing source text or images. Ingredient roles and source quality still require review.
