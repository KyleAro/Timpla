"""Local prototype API for AI meal suggestions constrained to available ingredients.

The Gemini key stays in this Python process. The Expo app must call this server,
never Gemini directly. This prototype does not save prompts or generated meals.
"""

from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import urllib.error
import urllib.request


ROOT = Path(__file__).resolve().parent
CATALOG = ROOT / "data/recipe_review/v1/recipes.draft.json"
DEFAULT_MODEL = "gemini-2.5-flash"
GEMINI_INTERACTIONS_URL = "https://generativelanguage.googleapis.com/v1beta/interactions"
MAX_BODY_BYTES = 16_384
MAX_INGREDIENTS = 30

ALIASES = {
    "eggs": "egg", "itlog": "egg", "chicken": "chicken_generic",
    "chicken_meat": "chicken_generic", "chicken_breast": "chicken_breast",
    "sayote": "chayote", "soy_sauce": "soy_sauce", "toyo": "soy_sauce",
    "kanin": "cooked_rice", "rice": "rice_grains", "cooked_rice": "cooked_white_rice",
    "oil": "cooking_oil", "mantika": "cooking_oil", "asin": "salt",
    "bawang": "garlic", "sibuyas": "onion", "talong": "eggplant",
    "kamatis": "tomato", "tomatoes": "tomato", "pepper": "black_pepper",
}

ACTION_TEXT = {
    "slice": "Slice {items} into manageable pieces.",
    "chop": "Chop {items} into small pieces.",
    "beat": "Beat {items} until blended.",
    "mix": "Mix {items} together.",
    "stir_fry": "Cook {items} together in a pan, stirring often, until tender and fully cooked.",
    "pan_cook": "Cook {items} in a pan until fully cooked.",
    "simmer": "Simmer {items} together until tender and fully cooked.",
    "boil": "Boil {items} until tender and fully cooked.",
    "steam": "Steam {items} until tender and fully cooked.",
    "mash": "Mash {items} together.",
    "serve": "Serve {items} together.",
}

SCHEMA = {
    "type": "object",
    "properties": {
        "suggestions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "ingredient_ids_used": {"type": "array", "items": {"type": "string"}},
                    "steps": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "action": {"type": "string", "enum": list(ACTION_TEXT)},
                                "ingredient_ids": {"type": "array", "items": {"type": "string"}},
                            },
                            "required": ["action", "ingredient_ids"],
                        },
                    },
                    "reference_recipe_ids": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["title", "ingredient_ids_used", "steps", "reference_recipe_ids"],
            },
        }
    },
    "required": ["suggestions"],
}


def normalize(value: str) -> str:
    key = re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")
    return ALIASES.get(key, key)


def ingredient_ids_in_line(line: dict) -> set[str]:
    found: set[str] = set()

    def walk(node: dict) -> None:
        if isinstance(node, dict):
            if isinstance(node.get("ingredient_id"), str):
                found.add(normalize(node["ingredient_id"]))
            for value in node.values():
                if isinstance(value, dict):
                    walk(value)
                elif isinstance(value, list):
                    for item in value:
                        walk(item)

    walk(line.get("requirement", {}))
    return found


def retrieve_references(available: set[str], limit: int = 8) -> list[dict]:
    if not CATALOG.exists():
        return []
    recipes = json.loads(CATALOG.read_text(encoding="utf-8"))
    ranked = []
    for recipe in recipes:
        foods: set[str] = set()
        for line in recipe.get("lines", []):
            foods.update(ingredient_ids_in_line(line))
        overlap = foods & available
        if overlap:
            ranked.append((len(overlap), len(overlap) / max(1, len(foods)), recipe, foods))
    ranked.sort(key=lambda row: (-row[0], -row[1], row[2].get("name", "").casefold()))
    return [
        {
            "id": recipe["id"],
            "name": recipe.get("name", "Untitled recipe"),
            "source_urls": recipe.get("source_urls", []),
            "recipe_ingredient_ids": sorted(foods),
            "matched_ingredients": sorted(foods & available),
        }
        for _, _, recipe, foods in ranked[:limit]
    ]


