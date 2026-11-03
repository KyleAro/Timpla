# Timpla: train and test the recipe recommendation model

Follow these steps in order. All commands are for Windows PowerShell.
You will train the model yourself, test predictions, and start a local API that
your phone can reach. The recipe results screen is not connected to this API yet.

## Step 1 — Open the project

Open VS Code, open the Timpla folder, then select **Terminal → New Terminal**.

Run:

```powershell
Set-Location "C:\Users\User\OneDrive - Innobyte\Desktop\Timpla"
Get-Location
```

Expected: the printed location ends with `Desktop\Timpla`.
If your checkout is elsewhere, use that actual folder instead.

Keep this terminal as **Terminal A**. You do not need to activate a virtual
environment or change PowerShell execution policy for the following commands.

## Step 2 — Confirm the scripts and input data exist

```powershell
Test-Path "ml/recipe_recommendation/quick_train.py"
Test-Path "ml/recipe_recommendation/quick_api.py"
Test-Path "ml/recipe_recommendation/data/recipe_review/v1/recipes.draft.json"
```

Expected: three `True` results. If any result is `False`, check that you opened
the right checkout and that it contains the current files. Do not train using a
different old dataset just to bypass a missing path.

## Step 3 — Select Python

```powershell
$py = ".\ml\recipe_recommendation\.venv\Scripts\python.exe"
Test-Path $py
```

If that prints `True`, continue to Step 4.

If it prints `False`, create the environment once:

```powershell
py -3.11 -m venv ml/recipe_recommendation/.venv
$py = ".\ml\recipe_recommendation\.venv\Scripts\python.exe"
& $py -m pip install -r ml/recipe_recommendation/requirements.txt
```

If Python 3.11 is missing, run `py --list` and install Python 3.11 before retrying.
The `.venv-model` environment shown in older terminals is separate; these commands
explicitly use the recommendation environment.

## Step 4 — Check dependencies

```powershell
& $py --version
& $py -c "import lightgbm, numpy, sklearn; print('LightGBM:', lightgbm.__version__); print('NumPy:', numpy.__version__); print('scikit-learn:', sklearn.__version__)"
```

Expected: Python and all three package versions print without an import error.
If a package is missing:

```powershell
& $py -m pip install -r ml/recipe_recommendation/requirements.txt
```

## Step 5 — Train

Choose the version name once and keep it for the remaining steps:

```powershell
$model = "ml/recipe_recommendation/models/quick_v1"
& $py ml/recipe_recommendation/quick_train.py train --output $model --inventories 300
```

The script will:

1. Read the existing recipe-role drafts.
2. Keep recipes with a proposed essential requirement; record other recipes as
   held out in metadata. Original recipes remain unchanged.
3. Generate synthetic inventories and automatic relevance labels.
4. Split inventory groups into training, validation and test sets.
5. Train LightGBM LambdaRank on CPU and save its outputs.

Progress messages include `Preparing automatic inventories`, periodic inventory
counts, `Training LightGBM on CPU`, then `Model saved:`. Wait for the command to
finish and the PowerShell prompt to return. Preparation can take time between
progress messages; elapsed time alone does not prove it is stuck.

If the output directory already exists, choose a NEW version:

```powershell
$model = "ml/recipe_recommendation/models/quick_v2"
& $py ml/recipe_recommendation/quick_train.py train --output $model --inventories 300
```

Use that same version in all following commands. Do not delete a previous model
just to reuse its directory name.

## Step 6 — Confirm training succeeded

```powershell
Get-ChildItem $model
Get-Content "$model/metadata.json"
```

Expected output files:

```text
ranker.txt
catalog.json
metadata.json
inventories.synthetic.json
```

`ranker.txt` is the trained model. `catalog.json` is the matching recipe catalog.
Keep the four files together; do not replace the catalog with a different version.
Metadata records split counts, generated-label metrics, limitations, and held-out
recipes. A traceback or missing files means training did not complete successfully.

## Step 7 — Test eggplant and egg

In Terminal A:

```powershell
& $py ml/recipe_recommendation/quick_train.py recommend --model $model --ingredients egg eggplant cooking_oil salt black_pepper
```

Expected: a JSON list of matching recipe suggestions, or `[]` if none qualify.
Each returned item includes a name, ranking score and missing supporting items.
The exact dishes depend on the current catalog and draft ingredient roles.

## Step 8 — Test another inventory

```powershell
& $py ml/recipe_recommendation/quick_train.py recommend --model $model --ingredients egg cooked_rice garlic cooking_oil salt
```

Also test an inventory that should have no useful match:

```powershell
& $py ml/recipe_recommendation/quick_train.py recommend --model $model --ingredients unknown_test_ingredient
```

An empty result is valid. The code should not invent a recipe to fill the screen.

Ingredient names matter. `talong` and `eggplant` are aligned; `kanin` maps to
`cooked_rice`. Generic `chicken` does not automatically satisfy every specific
chicken cut. To inspect the IDs available in your model:

```powershell
$catalog = Get-Content "$model/catalog.json" -Raw | ConvertFrom-Json
$catalog | ForEach-Object { $_.all_food } | Sort-Object -Unique
```

## Step 9 — Start the local API in Terminal B

Open another VS Code terminal. Run:

```powershell
Set-Location "C:\Users\User\OneDrive - Innobyte\Desktop\Timpla"
.\ml\recipe_recommendation\.venv\Scripts\python.exe ml/recipe_recommendation/quick_api.py --model ml/recipe_recommendation/models/quick_v1 --port 8001
```

Replace `quick_v1` if you used another model version. Keep Terminal B open while
testing. Expected: `Local testing API on port 8001`.

Port **8001** is for this recommendation API. It is separate from your ingredient
detector and the Expo development server.

