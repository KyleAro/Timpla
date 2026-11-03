# Timpla recipe recommendation: development roadmap

Updated: 30 October 2026, Asia/Manila.

This is the working sequence from data preparation to an evaluated recommender
integrated with the app. Follow the current step to its completion condition before
moving to the next. Existing scripts may be consolidated or corrected; adding a
new script, CSV, or model is not itself progress toward the next checkpoint.

## Finished product

The user scans or enters ingredients, corrects the inventory, and receives ranked
Filipino recipe suggestions based on what is available. Missing essential
ingredients exclude a recipe. Supporting ingredients must be disclosed and their
availability confirmed before presenting a dish as cookable without purchases.
Users can add ingredients they forgot. The model ranks real catalog entries and
does not generate invented recipes.

The target is the full usable Filipino recipe corpus from both downloaded
collections. Every source record must remain accounted for. A record may be
excluded from training or serving only with a recorded reason, such as an
incomplete list that cannot be resolved, unsuitable scope, or an unresolved
dependency on a separate prepared recipe. Full scope does not mean silently
training on invalid records.

## Current checkpoint

- All 2,129 source rows are accounted for in 2,074 cleaned recipes, containing
  23,135 ingredient occurrences and 12,698 distinct lines.
- Flat accepted mappings: **8,646** (3,683 owner-recorded plus 4,963 automated),
  covering **18,505 / 23,135 occurrences (79.99%)**; 293 completely mapped recipes.
- Structured requirements preserve either/or alternatives and unspecified types:
  **23,094 / 23,094 food occurrences resolved (100%)**, with all **2,074 recipes**
  represented. The other **41 occurrences** are separately classified non-food
  headings, equipment, or notes. Zero descriptions remain unresolved.
- All **12,698 distinct descriptions / 23,135 occurrences** are accounted for.
  Food identities represent 99.82% of all source occurrences because the source
  includes non-food entries. These figures measure annotation coverage, not
  independent human validation or overall ML readiness.
- **93 terminology flags across 80 recipes** remain visible for the recipe/source
  review stage. New annotations retain explicit AI provenance.
- The legacy group ledger has 4,694 accepted groups, 16 original deferrals, and
  3,896 pending groups. The structured resolver handles some of those cases
  separately; the two ledgers have different representations and counts.
- Four recipes have owner-reviewed roles and recorded assistant source checks;
  three constructed inventory scenarios are still drafts without approved labels
  or split assignments. No training-ready full-corpus export exists.
- Latest snapshot: `data/preparation/v6/`. Structured identities, identity registry,
  and terminology queue: `data/normalization/v6/`. Earlier snapshots are preserved.
- Python 3.11 recommendation environment has LightGBM 4.7.0, NumPy 2.4.6, and
  scikit-learn 1.9.1. Tests cover ingredient logic and provenance without fitting.
- No model has been trained. Ingredient normalization is complete at the AI
  annotation stage; current work moves to **Step 4**.

## Step 1 — Lock the requirements and scope

**Status:** Agreed.

Actions:

1. Focus on Filipino recipes using the user's confirmed inventory.
2. Keep the detector and recipe recommender as separate components.
3. Use essential-ingredient eligibility followed by learned ranking.
4. Start with the existing LightGBM LambdaRank implementation and retain a simple
   ingredient-based baseline for comparison. Change the choice only for a concrete
   problem or evaluation evidence.

**Done when:** These requirements guide the data, labels, model, and app behavior.
Do not add recipe generation, shopping recommendations, or a new detector to this
workstream.

## Step 2 — Import and clean both datasets

**Status:** Completed for the current downloads.

Actions: Preserve raw downloads and provenance; standardize field structure and
separators; clean text formatting; merge only records matching the chosen
fingerprint; retain their original source rows.

**Done when:** Both collections are imported once, original records are traceable,
and the cleaning report reconciles 2,129 source rows to 2,074 retained recipes.
Reopen this step only if a concrete parsing error or new source revision appears.

## Step 3 — Finish ingredient normalization across the corpus

**Status:** Complete at the AI annotation stage; terminology/quality checks carry
forward to the recipe review stage. No independent human validation is claimed.

Actions:

