# Saved recommendation preferences

The recommendations screen reads allergies, excluded ingredients and diet from
the saved CookingContext preferences. Changes invalidate the current request.
POST /recommendations accepts `allergies` (string array), `excluded` (string array),
and `diet` (`No preference`, `Vegetarian`, or `Halal`). The API returns an
`applied_preferences` echo of those three fields. Restricted requests reject
responses without the matching echo so an older server cannot silently ignore
settings. Restart/redeploy quick_api.py together with preference_filters.py and
quick_train.py for this contract.

Filtering runs on all_food before ranking, covering essential, supporting,
optional and alternative ingredients conservatively. Exclusions match whole
ingredient terms and forms (pork also matches pork_belly). Common allergy rules
cover Peanuts, Shellfish, Eggs, Dairy, Soy and Wheat, including known derivatives.
These are conservative discovery filters, not a complete allergen ontology or
an allergy-safety certification. Composite ingredients, product formulation and
cross-contact still need verification. Ingredient labels remain visible to users.

Custom allergies require an explicit normalized name in a recipe's
`verified_free_from` array. Diet restrictions require the exact diet name in the
recipe's `verified_diets` array. These fields must come from reviewed evidence;
they are never inferred from a missing animal ingredient or a recipe name.
The current experimental catalog has no verified diet labels, so Vegetarian and
Halal requests return no results until reviewed metadata is added to the serving
catalog. Training does not create or certify these labels.
