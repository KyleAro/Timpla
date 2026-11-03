# Timpla recipe recommendation: start-to-finish build guide

Updated: 30 October 2026. Run commands in PowerShell from the Timpla project root.

This is the single working guide for finishing the recipe recommender. It includes
the existing implementation, the remaining implementation gaps, the data you must
prepare, the training command, and the integration and evaluation steps.

## 1. Lock the behavior

The flow is:

**YOLO detection → user corrects/adds ingredients → eligibility filtering →
LightGBM ranking → real Filipino recipe suggestions.**

- Recommend dishes using the user's confirmed inventory.
- Missing essential ingredients make a recipe ineligible.
- Supporting ingredients are displayed and their availability confirmed. Do not
  assume oil, seasonings or sauces are available or free.
- Optional ingredients can be omitted when the source supports that omission.
- No automatic shopping suggestions or invented recipes.
- Preserve quantities and ingredient states. Ingredient detection alone does not
  establish how much food is available.
- Allow an empty result and let the user correct their inventory.

**Done when:** These rules are agreed and implemented consistently in filtering,
training examples, API responses and the app.

## 2. Understand the current starting point

You already have:

| Item | State |
|---|---|
| Raw source records | 2,129 retained |
| Cleaned recipes | 2,074 |
| Source ingredient-line occurrences | 23,135 |
| Normalized food occurrences | 23,094 represented |
| Non-food notes/equipment/headings | 41 classified separately |
| Latest normalization | `ml/recipe_recommendation/data/normalization/v6/` |
| Latest full preparation snapshot | `ml/recipe_recommendation/data/preparation/v6/` |
| Step 4 draft roles for the full corpus | `ml/recipe_recommendation/data/recipe_review/v1/recipes.draft.json` |
| Detailed Step 4 semantic reviews | Partial checkpoints; check actual files before counting completion |
| Existing owner-approved role records | Four preserved |
| Training implementation | `ml/recipe_recommendation/ranker.py` |
| Command interface | `ml/recipe_recommendation/cli.py` |
| Full-corpus trained ranker | Not yet produced |

Normalization coverage is not an accuracy score. Step 4 has already found cases
where a normalized ID needs correction. Those cases must be resolved before use.
Do not restart cleaning or discard the saved reviews. Work forward from these
snapshots, using new version folders for corrections.

**Important:** The CLI defaults to an old six-recipe seed catalog. The training
commands below explicitly select your full reviewed export instead.

## 3. Check the Python environment

Use the recommendation environment, rather than the older Python 3.9 environment:

```powershell
$py = ".\ml\recipe_recommendation\.venv\Scripts\python.exe"
& $py --version
& $py -c "import lightgbm, numpy, sklearn; print(lightgbm.__version__, numpy.__version__, sklearn.__version__)"
```

If this environment is missing, create it once:

```powershell
py -3.11 -m venv ml/recipe_recommendation/.venv
$py = ".\ml\recipe_recommendation\.venv\Scripts\python.exe"
& $py -m pip install -r ml/recipe_recommendation/requirements.txt
```

**Done when:** Imports succeed. No GPU or YOLO retraining is required to train this
tabular recipe ranker.

## 4. Finish recipe-level review

For every retained recipe, check the ingredient list against its own instructions
and record:

1. **Cuisine scope:** Filipino dish/adaptation, out of scope, or uncertain.
   Established Filipino adaptations can qualify; a foreign name alone is not an
   exclusion rule. Dataset membership alone is not proof of Filipino scope.
2. **Completeness:** No obvious internal gap, a specific gap, or uncertain.
   Record missing ingredients and conflicting states. Serving rice alongside a
   dish does not automatically make rice a missing ingredient of the dish.
3. **Roles:** Essential, supporting, or explicitly optional for that variant.
4. **Dependencies:** Ingredients made during preparation, reserved cooking liquids,
   and prepared subrecipes. These should not become unexplained extra purchases.