1. Use the saved structured `v6` report as the current baseline. The new semantic
   annotations and preparation snapshot agree; no legacy group import is needed.
2. Keep existing approvals, automated provenance, and deferred cases. The
   `finish_normalization.py` pass inspected every group and reached convergence:
   another pass accepts zero new mappings under the current rules.
3. The final semantic pass resolved or classified all 2,679 remaining descriptions
   in the frozen queue after rule expansion. Original wording, recipe context,
   provenance and earlier decisions are retained. Alternatives remain choices;
   meaningful cuts and cooking states remain separate.
4. Preserve ingredient forms and distinctions that affect suitability: meat cuts,
   cooked/raw states, sauces versus their base ingredients, alternatives versus
   jointly required ingredients. Record confidence/review provenance.
5. Track unresolved lines per recipe. Do not assume that automatically recognized
   text has been validated, or that unknown lines can be dropped.

**Done when:** Every ingredient line in each recipe intended for training/serving
has a defensible, traceable representation. Unresolved records remain pending or
have a documented exclusion. Coverage is reported separately for proposals and
approved mappings. A percentage alone is not the completion condition.

## Step 4 — Validate recipe completeness and annotate requirements

**Status:** Four reviewed; full corpus pending.

Actions:

1. Review Filipino-cuisine scope, short/suspicious lists, source provenance,
   alternatives, references to prepared subrecipes, and the 93 terminology flags
   across the corpus.
2. Record source evidence where available; distinguish an original recipe URL
   from the dataset download URL. Do not guess missing ingredients or claim a
   source was checked when it was not.
3. Assign essential, supporting, and optional roles per recipe. Use explicit
   criteria and review uncertain cases rather than treating all seasoning as
   universally optional.
4. Define ingredient compatibility separately from identity. Generic chicken must
   not automatically satisfy every cut, and raw rice must not satisfy cooked rice.
5. Store approved changes and exclusion reasons, and regenerate a versioned
   preparation snapshot without overwriting review work.

**Done when:** Every retained recipe used by the model has reviewed requirements,
no unexplained missing ingredients, and a recorded completeness/scope decision.
Every other source record remains accounted for with pending/excluded status.

## Step 5 — Build and label inventory-to-recipe examples

**Status:** Three draft scenarios only; no full labeling set.

Actions:

1. Prepare realistic inventories reflecting the recipe collection and intended
   users, including different proteins, vegetables, pantry availability, and
   ingredients marked use-first. Label constructed scenarios as constructed.
2. Retrieve candidates from the entire approved catalog using essential-ingredient
   rules, not only the four recipes used during early review.
3. Obtain reviewer judgments using the existing scale: 0 unsuitable, 1 weak,
   2 useful, 3 highly useful. Preserve context hashes, reviewer identity, and notes.
4. Ensure ranking groups contain multiple eligible recipes and informative
   differences in judgment. An inventory with one eligible dish is a useful
   eligibility test, but not an informative pairwise ranking group.
5. Audit recipe and scenario-family coverage; avoid letting only common pantry
   ingredients or four dishes dominate the training examples. Do not manufacture
   human labels from an ingredient-overlap formula.

**Done when:** The usable full catalog is represented in the example/coverage
audit; training pairs have complete reviewed judgments; every label refers to the
current recipe requirements and query. Recipe count and labeled-query count are
reported separately. More recipes alone do not create ranking supervision.

## Step 6 — Finalize train, validation, and test partitions

**Status:** Pending.

Actions: Group identical and closely related inventories before final split
assignment; keep each family in one split; retain an untouched test set and tune
on validation only. Scenarios differing only in use-first priority stay together.
Choose and record a split allocation appropriate to the number of independent
groups, rather than splitting individual candidate rows at random.

**Done when:** All three splits contain informative reviewed groups, there are no
cross-split inventory-family duplicates, and labels pass provenance checks. This
evaluates new inventories against the catalog; it does not establish performance
on previously unseen recipe families unless separately designed to do so.

## Step 7 — Finalize features, baseline, and evaluation targets

**Status:** Existing implementation available; validation with full data pending.

Actions:

1. Use the existing features for inventory use, supporting availability, use-first
   coverage, time, and preferences. Document missing values and remove unsupported
   or uninformative features based on training/validation analysis.
