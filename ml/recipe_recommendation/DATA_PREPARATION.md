# Timpla: step-by-step preparation of recipe data for machine learning

Preparation snapshot: **30 October 2026, Asia/Manila**. This is a record of the
actual work and its limitations, suitable as a basis for the paper's methodology.
Comparisons below are design tradeoffs, not measured experiments demonstrating
that one method is universally best. The latest snapshot is
`data/preparation/v6/`; earlier counts below are explicitly historical milestones.

## Purpose and scope

Timpla aims to suggest Filipino dishes from ingredients the user already has.
Ingredient detection is a separate task. This workspace prepares recipe data for
an ingredient-constrained ranking model: first establish eligibility, then learn
how to order eligible recipes. A recipe missing an essential ingredient must not
be admitted just because it receives a high ranking score.

**The target is both downloaded datasets in full, not a four-recipe demo.** Four
recipes were used to establish and review the annotation procedure. They remain
part of the full corpus; their review does not make all other records approved.
No model was fitted during this preparation task.

### Training-pipeline preparation check

The existing algorithm is LightGBM LambdaRank, with eligibility checked before
ranking. Its ten features describe inventory use, essential ingredient count,
supporting/optional availability, use-first ingredients, time, and region
preferences. These are candidate features, not experimentally proven optimal
predictors. The existing validation/test evaluation design compares the learned
ordering with an inventory-utilization baseline; no evaluation has been run on
the full corpus.

`python ml/recipe_recommendation/cli.py preflight` defaults to `v6` and verifies snapshot output
hashes, reports recipe annotation gaps, looks for the reviewed training exports,
and checks training-package installation metadata. When supervised files exist,
it invokes only the pure data checks for complete labels, query-group splits,
and stale judgments. It never calls model fitting. A failed preflight is an
expected readiness result rather than a failed training run.