5. **Source evidence:** Preserve actual URLs and existing comparisons. Do not
   substitute a dataset URL for an original recipe URL or invent a source check.

Examples of role reasoning:

- Basic Tortang Talong needs eggplant and egg.
- Adobo's listed soy sauce/vinegar can be defining ingredients, not universally
  optional condiments. Respect variants that explicitly use different bases.
- A source saying “extra wings if desired” does not make the main chicken optional.
- A recipe's explicit alternatives remain alternatives, rather than all becoming
  mandatory ingredients.

Current review input and policy:

```text
ml/recipe_recommendation/data/recipe_review/v1/REVIEW_POLICY.md
ml/recipe_recommendation/data/recipe_review/v1/partition_01.json
ml/recipe_recommendation/data/recipe_review/v1/partition_02.json
ml/recipe_recommendation/data/recipe_review/v1/partition_03.json
```

Each partition has a matching `.decisions.json` output. Some outputs are partial.
Only after all assigned recipes have actual decisions, merge into an unused folder:

```powershell
& $py ml/recipe_recommendation/merge_recipe_review.py --output ml/recipe_recommendation/data/recipe_review/v2
```

The merger rejects incomplete partitions and preserves prior owner decisions.
It produces role worksheets, scope/completeness issues and an explicit
compatibility-policy proposal. AI proposals remain AI proposals; reviewer names
and approvals must reflect the work actually performed.

If manual review is used instead, record the same information for every recipe;
completing the agent pipeline is not itself a requirement of machine learning.

**Done when:** Every recipe has a usable reviewed disposition. Keep excluded or
pending records with reasons. Correct material identity errors and gaps, or keep
affected records out of training/serving with an explicit audit trail.

## 5. Close the export and eligibility implementation gap

**This implementation is still required before full-corpus training.** The current
ranker accepts flat `major`, `supporting`, and `optional` lists, while the normalized
corpus also contains `any_of`, `all_of`, and derived-ingredient relationships.

Implement an exporter from the reviewed corpus and extend eligibility/features
where required:

- `all_of`: require each essential component.
- `any_of`: accept a source-approved available branch; do not require every option.
- Preserve role assignments within compounds and choices.
- Define exact aliases separately from substitutions and transformations.
- Do not equate every generic chicken detection with every chicken cut, or raw
  rice with cooked rice. Ask for clarification or explicitly support a reviewed
  preparation operation when appropriate.
- Resolve dependencies on prepared ingredients before treating a dish as cookable.
- Preserve source exclusions and pending-review reasons in an export audit.

Do not flatten an OR expression into a mandatory ingredient list just to satisfy
the existing trainer. Either extend the ranker to consume the structured schema,
or use a reviewed representation that preserves the same meaning. If the schema
changes, update validation, features, context fingerprints, inference and model
metadata together.

Create a new full-corpus export directory:

```text
ml/recipe_recommendation/data/training/full_v1/
  recipes.training.json
  aliases.json
  queries.review.json
  relevance.review.csv
  export_audit.json
```

Those full-corpus files do not exist yet. They must be produced from reviewed
records; renaming the draft JSON is insufficient.

For flat records compatible with the current code, the recipe format is:

```json
{
  "id": "stable-recipe-id",
  "name": "Reviewed recipe name",
  "source_url": "https://actual-original-source.example/recipe",
  "major": ["canonical_essential_ingredient"],
  "supporting": ["canonical_supporting_ingredient"],
  "optional": [],
  "minutes": null,
  "region": "Filipino",
  "reviewed_by": "Actual reviewer",
  "reviewed_at": "Actual review date"
}
```

This is a schema illustration, not a valid training record. Replace it with real
reviewed facts. The current validator requires a genuine HTTPS source URL. For
records without an original URL, either recover it or implement an explicit
dataset-row provenance schema and update validation deliberately. Never invent
URLs or silently remove most of the corpus because URLs are missing.