def build_prompt(available: set[str], references: list[dict]) -> str:
    pantry = sorted(available)
    return (
        "Create 3 distinct, practical Filipino or Filipino-style home meal suggestions "
        "from this inventory. This app aims to use food the user already has and reduce "
        "waste. Do not make the user shop. A suggestion may use only some inventory items; "
        "do not force unrelated ingredients into one dish. Every ingredient ID in every "
        "suggestion and step MUST be selected from the supplied inventory. Do not assume "
        "oil, salt, water, or other pantry staples unless they are listed. If the inventory "
        "cannot make 3 sensible options, return fewer. Steps use only the provided action "
        "codes and ingredient IDs; do not add quantities or ingredients. Use references only "
        "when truly relevant, and only return their exact IDs. Dataset references are ideas, "
        "not proof that a suggestion is an authentic or tested recipe. Avoid unsafe cooking "
        "claims; say meat must be cooked through.\n\n"
        f"Available ingredient IDs: {json.dumps(pantry)}\n"
        f"Possible Filipino recipe references: {json.dumps(references, ensure_ascii=False)}\n"
        f"Allowed action codes: {json.dumps(list(ACTION_TEXT))}"
    )


def response_schema(available: set[str], reference_ids: set[str]) -> dict:
    schema = json.loads(json.dumps(SCHEMA))
    suggestion = schema["properties"]["suggestions"]["items"]["properties"]
    suggestion["ingredient_ids_used"]["items"]["enum"] = sorted(available)
    suggestion["steps"]["items"]["properties"]["ingredient_ids"]["items"]["enum"] = sorted(available)
    if reference_ids:
        suggestion["reference_recipe_ids"]["items"]["enum"] = sorted(reference_ids)
    return schema


def extract_output_text(response: dict) -> str:
    if isinstance(response.get("output_text"), str):
        return response["output_text"]
    for step in response.get("steps", []):
        if step.get("type") != "model_output":
            continue
        for block in step.get("content", []):
            if block.get("type") == "text" and isinstance(block.get("text"), str):
                return block["text"]
    raise ValueError("The AI service returned no structured suggestion text.")


def render_suggestion(raw: dict, available: set[str], references: dict[str, dict]) -> dict:
    title = raw.get("title")
    used_values = raw.get("ingredient_ids_used")
    raw_steps = raw.get("steps")
    raw_refs = raw.get("reference_recipe_ids", [])
    if not isinstance(title, str) or not title.strip() or len(title) > 100:
        raise ValueError("A suggestion had an invalid title.")
    if not isinstance(used_values, list) or not isinstance(raw_steps, list) or not raw_steps:
        raise ValueError("A suggestion was missing its ingredient list or steps.")
    used = {normalize(item) for item in used_values if isinstance(item, str)}
    if not used or not used.issubset(available):
        raise ValueError("A suggestion included an ingredient the user did not provide.")

    steps = []
    mentioned: set[str] = set()
    for raw_step in raw_steps[:8]:
        action = raw_step.get("action")
        item_ids = raw_step.get("ingredient_ids")
        if action not in ACTION_TEXT or not isinstance(item_ids, list) or not item_ids:
            raise ValueError("A suggestion contained an invalid cooking step.")
        items = {normalize(item) for item in item_ids if isinstance(item, str)}
        if not items or not items.issubset(used):
            raise ValueError("A cooking step referred to an ingredient outside its suggestion.")
        mentioned.update(items)
        labels = ", ".join(sorted(items).copy()).replace("_", " ")
        steps.append(ACTION_TEXT[action].format(items=labels))
    if not steps or mentioned != used:
        raise ValueError("A suggestion's steps did not cover exactly its declared ingredients.")

    refs = [references[value] for value in raw_refs if isinstance(value, str) and value in references]
    return {
        "id": re.sub(r"[^a-z0-9]+", "-", title.casefold()).strip("-")[:80],
        "title": title.strip(),
        "type": "ai_suggestion",
        "ingredient_ids_used": sorted(used),
        "ingredient_ids_left_for_another_dish": sorted(available - used),
        "steps": steps,
        "references": refs,
        "note": "AI-generated cooking idea, not a tested recipe. Review the steps and cook food thoroughly.",
    }


