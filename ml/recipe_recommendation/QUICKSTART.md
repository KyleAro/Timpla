# Train and test now

This experimental path uses the existing full-corpus ingredient-role drafts and
automatic relevance labels. It does not require completing the manual review.
It is a weakly supervised model: evaluation measures agreement with generated
rules, not human recommendation quality. Cuisine scope, quantities, prepared-food
dependencies and ingredient roles still have known limitations.

From the project root, PowerShell:

```powershell
$py = ".\ml\recipe_recommendation\.venv\Scripts\python.exe"
& $py ml/recipe_recommendation/quick_train.py train --output ml/recipe_recommendation/models/quick_v1 --inventories 300
```

Training saves `ranker.txt`, `catalog.json`, `metadata.json` and
`inventories.synthetic.json` inside the output folder. Existing folders are never
overwritten; use `quick_v2` for a later run. The metadata names the recipes held
out because their draft contains no essential requirement. Original data is not
changed. Similar synthetic inventories can still cross splits; metrics are
experimental, not a publishable independent user evaluation.

Test predictions:

```powershell
& $py ml/recipe_recommendation/quick_train.py recommend --model ml/recipe_recommendation/models/quick_v1 --ingredients egg eggplant cooking_oil salt black_pepper
& $py ml/recipe_recommendation/quick_train.py recommend --model ml/recipe_recommendation/models/quick_v1 --ingredients egg cooked_rice garlic cooking_oil salt
```

Use source-specific ingredient IDs where necessary. Generic chicken does not
automatically mean chicken breast, thighs or every other cut. Empty matches are
allowed. Missing supporting ingredients are returned for confirmation; a match is
not a guarantee that the dish can be made without further ingredients.

Start the local API in another terminal:

```powershell
.\ml\recipe_recommendation\.venv\Scripts\python.exe ml/recipe_recommendation/quick_api.py --model ml/recipe_recommendation/models/quick_v1 --port 8001
```

Test it on the PC:

```powershell
Invoke-RestMethod -Uri "http://localhost:8001/recommendations" -Method Post -ContentType "application/json" -Body '{"available":["egg","eggplant","cooking_oil","salt","black_pepper"],"limit":5}'
```

`GET http://localhost:8001/health` checks whether the model server is ready.
For a phone, replace localhost with your PC's actual Wi-Fi IPv4 address from
`ipconfig`. Put the phone on the same network and allow this Python server through
the local firewall if Windows prompts. Port8001 is separate from the detector.

The app/backend request contract is:

```json
{"available":["egg","eggplant","cooking_oil","salt"],"limit":5}
```

Response:

```json
{"recommendations":[]}
```

Each returned recommendation includes `id`, `name`, `ranking_score`,
`missing_supporting`, `supporting_confirmation_needed`, source URLs and a
quantity/preparation-check flag. Send the user's confirmed/edited inventory after
scanning. Display missing supporting items and permit no matches. The API is for
local testing; production authentication, deployment and app UI wiring are separate.

Python backend integration can call the same function directly:

```python
from pathlib import Path
from quick_train import recommend

results = recommend(Path("ml/recipe_recommendation/models/quick_v1"),
                    ["egg", "eggplant", "cooking_oil", "salt"], limit=5)
```

The import above assumes `ml/recipe_recommendation` is on the Python import path.
The local API already configures that naturally when launched using the command.
The trained model/catalog are cached in memory for repeated requests.
