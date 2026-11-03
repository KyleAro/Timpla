# Recipe imagery

Generated with the built-in imagegen tool as illustrative application assets.
These are not photographs from the recipe sources and are not used as training data.

- `tortang-talong.png`: whole grilled eggplants flattened into golden egg omelettes.
- `chicken-adobo.png`: bone-in chicken in soy-vinegar sauce with bay leaves and peppercorns.
- `ginisang-sayote.png`: sauteed chayote with ground pork.
- `adobo-burrito.png`: flour tortillas with rice and shredded pork adobo.
- `kitchen-fallback.png`: neutral uncooked ingredients and utensils; used when a matching dish illustration is unavailable.

Prompt direction: standalone realistic editorial food photographs, warm natural daylight,
cream ceramic dishes, linen and wood, landscape crop-safe composition, no text or watermark.
The fallback prompt requests rice, onion, garlic, tomatoes, calamansi, soy sauce and utensils,
with no prepared dish so it does not imply a specific recipe.

Image assignments live in `src/utils/recipeImages.ts` and use exact dish-family names.
The shared fallback provides image coverage for all recipes; individual dish imagery
currently covers the four dishes above. Replace or extend assignments as sourced photos arrive.