def generate_suggestions(available_values: list[str], api_key: str, model: str = DEFAULT_MODEL) -> list[dict]:
    available = {normalize(value) for value in available_values if value.strip()}
    if not available:
        raise ValueError("Add at least one ingredient first.")
    if len(available) > MAX_INGREDIENTS:
        raise ValueError(f"Use no more than {MAX_INGREDIENTS} ingredients at a time.")
    references_list = retrieve_references(available)
    references = {item["id"]: item for item in references_list}
    request_data = {
        "model": model,
        "input": build_prompt(available, references_list),
        "store": False,
        "generation_config": {"max_output_tokens": 1800},
        "response_format": {
            "type": "text",
            "mime_type": "application/json",
            "schema": response_schema(available, set(references)),
        },
    }
    request = urllib.request.Request(
        GEMINI_INTERACTIONS_URL,
        data=json.dumps(request_data).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            payload = json.loads(response.read())
    except urllib.error.HTTPError as error:
        if error.code == 429:
            raise RuntimeError("The Gemini free-tier quota is currently unavailable. Check AI Studio limits and try again later.") from None
        if error.code in (401, 403):
            raise RuntimeError("Gemini rejected the key or this project does not have free-tier access.") from None
        raise RuntimeError(f"Gemini request failed with HTTP {error.code}.") from None
    except (urllib.error.URLError, TimeoutError):
        raise RuntimeError("Could not reach Gemini. Check the PC internet connection and retry.") from None

    decoded = json.loads(extract_output_text(payload))
    candidates = decoded.get("suggestions")
    if not isinstance(candidates, list):
        raise ValueError("The AI service returned an invalid suggestions list.")
    results = []
    seen = set()
    for candidate in candidates:
        result = render_suggestion(candidate, available, references)
        key = result["title"].casefold()
        if key not in seen:
            results.append(result)
            seen.add(key)
        if len(results) >= 3:
            break
    return results


def make_handler(model: str):
    class Handler(BaseHTTPRequestHandler):
        def reply(self, status: int, data: dict) -> None:
            body = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_OPTIONS(self) -> None:
            self.reply(200, {})

        def do_GET(self) -> None:
            if self.path != "/health":
                self.reply(404, {"error": "Not found"})
                return
            self.reply(200, {
                "status": "ready" if os.environ.get("GEMINI_API_KEY") else "needs_api_key",
                "mode": "experimental_free_tier_ai_suggestions",
                "model": model,
            })

        def do_POST(self) -> None:
            if self.path != "/suggestions":
                self.reply(404, {"error": "Not found"})
                return
            if not os.environ.get("GEMINI_API_KEY"):
                self.reply(503, {"error": "Set GEMINI_API_KEY in this Python server terminal first."})
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= MAX_BODY_BYTES:
                    raise ValueError("Invalid request size.")
                data = json.loads(self.rfile.read(length))
                available = data.get("available")
                if not isinstance(available, list) or any(not isinstance(value, str) for value in available):
                    raise ValueError("available must be a list of ingredient names.")
                if not 1 <= len(available) <= MAX_INGREDIENTS:
                    raise ValueError(f"Provide 1 to {MAX_INGREDIENTS} ingredients.")
                suggestions = generate_suggestions(available, os.environ["GEMINI_API_KEY"], model)
                self.reply(200, {"suggestions": suggestions})
            except (ValueError, TypeError, json.JSONDecodeError) as error:
                self.reply(400, {"error": str(error)})
            except RuntimeError as error:
                self.reply(503, {"error": str(error)})
            except Exception:
                self.reply(502, {"error": "Could not prepare valid meal suggestions. Try again."})

        def log_message(self, format: str, *args) -> None:
            # Do not log ingredient inventories or provider responses.
            print(f"{self.address_string()} - {format % args}")

    return Handler


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8002)
    parser.add_argument("--model", default=os.environ.get("GEMINI_MODEL", DEFAULT_MODEL))
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), make_handler(args.model))
    print(f"Timpla AI suggestion prototype listening on port {args.port}; GET /health, POST /suggestions")
    print("GEMINI_API_KEY is configured." if os.environ.get("GEMINI_API_KEY") else "GEMINI_API_KEY is not configured; suggestions will return 503.")
    server.serve_forever()


if __name__ == "__main__":
    main()