**Done when:** The usable reviewed corpus exports without losing choices,
provenance or source records. Every excluded recipe has a reason. Eligibility
works on the exported representation before training starts.

## 6. Prepare inventory scenarios

Each scenario represents ingredients a user confirms they have. Include varied
proteins, vegetables, eggs, cooked rice, pantry availability, small inventories,
use-first ingredients, exclusions and cases with no suitable dishes.

Planning target: start with several hundred independently reviewed scenarios,
then expand according to coverage and evaluation results. This is a proposed
research target, not a measured minimum for model quality.

Example scenario shape:

```json
{
  "id": "inventory-001",
  "available": ["egg", "cooked_rice", "garlic", "cooking_oil", "salt"],
  "use_first": ["cooked_rice"],
  "excluded": [],
  "max_minutes": 30,
  "preferred_region": "Filipino",
  "split": "train",
  "leakage_group": "rice-egg-inventory-family-001",
  "origin": "constructed research scenario",
  "reviewed_by": "Actual reviewer"
}
```

Use IDs from your exported alias vocabulary, not inconsistent spellings. Mark
constructed scenarios honestly; do not call them observed user behavior.

**Done when:** Scenario coverage includes the usable catalog and intended user
situations. Track coverage, rather than using only the same few dishes.

## 7. Assign splits before fitting

Use independent inventory families for train, validation and test. A reasonable
initial allocation is approximately 70% / 15% / 15% of families; adjust if the
number of independent groups makes those splits uninformative.

- Identical inventories stay in one split.
- Closely related variations share a `leakage_group` and stay together.
- Use-first variations of the same inventory stay together.
- Do not randomly split individual recipe-candidate rows.
- Keep test labels untouched during feature/parameter decisions.

This design evaluates new inventory queries against the catalog. It does not
establish generalization to unseen recipe families unless you add that experiment.

## 8. Create relevance labels—the ranking supervision

Ingredient roles establish eligibility. **Relevance judgments teach the model
which eligible recipes to rank higher.** Recipe JSON alone does not supply these
judgments.

After the full export and eligibility changes are ready, set the file paths:

```powershell
$recipes = "ml/recipe_recommendation/data/training/full_v1/recipes.training.json"
$aliases = "ml/recipe_recommendation/data/training/full_v1/aliases.json"
$queries = "ml/recipe_recommendation/data/training/full_v1/queries.review.json"
$labels = "ml/recipe_recommendation/data/training/full_v1/relevance.review.csv"
```

Audit and generate a blank label queue using the existing CLI:

```powershell
& $py ml/recipe_recommendation/cli.py --recipes $recipes --aliases $aliases audit
& $py ml/recipe_recommendation/cli.py --recipes $recipes --aliases $aliases review-queue --queries $queries --output $labels
```

Do not overwrite an existing label file. Use a new version after changing recipe
requirements, queries or compatibility rules.

Rate every eligible candidate for each ranking scenario:

| Relevance | Meaning |
|---|---|
| 0 | Unsuitable for this situation |
| 1 | Weak suggestion |
| 2 | Useful suggestion |
| 3 | Highly useful suggestion |

Record `reviewer` and reasons. Consider useful inventory consumption, supporting
availability, use-first items and time preferences. Do not automatically convert
ingredient-overlap percentages into “human” labels.

The current trainer requires each ranking query to have at least two eligible
candidates, different ratings, and at least one rating of 2 or 3. Keep zero- and
single-candidate inventories as eligibility/integration tests; they cannot form
informative pairwise ranking groups under the current implementation. Do not
force ratings apart merely to pass validation.

**Done when:** Labels are complete, genuine, current and informative in every split.

## 9. Validate before training

Existing full-preparation check:

```powershell
& $py ml/recipe_recommendation/cli.py preflight --preparation-dir ml/recipe_recommendation/data/preparation/v6
```

