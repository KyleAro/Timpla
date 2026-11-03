# Free AI suggestion API prototype

This is a backend-only prototype for suggesting Filipino or Filipino-style meals from ingredients the user already has. It does not replace the current ranker or change the Expo screens. It runs separately on port `8002` so you can test its API first.

The prototype uses Gemini 2.5 Flash through Google's Interactions API. Google currently lists text input/output as free on its free tier, but actual quotas depend on the Google AI Studio project and can change. Google's current terms also say free-tier prompts and responses may be used to improve its products. `store: false` is sent to avoid saving an interaction as a retrievable conversation, but this does **not** opt out of the free-tier data-use terms. For this prototype, only ingredient IDs and matching recipe reference names/IDs/links are sent. Do not send account details or other personal information.

## 1. Create a free API key

Create a Gemini API key in [Google AI Studio](https://aistudio.google.com/app/apikey). Check that the project has free-tier access and inspect its current model limits in AI Studio. Do not put the key in `EXPO_PUBLIC_*`, the Expo app, or a committed file.

## 2. Start the local Python service

In PowerShell, from the Timpla project root:

```powershell
$secureKey = Read-Host -AsSecureString "Gemini API key"
$env:GEMINI_API_KEY = [System.Net.NetworkCredential]::new("", $secureKey).Password
& ".\ml\recipe_recommendation\.venv\Scripts\python.exe" ".\ml\recipe_recommendation\suggestions_api.py" --host 0.0.0.0 --port 8002
```

Keep this terminal open. The key exists only in this terminal's process environment and is not written to the repository.

## 3. Check that the service is running

In a second PowerShell terminal:

```powershell
Invoke-RestMethod "http://localhost:8002/health"
```

The response should say `"status": "ready"`.

## 4. Ask for suggestions from the example inventory

```powershell
$body = @{ available = @("egg", "chicken breast", "soy sauce", "sayote") } | ConvertTo-Json
Invoke-RestMethod `
    -Uri "http://localhost:8002/suggestions" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body | ConvertTo-Json -Depth 10
```

The response contains multiple AI-generated ideas, exact available ingredient IDs used by each idea, remaining ingredients for another dish, fixed rendered steps, and any matching dataset references. AI ideas are labelled separately from dataset recipes and are not claimed to be tested or authentic. Review every suggestion before cooking.

The server enforces that the selected ingredient IDs and each step's ingredient IDs come from the user's inventory. Steps are rendered from a fixed action list rather than free-form AI prose, which limits unlisted ingredients appearing as added shopping requirements. The generated titles still need human review.

## What this prototype does not do yet

- It is not connected to the Expo Results screen.
- It does not replace or train the LightGBM ranker.
- It does not guarantee culinary quality, complete instructions, safe temperatures, or zero waste.
- It is not production-ready: this local API has permissive development CORS and no user authentication or hosted service deployment.
- Free-tier availability and quotas are controlled by Google and are not guaranteed.
