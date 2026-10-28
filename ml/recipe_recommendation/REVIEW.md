# First review: recipe recommendation data

Nothing in this folder is connected to the app. These are real source-backed candidate recipe records, not training labels or a trained model.

## 1. Check the recipe records

Open `data/recipes.review.json` and visit each source. The proposed ingredient roles are:

| Recipe | Proposed major ingredients |
| --- | --- |
| Tortang Talong | Eggplant, egg |
| Sinangag | Cooked rice, garlic |
| Kultyas | Tomato, egg, onion, garlic |
| Ginisang Repolyo with Eggs | Cabbage, egg, carrot, onion, garlic |
| Adobong Kangkong with Pork | Kangkong, pork belly, onion, garlic, soy sauce, vinegar |
| Ginisang Sayote with Egg | Chayote, egg, garlic, onion |

Check the supporting and optional lists too. The role of onion/garlic is a recipe-specific decision for the team to review. Recipes retain their specific published version; do not silently remove major ingredients or merge different versions.

For each approved record, fill `reviewed_by` with the reviewer's name and `reviewed_at` with the actual review date. Leave unapproved records unreviewed. Known unknown preparation time is null rather than invented. Confirm ingredient forms (especially cooked rice and meat cuts).

## 2. Check the input scenarios

Open `data/queries.review.json`. Eight draft researcher scenarios are supplied for discussion, not collected user observations. Confirm/revise each inventory and use-first list, fill `reviewed_by`, and assign `split` (`train`, `validation`, `test`) and `leakage_group`.

Related inventory variations must stay in one split. A tiny eight-query collection only supports pipeline experiments; add independent scenarios before making performance claims.

## 3. Rate the suggestions

After recipe/query review, generate a fresh queue with `cli.py review-queue --output <new-file.csv>` if ingredient facts or scenarios changed. Source and query fingerprints prevent labels from being used after their context changes. Changing only reviewer names or split assignments does not invalidate the context.

Open the CSV. Each row is a proposed ingredient-list/recipe pair. Fill:

- `relevance`: 3 = highly useful, 2 = useful, 1 = weak, 0 = unsuitable for that situation.
- `reviewer`: reviewer's name.
- `notes`: reason, especially when support ingredients are unavailable or use-first ingredients influence your judgment.

Do not change `context_sha256`; regenerate the queue when the scenario or recipe changes. Do not fabricate rankings from overlap percentages. There can be several useful dishes for one scenario. Training requires ratings for every eligible candidate, including weaker suggestions.

The ranker learns which eligible recipes people prefer. It never learns permission to suggest a recipe with missing major ingredients.