2. Build the simple ingredient-utilization baseline using the same eligibility
   rules and candidate sets as the learned model.
3. Check the training environment and LightGBM API with the real finalized schema.
   The read-only `cli.py preflight` must pass data/dependency checks.
4. Before examining test results, record the evaluation criteria: NDCG@5,
   precision among up to five returned recipes, essential-ingredient violations,
   supporting-ingredient disclosure, coverage/no-result rate, and measured latency.
   Set practical targets with a stated rationale; do not invent an accuracy goal.

**Done when:** Reproducible validated features/groups and a baseline exist, and
evaluation criteria are written before test-set use. A passing preflight is not
proof of recommendation quality.

## Step 8 — Train and select the ranking model

**Status:** Not started. Start only after Steps 3–7 meet their completion conditions.

Actions: Fit LightGBM LambdaRank on training groups, use validation for early
stopping and controlled tuning, and save a versioned model with input hashes,
features, parameters, dependency versions, and seed. Never fit on test groups.

**Done when:** A reproducible nonconstant learned model is saved and reloads
successfully. Its scores are relative ranking scores, not accuracy percentages.

## Step 9 — Evaluate and decide whether the model is useful

**Status:** Pending.

Actions: Evaluate the selected model and baseline on the held-out test groups;
review failures by ingredient family and inventory type; verify no missing
essential ingredients are admitted. Report missing supporting ingredients and
no-result cases. Investigate and fix failures without repeatedly tuning on the
same test set; use a fresh final test if it becomes part of model development.

**Done when:** The model meets the recorded acceptance criteria and has a useful
justified result against the baseline. If it does not, improve data/features or
reconsider the model; do not claim success merely because training completed.
Do not claim observed zero-waste or cost savings without a separate user study.

## Step 10 — Add the recipe recommendation backend

**Status:** Pending; removed demo endpoints stay removed until this implementation.

Actions: Load the selected model and matching approved catalog once; accept the
confirmed inventory; enforce eligibility/exclusions; return ranked recipe IDs,
source details, used ingredients, and missing supporting items. Handle empty
results and incompatible model/catalog versions explicitly. Test actual model
reload and API behavior without fabricated recommendations.

**Done when:** The API returns verified ranked catalog entries using the saved
model, rejects missing-essential cases, and handles no-results/errors reliably.

## Step 11 — Connect and test the Expo app

**Status:** Pending for the real recommender; ingredient scanning/editing exists.

Actions: Connect recommendations to confirmed and manually edited ingredients;
refresh on inventory changes; show missing supporting items and real recipe
details. Handle loading, stale requests, empty results, and errors. Verify on Expo
Go iOS and the web; keep detection confidence separate from ranking scores.

**Done when:** Scan/upload or manual entry leads to appropriate ranked Filipino
dishes, edits update the results, and unavailable requirements are clearly shown.
Run app lint/type checks and relevant client/backend tests. Measure behavior on
the actual phone rather than assuming a browser test proves mobile behavior.

## Step 12 — Final documentation and reproducible delivery

**Status:** Process documentation started; final report pending actual results.

Actions: Finalize the data-preparation methodology, model-selection comparison,
data/label counts, exclusions, split design, training settings, evaluation results,
limitations, setup/run instructions, and model/data provenance. Answer why the
chosen approach fits and how alternatives differ; distinguish design reasoning
from experimentally demonstrated performance.

**Done when:** Another team member can reproduce the data/model versions and run
the app, and the paper's claims match saved evidence. Commit/push when requested;
do not publish data, invent results, or declare the system finished merely because
one demonstration works.

## Rules for staying on track

1. State the current step and its completion condition before starting new work.
2. Reuse/consolidate existing code. Create a new artifact only if it serves the
   current step and has a defined input/output and owner.
3. Record blockers and partial coverage honestly. Preserve valid earlier work.
4. Do not return to tiny pantry batches, add unrelated features, or switch models
   without a specific problem or evidence.
5. The next action is **Step 3.1: reconcile saved approvals with recipe annotations**.
   Then consolidate normalization and handle full-corpus exceptions. Do not start
   training or score only the four reviewed dishes as if they were the catalog.