At the latest snapshot, all 2,074 recipes have structured ingredient requirements
and no descriptions remain unresolved. The legacy flat ledger still has 1,781
incomplete recipes because it does not represent the new semantic/alternative
annotations; it is not the current normalization completion metric. There are
2,070 pending role and source-comparison reviews. The full supervised exports do
not exist.
The recommendation environment is Python 3.11 with LightGBM 4.7.0, NumPy 2.4.6,
and scikit-learn 1.9.1. These package versions were checked without model fitting;
the earlier Python 3.9 environment is separate. The
LightGBM ranking API was consulted in the
[official documentation](https://lightgbm.readthedocs.io/en/stable/pythonapi/lightgbm.LGBMRanker.html).

## Step 1. Preserve and inspect the source collections

- **How:** Kept the original CSV/Parquet downloads and their existing provenance
  manifests under `data/external/`. Inspected column names and example records.
- **Reason:** Determine how each collection represents recipes before combining it.
- **Comparative analysis:** Blind concatenation is quick but ignores field and
  separator differences. Inspecting the schema first supports a consistent import.
- **Problem:** The larger CSV has pipe-separated `ingredients`; the filtered CSV
  has newline-separated `full_ingredients`. Their ingredient-name fields also use
  different separators. Parquet and CSV versions of the larger collection are
  representations of the same data, not separate datasets.
- **Solution:** Defined source-specific field and separator settings and imported
  each CSV once. Preserved the dataset collection, original row, and available URL.
- **Why selected / limitation:** This retains traceability while preventing format
  differences from being mistaken for missing data. Publisher license metadata was
  unspecified in the saved source manifests; normalization does not grant rights.

Sources: `joackimagno/FILIPINO_RECIPES_2K` (1,988 rows) and
`joackimagno/filtered-filipino-recipes` (141 rows). Dataset revisions and download
checksums are recorded in `data/external/collections.json` and each manifest.

## Step 2. Clean formatting and conservatively merge duplicates

- **How:** `clean_dataset.py` decodes HTML entities, normalizes Unicode to NFC,
  collapses repeated whitespace, splits ingredient/instruction fields into lists,
  and removes repeated supplied ingredient names within a record.
- **Reason:** Give downstream scripts a predictable structure without discarding
  recipe details.
- **Comparative analysis:** Title-only deduplication can erase distinct versions
  of the same dish. A fingerprint of title, full ingredients, and instructions is
  more conservative, although it misses differently worded duplicates.
- **Problem:** Overlapping collections contain repeated records and recipe variants.
- **Solution:** Used SHA-256 over case-normalized title and ordered ingredient and
  instruction lists. A matching record retains all original source rows.
- **Why selected / limitation:** It reduces exact normalized duplicates without
  assuming every same-title recipe is identical. It is not semantic deduplication.

**Result:** 2,129 source rows; 55 merged duplicate rows; **2,074 retained recipes**.
An earlier external overlap audit used a different comparison and reported 56
matching content records; it is not the duplicate-removal count for this script.

Outputs: `data/processed/recipes.cleaned.json` and `cleaning_report.json`.

## Step 3. Inspect ingredient-list quality and build a vocabulary

- **How:** Counted review flags and ran `build_ingredient_vocabulary.py` over the
  full ingredient lines, retaining each distinct lowercased line and its frequency.
- **Reason:** Discover actual text patterns and prioritize common cases.
- **Comparative analysis:** Using only the supplied `ingredient_names` is simpler,
  but the inspected example omitted ingredients present in the full recipe text.
  Full ingredient lines preserve quantities, forms, and preparation descriptions.
- **Problem:** 1,888 recipes had fewer supplied names than full ingredient lines.
  This is a length-based review hint, not proof that every flagged record is wrong.
- **Solution:** Used full ingredient text as the identity-review starting point,
  while retaining supplied names and original records as reference information.
- **Why selected / limitation:** This avoids silently losing ingredients. The full
  lists themselves still need completeness checks against original recipes.

**Result:** **23,135 ingredient-line occurrences**, representing **12,698 distinct
lines**. Output: `data/processed/ingredient_vocabulary.json`.

## Step 4. Propose consistent ingredient identities

- **How:** `normalize_ingredients.py` removes recognized leading quantities/units
  for lookup, handles selected size and usage phrases, and matches explicit aliases.
  Rules were expanded using the actual unresolved lines reported by the script.
- **Reason:** Connect text such as `1/4 cup soy sauce` and `2 tablespoons soy sauce`
  to `soy_sauce`, so recipes can later be compared with confirmed user ingredients.
- **Comparative analysis:** Exact raw-text matching misses equivalent descriptions;
  broad substring matching may confuse `beef` with `beef powder`. Explicit aliases
  with review give traceable proposals but leave many unfamiliar lines unresolved.
- **Problem:** Amounts, preparation words, English/Filipino names, alternative
  ingredients, and packaging expressions vary considerably.
- **Solution:** Preserve the original line alongside proposed canonical IDs. Keep
  meaningful identities separate, including raw/cooked rice, meat cuts, broth,
  powder, sauce, and ingredient varieties. One line may map to several ingredients
  only when those are jointly required; alternatives require separate handling.
- **Why selected / limitation:** Conservative rules make incorrect broad matches
  easier to avoid and audit. Matching coverage does not measure mapping accuracy.

**Result:** 1,959 distinct lines have proposals, covering **10,889 / 23,135
occurrences (47.07%)**. The other 10,739 distinct lines remain unresolved.
Output: `ingredient_mapping.proposed.json`. These are not training labels.

## Step 5. Review mappings and import approved decisions

- **How:** Exported a 200-row initial review batch and a 25-row recipe-focused
  batch. Recorded `approved_ingredients`, `decision`, and notes in CSV files.
  `import_mapping_review.py` validates and imports approvals with reviewer and UTC
  timestamp provenance. It rejects conflicting existing mappings.
- **Reason:** Keep automatically suggested identities separate from accepted ones.
- **Comparative analysis:** Automatically accepting every proposal is faster but
  hides errors. Independent expert annotation could provide stronger evidence but
  was not performed. This work used project-owner review assisted by Codex.
- **Problem:** A successful text match is not sufficient evidence of correctness.
- **Solution:** Imported 19 initial approvals and 25 pilot approvals. The ambiguous
  `salt and pepper to taste` line remains deferred; it does not explicitly specify
  black pepper. The separate phrase naming ground black pepper was approved.
- **Why selected / limitation:** Decisions have provenance and can be corrected.
  Assistant-supplied mappings and owner acceptance are not independent annotator
  agreement or expert validation; the paper must not describe them as such.

**Historical pilot result:** **44 approved distinct-line mappings**. Initial batch: 19 approved,
1 deferred, 180 blank. Pilot batch: 25 approved. Output:
`data/processed/ingredient_mapping.approved.json`.

## Step 6. Apply approved mappings and annotate ingredient roles

- **How:** `apply_approved_mappings.py` attaches approved IDs to recipe lines and
  marks unmatched lines pending. `prepare_pilot_roles.py` assigns the essential,
  supporting, and optional roles explicitly accepted by Kyle for four recipes.
- **Reason:** Identity answers "what ingredient is this?" Role answers "must this
  ingredient be present for this recipe to qualify?" They are different decisions.
- **Comparative analysis:** A global pantry list is simple but can ignore ingredients
  defining a dish. Recipe-specific roles allow context-dependent requirements, but
  need review for every record and do not themselves approve substitutions.
- **Problem:** Identity normalization alone cannot establish cooking eligibility.
- **Solution:** Preserve every recipe item and require nonoverlapping roles covering
  all mapped ingredients. Validation caught a missing green-bell-pepper role in the
  pork repolyo record; it was corrected to supporting before export.
- **Why selected / limitation:** This prevents accidental omission of known items.
  Supporting ingredients are not automatically optional or known to be in the pantry.
  Missing supporting items must be disclosed and confirmed before a zero-purchase
  claim. Quantities, equipment, and cooking feasibility are not validated here.

**Historical pilot result:** Approved mappings cover **2,460 occurrences (10.63%)**; **four recipes**
have complete mappings and owner-approved roles. The remaining 2,070 retain pending
mapping work. The original four are Tortang Talong, chicken repolyo, pork repolyo,
and the soda version of Halabos na Hipon. This is a reviewed subset of the full data.

## Step 7. Check original recipe lists and record source gaps

- **How:** Codex compared the four ingredient lists against the author's recipe
  cards. `data/source_checks.json` records URLs, comparison scope, dates, source
  author, and a hash of each checked ingredient list.
- **Reason:** Mapping a truncated list perfectly would still produce bad eligibility.
- **Comparative analysis:** Choosing recipes solely because they have short lists
  is quick but can favor incomplete records or references to another prepared dish.
  Original-source comparison provides more evidence of list completeness.
- **Problem:** The larger data contains suspiciously short lists: the inspected
  rosemary/balsamic adobo record listed only oil and garlic; tuna rice omitted rice;
  a cordon bleu record referenced a separate stuffed-chicken recipe.
- **Solution:** Do not invent missing ingredients. Preserve and flag these records.
  Save source evidence only for records actually checked; a suggested URL is not a
  verified source. Alternative versions remain distinct from approved records.
- **Why selected / limitation:** This maintains a traceable quality boundary. Four
  comparisons are agent-assisted ingredient-list checks, not verification of the
  whole corpus, food safety, instructions, or nutrition. Source authors did not
  approve Timpla's ingredient-role assignments.

Compared recipe cards:

- [Basic Tortang Talong](https://panlasangpinoy.com/basic-tortang-talong-recipe/)
- [Ginisang Repolyo with Chicken](https://panlasangpinoy.com/ginisang-repolyo-with-chicken-knr-cc/)
- [Ginisang Repolyo with Giniling](https://panlasangpinoy.com/ginisang-repolyo-with-giniling/)
- [Halabos na Hipon](https://panlasangpinoy.com/halabos-na-hipon-recipe/)

The shrimp source permits a water-based variation. That was recorded as a note;
the existing approved soda recipe was not silently changed to a different version.

## Step 8. Prepare the full corpus and complete review queues

- **How:** `prepare_full_dataset.py` processes **all 2,074 recipes**, merges existing
  approvals and four role reviews into annotations, retains unresolved records,
  and exports complete ingredient, per-recipe role, and source-quality review CSVs.
- **Reason:** Progress the full datasets while showing exactly what is and is not
  suitable for eventual training.
- **Comparative analysis:** Restricting preparation to four recipes gives a small
  workflow exercise but does not satisfy full-corpus preparation. Treating all
  records as ready hides the semantic review gaps. Full processing with explicit
  status fields preserves scope without manufacturing completed annotations.
- **Problem:** Most records remain unreviewed, and source URL coverage is poor.
- **Solution:** Produce a versioned snapshot, input/output SHA-256 manifest,
  reproducible review queues, and machine-readable readiness report. Preserve
  deferred decisions. Refuse to overwrite existing review folders.
- **Why selected / limitation:** It is auditable and scalable across the existing
  corpus. It finishes mechanical preparation, not the semantic annotation work.
  Source-list checks, role decisions, and ranking judgments cannot be inferred from
  the fact that a script ran without errors.

Historical snapshot outputs under `data/preparation/v1/` (current outputs are `v3`):

| Artifact | Purpose | Initial size |
|---|---|---:|
| `recipes.prepared.json` | Every recipe and ingredient mapping/review status | 2,074 recipes |
| `ingredient_review.csv` | Full vocabulary; preserve approvals and deferrals | 12,698 rows |
| `recipe_roles.review.csv` | Per-recipe ingredient identity and role decisions | 23,190 rows |
| `source_quality.review.csv` | Source, cuisine scope, and completeness checks | 2,074 rows |
| `readiness.json` | Counts and remaining training prerequisites | One report |
| `manifest.json` | Input/output hashes and generation provenance | One manifest |

Role rows exceed ingredient-line occurrences because an approved combined line,
such as salt plus black pepper, has a separate role row for each ingredient ID.

**Quality findings:** 1,994 records lack a recorded original recipe URL; 569 have
an `or` expression requiring interpretation; 19 have three or fewer ingredient
lines; one matches the explicit numbered-subrecipe heuristic. These are review
flags, not findings that all such records are invalid. Available source URLs total
80 records after adding the four checked originals. Missing source URLs do not
erase the existing dataset-level provenance.

## Full-corpus automatic pass after the owner review batches

On 29 October 2026 the owner authorized taking over preparation automatically,
with an explicit stop before machine-learning training. The following pass used
the complete vocabulary, not a four-recipe subset or another small review batch.

1. Read all 8,606 lookup groups, their memberships, all 12,698 distinct original
   lines, and the 3,683 previously accepted mappings. Validate that membership
   covers the vocabulary exactly once and matches the saved proposal data.
2. Extend the finite ingredient dictionary and strict handling/measurement rules.
   Use longest matching known identities and accept only recognized remaining
   text. Examples include package-size prefixes, garlic preparation descriptions,
   and explicit ingredient names. Keep source quantities and descriptions intact.
3. Preserve every earlier mapping record and every nonblank owner group decision.
   Leave a conflict with an earlier individual approval unresolved. Keep all 16
   deferred groups. Save recovery copies before replacing the maintained files.
4. Mark newly accepted records with `review_type: automated_rule_acceptance` and
   an automated reviewer identity. These are rule-based decisions authorized by
   the owner, not 2,641 independent human reviews or human relevance labels.
5. Repeat the pass to apply recognized preparation variants of accepted identities.
   The three mutation passes added 2,490, 150, and one distinct mapping respectively.
   A final read-only pass found zero additional safe mappings under these rules.
6. Reapply the accepted mappings to all 2,074 recipes and generate the immutable
   `data/preparation/v3/` snapshot. Preserve `v1` and `v2` as historical outputs.
   Store input/output hashes and provenance; export remaining review worksheets.
7. Run the read-only training preflight and data tests. No fitting, synthetic
   training test, model export, or model inference was performed.

**Reason:** Reduce repetitive identity normalization across the entire dataset
while preserving distinctions needed for ingredient-constrained suggestions.

**Comparative analysis:** Reviewing each quantity variant separately repeats work.
Unrestricted keyword matching can incorrectly turn chicken broth into chicken,
discard a prepared state, or require both sides of an either/or ingredient.
Explicit rules plus a residual review queue cover repeated patterns without
claiming uncertain cases are resolved. They still require rule auditing and
contextual review; they are not evidence of perfect normalization accuracy.

**Problem addressed:** Frequent pantry terms had already been mapped. Remaining
lines contain rarer identities, preparation details, unspecified pepper varieties,
alternatives, and recipe dependencies. Approving a similar number of groups now
adds fewer ingredient occurrences, so percentage gains per batch naturally shrink.

**Solution and why selected:** Run every group through conservative rules, keep
earlier decisions, preserve original text, record automated provenance, and export
exceptions. This fits the existing auditable workflow and avoids manufacturing
training readiness. It is the selected approach for this corpus and constraints,
not an experimentally established universal best method.

Identity normalization does not make quantities, ingredient forms, or substitutions
equivalent. For example, different amounts of raw egg can share the `egg` ID while
their quantities remain separate; boiled egg retains a prepared-state identity.
`chicken_broth` is not chicken meat, and cooked rice is not uncooked rice. Whether
a generic detection satisfies a recipe-specific cut or variety needs a separate
explicit compatibility decision. A complete identity map alone cannot prove the
user has enough ingredients or can cook a recipe without extra purchases.

### Progress history

These milestones are owner-reported import/application results, followed by the
saved automatic-pass result. Repeated terminal output is counted once. Coverage
uses the fixed denominator of 23,135 ingredient occurrences, not recipe count.

| Checkpoint | Accepted individual mappings | Mapped occurrences | Coverage | Fully mapped recipes | Deferred groups |
|---|---:|---:|---:|---:|---:|
| First imported review | 19 | 2,150 | 9.3% | 0 | Not recorded |
| Pilot identities added | 44 | 2,460 | 10.6% | 4 | Not recorded |
| First common lookup groups | 708 | 6,413 | 27.7% | 4 | 2 |
| Following application | Not recorded here | 6,980 | 30.2% | 4 | Not recorded |
| Owner review milestone | 1,231 | 8,468 | 36.6% | 4 | 2 |
| Owner review milestone | 1,521 | 9,239 | 39.9% | 4 | 2 |
| Owner review milestone | 1,986 | 10,504 | 45.4% | 4 | 2 |
| Owner review milestone | 2,612 | 11,508 | 49.7% | 12 | 6 |
| Owner review milestone | 3,050 | 12,144 | 52.5% | 21 | 11 |
| Owner review milestone | 3,416 | 12,641 | 54.6% | 29 | 15 |
| Before automatic takeover | 3,683 | 13,043 | 56.4% | 36 | 16 |
| After first full automatic pass, v3 | 6,324 | 16,063 | 69.43% | 111 | 16 |
| Extended flat normalization, v4 | 8,378 | 18,232 | 78.81% | 259 | 16 |
| Additional shape/physical rules, v5 | 8,646 | 18,505 | 79.99% | 293 | 16 |

At the historical v3 checkpoint, the 6,324 mappings comprised **3,683 owner-recorded mappings plus 2,641
automated rule acceptances**. Combined coverage increased by 13.05 percentage
points using unrounded counts, and 75 more recipes became completely mapped.
This is identity-annotation coverage, not model accuracy, validated recipe
coverage, or overall system completion. The corpus remains 2,074 retained recipes
with all 2,129 source-row references accounted for.

### Historical v3 outputs and unresolved cases

| Artifact | Result / use |
|---|---|
| `data/processed/ingredient_mapping.approved.json` | Maintained accepted mappings, with owner/automated provenance |
| `data/processed/recipes.annotated.json` | Applied mappings for all 2,074 recipes |
| `data/preparation/v3/readiness.json` | Current full-corpus counts and pending work |
| `data/preparation/v3/manifest.json` | Input and output SHA-256 hashes |
| `data/preparation/v3/recipe_roles.review.csv` | 23,219 per-recipe ingredient role rows; unresolved identities remain visible |
| `data/preparation/v3/source_quality.review.csv` | Completeness and cuisine-scope review for all 2,074 recipes |
| `data/automation_runs/20261029T072715921528Z/exceptions.csv` | 6,058 unresolved/deferred lookup groups with reasons and examples |
| `data/automation_runs/20261029T072715921528Z/preservation_audit.json` | Verification against the pre-takeover owner decisions |
| `data/automation_runs/20261029T072715921528Z/preflight.json` | Read-only readiness result; no model fitting |

There are 6,042 pending groups plus 16 owner-deferred groups. The remaining 7,072
unmapped occurrences affect 1,963 recipes. Most remaining groups have no strict
dictionary/rule match; others involve alternatives, unclear references, or
unspecified varieties. A missing rule is not proof that a recipe is invalid.
There are still only four owner-reviewed role assignments and four recorded
source comparisons. No additional roles, source verification, or human ranking
labels were invented to make these statistics look complete.

## Extended normalization and structured requirements: historical v5 result

The owner subsequently requested 100% ingredient normalization. That target has
**not** been reached. Processing every source line is distinct from resolving
its meaning. No unknown text was assigned an arbitrary identity to inflate the
percentage, and no valid record was removed to shrink the denominator.

### Work performed

1. Extended a finite culinary-name lexicon using explicitly selected names found
   in the source vocabulary. Expanded packaging, measurement, shape, and bilingual
   handling rules in `contextual_normalization.py`. Unknown text still fails closed.
2. Retained explicit preparation states as distinct identities when appropriate:
   for example `boiled_chicken` rather than silently accepting raw chicken. A
   state-qualified ID is not approval of interchangeability with another state.
3. Ran the maintained mapping workflow until an additional pass accepted no more
   groups. Recovery copies remain under `data/automation_runs/`; every earlier
   owner record and all 16 owner deferrals remain unchanged.
4. Added `resolve_ingredient_requirements.py` to represent logical ingredient
   requirements. `water or beef broth` is `any_of(water, beef_broth)`, whereas an
   explicitly named cornstarch/water slurry requires both. Shared-head grammar
   preserves broth in `beef or pork broth`; it does not substitute beef meat.
5. Preserved unspecified varieties: plain `pepper` becomes `pepper_unspecified`,
   not an assumed black-pepper identity. These structured resolutions are separate
   from the original deferred group records and carry automated provenance.
6. Checked original quantity-bearing lines and instructions for a limited set of
   contextual cases, such as meat cubes versus seasoning cubes. If evidence did
   not support a complete interpretation, the line remained unresolved.
7. Classified nine non-ingredient occurrences: three `Cooking Procedure` headings
   plus six detached usage/preparation notes. The detached notes retain links to
   the preceding ingredient in their original recipes. Original rows remain intact;
   these occurrences are not counted as successful ingredient identity mappings.
8. Exported structured identities and the exact unresolved queue under
   `data/normalization/v4/`, then built `data/preparation/v5/`. The full snapshot
   retains flat accepted IDs, complete expression trees, original ingredient lines,
   source references, review provenance, and readiness flags.

**Reason / problem:** A flat list cannot faithfully encode either/or requirements,
and a quantity-stripped group can hide whether cubes refer to meat or seasoning.
Malformed source headings and detached notes cannot be treated as food.

**Comparison / selected solution:** Flattening alternatives into a conjunction
would demand extra ingredients. Picking only one option would discard a valid
source alternative. Explicit `any_of`/`all_of` trees preserve the written choice.
Context-aware checks and a residual queue preserve uncertainty rather than hiding
it. This is a suitable representation for later eligibility work; the current
training pipeline still needs reviewed exports that preserve these semantics.

### Statistics at the v5 checkpoint

| Measure | Current v5 result |
|---|---:|
| Recipes / original source-row references retained | 2,074 / 2,129 |
| Distinct source ingredient lines / occurrences | 12,698 / 23,135 |
| Flat accepted mapping entries | 8,646 |
| Owner-recorded / automated flat mapping entries | 3,683 / 4,963 |
| Flat mapped occurrences | 18,505 / 23,135 — 79.99% |
| Recipes with complete flat mappings | 293 |
| Resolved structured ingredient occurrences | 19,345 / 23,135 — 83.62% |
| Distinct resolved ingredient lines | 8,982 |
| Distinct resolved lines containing an either/or choice | 225 |
| Non-ingredient fragments, separately classified | 9 occurrences / 6 distinct lines |
| Unresolved occurrences / distinct lines | 3,781 / 3,710 |
| Recipes with complete structured requirements | 478 |
| Recipes with unresolved requirements | 1,596 |
| Owner-reviewed roles / recorded source comparisons | 4 / 4 |

Flat-map coverage and structured-requirement coverage are different measures.
Neither is model accuracy, independent human validation, or overall project
completion. The 3,710 unresolved lines include ordinary valid ingredients with
unhandled wording, as well as ambiguous or conflicting source descriptions. They
are not all bad recipes. The queue records the original line, occurrence count,
recipe IDs, and recipe examples for contextual resolution.

The v5 readiness report remains `ready_for_training: false`. There has been no
training, no fabricated human relevance label, and no model-performance claim.

Reproduce the structured step and snapshot into unused version folders:

```powershell
.\ml\recipe_recommendation\.venv\Scripts\python.exe ml/recipe_recommendation/resolve_ingredient_requirements.py --output ml/recipe_recommendation/data/normalization/vNEXT
.\ml\recipe_recommendation\.venv\Scripts\python.exe ml/recipe_recommendation/prepare_full_dataset.py --output ml/recipe_recommendation/data/preparation/vNEXT --requirements ml/recipe_recommendation/data/normalization/vNEXT/requirements.json
.\ml\recipe_recommendation\.venv\Scripts\python.exe ml/recipe_recommendation/cli.py preflight --preparation-dir ml/recipe_recommendation/data/preparation/v5
```

Use unused concrete version names in place of `vNEXT`. Do not overwrite existing
review files. `data/normalization/v1` is a superseded development trial, not the
result at that historical checkpoint. Its unresolved queue was
`data/normalization/v4/unresolved.csv`.

## Context-based semantic annotation after the rule-based pass

**Problem and reason:** Strict text rules eventually leave a long tail of valid
ingredient descriptions. Additional regular expressions alone cannot reliably
resolve an unnamed liquid, a detached preparation note, a prepared subrecipe, or
a phrase whose meaning depends on the cooking instructions. Rejecting every
unparsed line would discard usable Filipino dishes; assigning a guessed ID would
hide uncertainty.

**Selected solution:** Freeze the remaining queue and the original inputs, then
annotate every remaining description with its recipe context. The user explicitly
authorized parallel agents on 29 October 2026. Each of three disjoint partitions
contains 893 distinct descriptions. The frozen baseline already resolves 20,376
of 23,135 occurrences (88.1%), separately classifies 21 non-food occurrences, and
leaves 2,738 occurrences across 2,679 descriptions for this semantic pass.

1. Preserve the original ingredient lines, instructions, source-row references,
   accepted owner decisions, and explicit deferrals. Do not overwrite them with
   the new annotations.
2. Read the ingredient wording and the matching recipe's instructions. Prefer an
   existing meaningful identity; create a new identity only for an actual named
   food, form, state, or product. Quantities and preparation details remain in the
   original text even when they are not part of the identity used for retrieval.
3. Keep explicit choices as `any_of` and ingredients needed together as `all_of`.
   Preserve meat cuts, cooking states and named prepared foods. Equipment and
   detached notes remain separately classified; they are not food matches.
4. Use recipe-specific decisions when identical wording refers to different
   ingredients. For example, do not combine chicken and pork cooking liquids into
   a universal meaning of “reserved broth.” Record the basis for contextual
   recovery and retain uncertainty about missing quantities.
5. Distinguish a named food with a questionable bilingual gloss from an absent
   food identity. Preserve the leading source term and flag terminology for
   review; do not create a universal substitution rule. Recipe authors sometimes
   use culinary glosses loosely, as illustrated by the
   [Kawaling Pinoy ingredient glossary](https://www.kawalingpinoy.com/ingredients/).
   This source supports the existence of that usage, not botanical equivalence.
6. Keep genuinely unrecoverable source errors explicit as `source_issue`. They
   block affected recipes rather than being counted as ingredient matches.
7. Validate exact partition coverage, duplicate keys, recipe context membership,
   expression structure, and frozen input hashes before merging. Bind contextual
   annotations to ingredient and instruction hashes so later edits invalidate
   stale interpretations.
8. Save the merged requirements, identity registry, source-issue queue, metrics,
   and input/output hashes in a new versioned snapshot. AI semantic annotations
   remain identified as AI annotations; they are not attributed to Kyle or called
   independent human validation.

**Comparison with alternatives:** Leaving all decisions to the original strict
parser preserves conservatism but stalls on valid wording. Fuzzy matching alone
can confuse broth with meat, raw with cooked rice, or an ingredient choice with a
conjunction. Manual transcription of all 23,135 occurrences repeats work already
captured by exact mappings. A frozen semantic review of the remaining descriptions
adds context only where the rules were insufficient, retains the earlier work,
and makes unresolved evidence visible. This is the selected practical approach
for this corpus; its superiority has not been established by a controlled
annotation-accuracy experiment.

**Percentage definitions:** Ingredient identity resolution counts resolved food
occurrences. Review disposition counts all occurrences given a specific outcome,
including non-food notes and source problems. A 100% disposition therefore does
not mean 100% ingredient matching, human agreement, model accuracy, or training
readiness. Recipe roles, source completeness, cuisine scope, and supervised
ranking labels are separate preparation gates.

### Final semantic snapshot: v6, 30 October 2026

All three partitions were completed, cross-checked and merged. Concrete
cross-check corrections included retaining coconut palm **heart** rather than a
whole palm, treating recommended fish cuts/species as preferences, avoiding an
invented mixed-chicken-parts requirement, retaining the headless state of steamed
shrimp, and applying the dried-fish state to both explicitly offered fish options.
An explicit ID-alignment ledger reconciles synonymous names and singular/plural
spellings in the new annotations; original semantic decisions and previous
accepted records are retained.

| Measure | Verified v6 result |
|---|---:|
| Original source-row references retained | 2,129 / 2,129 |
| Cleaned recipes represented | 2,074 / 2,074 |
| Original distinct ingredient descriptions accounted for | 12,698 / 12,698 |
| Original ingredient-line occurrences accounted for | 23,135 / 23,135 — 100% |
| Food-ingredient occurrences resolved | 23,094 / 23,094 — 100% |
| Non-food headings, equipment and notes | 41 occurrences |
| Food identities as a share of all source occurrences | 99.82% |
| Unresolved descriptions / occurrences | 0 / 0 |
| Recipes with complete structured ingredient representations | 2,074 / 2,074 |
| Terminology flags retained | 93 occurrences across 80 recipes |
| Previous nonpending structured resolutions preserved | 10,019 |
| Owner-recorded flat decisions preserved | 3,683 |
| Recipes with owner-reviewed roles / recorded source comparisons | 4 / 4 |
| Model training performed | No |

The 100% figure describes **ingredient normalization coverage**. It does not
certify recipe completeness, Filipino cuisine scope, ingredient compatibility,
role assignments, ranking-label quality, or model performance. There are no
`source_issue` outcomes left in this normalization pass, but the 93 terminology
flags and earlier source-quality flags still require recipe review. AI semantic
annotations are clearly identified and are not independent human approvals.

Current artifacts are `data/normalization/v6/ingredient_requirements.json`,
`identity_registry.json`, `terminology_review.json`, `report.json` and
`manifest.json`, together with `data/preparation/v6/`. The legacy flat mapping
ledger remains at 79.99%; no either/or choice was flattened just to change that
number. Use the structured snapshot for the current completion figures.

Reproduce into unused folders without running training:

```powershell
.\ml\recipe_recommendation\.venv\Scripts\python.exe ml/recipe_recommendation/merge_semantic_review.py --output ml/recipe_recommendation/data/normalization/vNEXT
.\ml\recipe_recommendation\.venv\Scripts\python.exe ml/recipe_recommendation/prepare_full_dataset.py --output ml/recipe_recommendation/data/preparation/vNEXT --requirements ml/recipe_recommendation/data/normalization/vNEXT/ingredient_requirements.json
.\ml\recipe_recommendation\.venv\Scripts\python.exe ml/recipe_recommendation/cli.py preflight --preparation-dir ml/recipe_recommendation/data/preparation/vNEXT
```

The frozen review folder is named `review_20261029` because review began on
29 October. The final v6 snapshot and completion documentation were saved on
30 October. `vNEXT` must be replaced with a new unused version name.

The final preservation audit is
`data/automation_runs/20261030T003033637120Z/preservation_audit.json`.
It verifies both snapshot manifests and their input/output hashes, all 3,683
pre-takeover owner mapping records, all 615 previous nonblank group decisions
(including 16 deferrals), every original ingredient line, and all 2,129 source-row
references. The same folder contains `preflight.json`: zero incomplete ingredient
representations, 2,070 pending role reviews, 2,070 pending source comparisons,
and missing supervised training exports. These pending gates are preserved rather
than filled with fabricated reviews or judgments.

Validation on 30 October: **37 non-training tests passed**, covering normalization,
alternatives, context staleness, full-corpus retention, ID alignment, review
provenance, eligibility and split leakage. Expo lint and TypeScript type checking
also passed. No test that fits LightGBM and no training command was run.

## Step 9. Work remaining before training — not completed

1. Review the retained terminology flags and verify annotation quality without
   overwriting original owner decisions. Ingredient normalization coverage is now complete.
2. Find/check original recipe lists where possible. Confirm Filipino cuisine scope;
   retain exclusion reasons for out-of-scope, incomplete, or unusable records.
3. Approve recipe-specific roles and explicitly represent alternatives or prepared
   subrecipes. Resolve vocabulary compatibility without equating every generic
   detection with every specific cut, variety, or prepared state.
4. Assemble realistic confirmed-inventory queries. Constructed research scenarios
   must be labeled as such; they are not observed user behavior.
5. Assign related/identical inventories to one split before labeling/model fitting.
   Maintain separate training, validation, and test groups.
6. Collect human relevance judgments for eligible query–recipe pairs, with reviewer
   provenance. The existing ranker uses 0–3 judgments and requires informative
   groups with multiple eligible candidates and differing ratings.
7. Validate complete label coverage, no stale judgments, no group leakage, and no
   missing essential ingredients admitted by ranking. Then consider training.

The four reviewed recipes do not provide enough variety to support claims about a
general Filipino recipe recommender. No full-corpus ranking examples or relevance
labels were fabricated to make the data appear ready. No training, ranking-model
accuracy, recommendation accuracy, or zero-waste benefit was measured in this task.

## Reproduction and review-file handling

From the project root, use the existing Python environment. These preparation
scripts use Python's standard library; no additional training packages are needed.

```powershell
python ml/recipe_recommendation/clean_dataset.py
python ml/recipe_recommendation/build_ingredient_vocabulary.py
python ml/recipe_recommendation/normalize_ingredients.py
```

The above regenerate derived files; they do not perform review. Preserve completed
review CSVs and approved mappings before changing rules or regenerating data.
Exporters refuse to overwrite existing review files.

```powershell
python ml/recipe_recommendation/import_mapping_review.py --reviewer "Kyle"
python ml/recipe_recommendation/import_mapping_review.py --reviewer "Kyle" --review-file "ml/recipe_recommendation/data/processed/ingredient_review.pilot.csv"
python ml/recipe_recommendation/apply_approved_mappings.py
python ml/recipe_recommendation/prepare_pilot_roles.py
python ml/recipe_recommendation/prepare_full_dataset.py --output "ml/recipe_recommendation/data/preparation/vNEXT"
```

Replace `vNEXT` with an unused version folder when new review decisions warrant
regeneration; the current snapshot is already saved in `v6`. Use a new snapshot
folder to preserve previous work. Ingredient approvals in the
full queue can be imported with the existing `--review-file` option only after
appropriate reviewer provenance is supplied; do not attribute someone else's
reviews to yourself. The full role/source queues are review worksheets, not yet
automatic training inputs. Their import/adjudication must be implemented when
decisions are available. Do not fill missing roles or labels to bypass checks.

Targeted validation (does **not** train a model):

```powershell
python -m unittest discover -s ml/recipe_recommendation/tests -p test_full_preparation.py -v
python -m unittest discover -s ml/recipe_recommendation/tests -p test_ranker.py -v
```

Tests check record/source retention, nonpromotion of proposals to approvals,
stale source comparisons, incomplete vocabulary, role overlap, and the existing
ranking pipeline's eligibility, label-provenance, and split-leakage protections.