It currently reports pending reviews and missing full supervised exports. That is
a readiness result. Once the final full export is implemented, regenerate a new
preparation snapshot with its actual reviewed files and point preflight there.
Do not edit a saved readiness JSON to make it pass.

Validate the exported files with the current pure-data training validator:

```powershell
@'
import sys
from pathlib import Path
sys.path.insert(0, "ml/recipe_recommendation")
from ranker import read_json, training_groups
p = Path("ml/recipe_recommendation/data/training/full_v1")
groups = training_groups(
    read_json(p / "recipes.training.json"),
    read_json(p / "queries.review.json"),
    p / "relevance.review.csv",
    read_json(p / "aliases.json"),
)
print({split: len(rows) for split, rows in groups.items()})
'@ | & $py -
```

Update this validation entry point if you extend the representation in Step 5.
Check no missing essentials admitted, no OR-to-AND loss, no stale labels, no
cross-split inventory leakage, complete coverage and accurate reviewer provenance.

Run relevant non-training tests individually:

```powershell
& $py -m unittest discover -s ml/recipe_recommendation/tests -p test_ranker.py -v
& $py -m unittest discover -s ml/recipe_recommendation/tests -p test_recipe_review.py -v
```

Avoid a blanket test-discovery command before you intend to fit anything: this
workspace also contains a training test.

**Done when:** Real reviewed input validation and meaningful tests pass.

## 10. Train LightGBM LambdaRank

Why this model: the task is ordering eligible catalog recipes using structured
inventory/recipe features. The existing implementation uses a small gradient-
boosted ranking model that can run on CPU. It is a reasonable starting model,
not an experimentally established best model for this dataset.

| Alternative | Difference / reason not selected as the starting learned ranker |
|---|---|
| Ingredient-overlap sorting | Useful baseline; no learned preference ranking |
| Ordinary recipe classification | Predicts classes rather than ordering eligible candidates for each inventory |
| Collaborative filtering | Needs meaningful user interaction history, which this project has not collected |
| Neural/transformer ranker | Adds data and implementation demands before we have evidence it improves this task |
| Recipe-generating LLM | Generates text rather than ranking the verified catalog; harder to enforce ingredient constraints |

The current ten features describe inventory utilization, major ingredient count,
supporting availability/missing count, optional availability, use-first coverage,
time, unknown time, time preference and region preference. Keep these aligned
between training and inference when extending structured eligibility.

When all prior gates pass, **you run**:

```powershell
& $py ml/recipe_recommendation/cli.py --recipes $recipes --aliases $aliases train --queries $queries --labels $labels --output ml/recipe_recommendation/models/full_v1
```

Current outputs:

```text
models/full_v1/ranker.txt
models/full_v1/metadata.json
models/full_v1/evaluation.json
```

The trainer validates data, trains on train groups, uses validation for early
stopping and reports validation/test metrics plus an inventory-utilization
baseline. It refuses to overwrite an existing model folder and rejects a model
that learns no ranking splits.

**Done when:** A genuine fitted model and its metadata/evaluation artifacts exist.

## 11. Evaluate and decide whether to use the model

Inspect `evaluation.json`:

- **NDCG@5:** Quality of the ordering against the relevance labels.
- **Precision at up to 5:** Fraction rated useful/highly useful among returned
  suggestions. The current code uses fewer than five when fewer candidates exist.
- **Inventory-utilization baseline:** The comparator already implemented.
- Query counts and performance across diverse inventory families.

Also measure essential-ingredient violation count (target zero), empty-result
frequency, catalog coverage, latency, and failures by ingredient/dish family.
These additional slice/coverage/latency reports still need implementation.

Use validation to decide changes. If the learned model does not improve on the
baseline on the chosen criteria, report that result and investigate labels,
coverage and features. Do not repeatedly tune against the held-out test set.
Ranking scores are not detection confidence, probability, or model accuracy.

**Done when:** Evaluation supports the chosen behavior and limitations are recorded.

## 12. Test inference from the command line

After training, use the same recipe export and aliases:

```powershell
& $py ml/recipe_recommendation/cli.py --recipes $recipes --aliases $aliases recommend --model ml/recipe_recommendation/models/full_v1 --ingredients egg cooked_rice garlic cooking_oil salt --limit 5
```

Use actual exported IDs; this sample inventory does not guarantee any particular
dish exists or is eligible. Test missing essentials, only supporting ingredients,
empty inventory, unknown ingredients, alternatives, exclusions and no matches.

The current predictor checks the catalog/alias fingerprint against model metadata.
Changing those files requires a compatible version/retraining, not ignoring the
fingerprint error.

## 13. Implement the recommendation API

This endpoint is still to be built/connected for the full trained recommender.
Use the existing Python backend rather than putting LightGBM inside Expo.

Proposed endpoint: `POST /recommendations`.

Request fields: confirmed `available`, `use_first`, `excluded`, `max_minutes`,
`preferred_region`, and a bounded result `limit`.

Implementation sequence:

1. Load the versioned model, reviewed catalog and aliases once at server startup.
2. Validate and normalize the request.
3. Apply eligibility and explicit ingredient constraints before prediction.
4. Rank eligible candidates using the trained model.
5. Return recipe IDs/names, source/provenance, available essential ingredients,
   missing supporting ingredients, optional items, quantity/preparation checks,
   ranking score and model version.
6. Return an empty list with a clear reason when nothing qualifies.
7. Return consistent JSON errors; log server details without exposing them to users.

Use the dependency and transformation rules reviewed in Step 5. Do not claim
“ready to cook without buying anything” while required supporting items remain
unconfirmed.

**Done when:** API tests cover real model inference and invalid/empty requests.

## 14. Connect the Expo application

Before writing Expo/React Native code, follow the repository's AGENTS.md:
read the installed Expo major and its matching versioned documentation.

1. Send the user's edited/confirmed ingredient inventory to the recommendation API.
2. Refetch when the user adds/removes ingredients; discard stale responses.
3. Show recipe cards, required supporting items and source links.
4. Separate “candidate needs confirmation” from “all required items confirmed.”
5. Add loading, empty, retry and server-error states.
6. Use an API address reachable by the phone; test on the actual iOS/Android
   device and network used for the demonstration.
7. Keep detector confidence separate from recommendation ranking scores.

Run app lint/type checking and end-to-end tests. Verify that recipe suggestions
actually come from the trained model and current inventory, rather than placeholders.

## 15. Final acceptance and paper documentation

- [ ] Full source corpus accounted for; retained/excluded/pending totals reconcile.
- [ ] Material normalization and completeness issues resolved or explicitly held out.
- [ ] Filipino scope and recipe roles reviewed with actual provenance.
- [ ] Alternatives/dependencies survive export and inference.
- [ ] Supporting items and quantities are disclosed/confirmed appropriately.
- [ ] Inventory scenarios and genuine relevance labels cover the intended task.
- [ ] Related inventory families do not leak across train/validation/test.
- [ ] Trained model, catalog, aliases, parameters and input hashes are versioned.
- [ ] Held-out evaluation and baseline comparison are saved without invented results.
- [ ] API and physical-phone flow work, including empty/error cases.
- [ ] Paper describes cleaning, normalization, role annotation, label collection,
  splits, features, model choice, baseline, metrics, limitations and actual counts.

Do not claim measured zero waste, zero cost, user satisfaction or recommendation
accuracy unless an evaluation actually measured those outcomes.

## Working rule to prevent more detours

Follow the numbered completion gates in order. Reopen an earlier stage only for a
specific discovered defect. Keep one current version of each final artifact and
preserve previous versions as history. Do not add another parser, review batch,
model or app feature unless it closes a documented gap in this guide.

The immediate next deliverable is **the reviewed full-corpus recipe export with
correct eligibility semantics**. After that, prepare the inventory/relevance data,
validate, train, evaluate, and integrate—in that order.