Stop this server later with **Ctrl+C** in Terminal B.

## Step 10 — Check API health on the PC

Back in Terminal A:

```powershell
Invoke-RestMethod -Uri "http://localhost:8001/health"
```

Expected fields:

```json
{"status":"ready","mode":"experimental_automatic_labels"}
```

If it cannot connect, inspect Terminal B. The server must still be running and
must have loaded the same model folder successfully.

## Step 11 — Request recommendations over HTTP

In Terminal A:

```powershell
$body = @{
    available = @("egg", "eggplant", "cooking_oil", "salt", "black_pepper")
    limit = 5
} | ConvertTo-Json

$result = Invoke-RestMethod `
    -Uri "http://localhost:8001/recommendations" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body

$result | ConvertTo-Json -Depth 10
```

Expected: an object with a `recommendations` array. The array can be empty.
For a simpler table:

```powershell
$result.recommendations | Select-Object name, ranking_score, missing_supporting
```

Interpretation:

| Field | Meaning |
|---|---|
| `name` | Real recipe entry from the saved catalog |
| `ranking_score` | Relative learned score; not accuracy or a probability |
| `missing_supporting` | Items still needing confirmation |
| `supporting_confirmation_needed` | Whether supporting items remain unconfirmed |
| `quantity_and_preparation_check_needed` | Amounts and preparation still need checking |
| `source_urls` | Available source links; some dataset records have none |

## Step 12 — Check phone connectivity

In Terminal A:

```powershell
ipconfig
```

Find the **IPv4 Address** of the active Wi-Fi adapter. For example, if it is
`192.168.1.2`, open this in your phone's browser:

```text
http://192.168.1.2:8001/health
```

Use your ACTUAL address, not the example by assumption. Both devices should be
on the same reachable local network. Keep Terminal B running. If Windows prompts
for Python network access, allow it on the private network you are testing on.
Do not disable the firewall globally.

Expected: the same ready JSON as on the PC. This verifies phone-to-server
connectivity; it does not connect the Expo results screen automatically.

## Step 13 — Connect the app after the API tests work

The current deliverable provides the trainer, command-line inference and local
API. The Expo recommendation request/results integration is still a coding task.
No recommendation environment variable is wired in the app yet.

The integration must do the following:

1. Take the inventory AFTER the user confirms, removes or adds detected ingredients.
2. Send `POST http://YOUR_PC_IPV4:8001/recommendations` with JSON containing
   `available` (an array of ingredient names/IDs) and `limit` (1–20).
3. Read the response's `recommendations` array.
4. Render recipe names and missing supporting ingredients.
5. Handle loading, network errors and empty results.
6. Request fresh results when the confirmed inventory changes; discard stale ones.
7. Keep ranking scores separate from YOLO detection confidence.

For this integration, follow AGENTS.md: read the installed Expo major and matching
Expo documentation before changing Expo/React Native code. The API already permits
local browser cross-origin requests. The Python server is for local testing,
not a deployed authenticated production service.

## Step 14 — Common errors

| Error/symptom | What to do |
|---|---|
| Cannot open `quick_train.py` | Return to the correct Timpla project root; repeat Step 2. |
| `$py` is empty/not recognized | Repeat Step 3 in that terminal; variables do not carry to a new terminal. |
| `No module named lightgbm` | Install requirements using the exact `$py` interpreter. |
| `Output exists` | Use a new model version name and update later commands. |
| Too few informative inventories / empty split | Retry with a NEW model directory, `--inventories 600 --seed 43`; if it persists, improve draft roles/scenario diversity. |
| `Model learned no splits` | The generated examples are insufficiently informative; inspect data rather than reporting successful training. |
| Missing `ranker.txt` | Training failed or you selected the wrong model folder. Check its terminal output. |
| Port already in use | Stop your old test server, or use `--port 8002` and update request URLs. |
| HTTP404 | Check `/health` for GET or `/recommendations` for POST. |
| HTTP400 | Send a JSON `available` list of strings and integer `limit` from1 to20. |
| PC works; phone fails | Verify actual Wi-Fi IP, same network, private-network firewall permission, and that the server remains running. |
| Results are `[]` | Check inventory IDs and draft essential requirements; an empty match can be correct. |
| Irrelevant/non-Filipino recipe appears | The experimental catalog has unverified scope. Flag/filter the entry during review; automatic labels do not fix catalog quality. |

## Step 15 — Know what this test proves

This path trains a real LightGBM ranking model using **automatically generated
labels**. It lets you test training, prediction and a local API without waiting
for every manual review.

- Generated-label metrics measure agreement with the automatic scoring rules.
- They do not establish human usefulness or superiority over those rules.
- Draft roles, cuisine scope, prepared-food dependencies and quantities still
  have limitations. Similar synthetic inventories may cross split boundaries.
- The code keeps essential-ingredient filtering and reports missing supporting
  items, but recommendations still require review before being claimed cookable
  without additional purchases.

For your paper, describe this run as an **experimental weakly supervised baseline**.
Save the model version, metadata, actual results and observed failures. Later,
use reviewed recipes and independent human relevance judgments to evaluate the
real recommendation objective.

## Completion checklist

- [ ] Python imports work.
- [ ] Training finishes and all four model output files exist.
- [ ] Terminal recommendation tests run.
- [ ] PC `/health` returns ready.
- [ ] PC POST returns a recommendations array.
- [ ] Phone `/health` returns ready.
- [ ] Expo request/results integration is implemented separately.
- [ ] The app updates recommendations after inventory edits.
- [ ] Missing supporting items, empty results and errors are handled.

**Start with Step 1. Do not rerun the old cleaning or annotation scripts to run
this experimental trainer.**
