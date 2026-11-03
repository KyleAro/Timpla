# Timpla Step 4 semantic review policy

Review every assigned recipe against its supplied ingredient lines AND instructions.
The automatic role proposals are drafts, not correct by default. No training.

## Roles

- essential: substantive or defining ingredients needed for this listed variant.
- supporting: cooking media, supporting aromatics, seasoning or garnish used by the
  recipe. Still disclose and confirm availability; never promise a no-purchase
  complete dish when supporting items are absent.
- optional: explicitly optional in the source. A small quantity or a generic
  condiment category does not establish optionality. 'Plus more if desired' makes
  the EXTRA amount optional, not the entire required ingredient.
- Keep the four owner-approved role records exactly as given. Flag disagreement
  in notes, do not override owner roles or pretend to approve completeness/scope.
- Preserve all_of/any_of expressions, states, cuts and alternatives. Role overrides
  assign each food leaf; never convert an OR into all mandatory identities.
- Check identity-defining seasonings: adobo soy/vinegar as present in that variant;
  paksiw vinegar; bistek citrus/soy/onion; ginataan coconut milk; sinangag garlic;
  kare-kare peanut base; sinigang souring base; tinola ginger. Recipe-specific
  evidence wins over these examples. Do not make all condiments optional.
- Prepared rice, broth from the same cooking step, retained pineapple juice, squid
  ink etc may derive from another listed ingredient. Record a dependency note,
  do not imply a separate purchase. Do not silently drop them or equate raw/cooked.

## Filipino cuisine scope

- proposed_in_scope: identifiable Filipino/local dish, Filipino adaptation, or
  contextual Filipino preparation. Recognized Filipino adaptations (e.g. sweet
  spaghetti, pancit, Filipino adobo, local-style lumpia) can qualify. A foreign
  origin by itself does not disqualify an established Filipino adaptation.
- proposed_out_of_scope: supplied text identifies another cuisine with no
  identifiable Filipino adaptation, or a generic auxiliary product rather than a
  relevant dish. Retain it and give a reason; no automatic deletion/exclusion.
- needs_review: insufficient evidence. Dataset membership, author's presumed
  nationality, and web-domain name alone do not establish cuisine scope. State
  uncertainty instead of labeling every record Filipino.
- Scope decisions are AI proposals requiring project review, not cultural claims.

## Internal completeness

- no_obvious_gap: read both list and method; no material unexplained gap identified
  in this dataset text. This is NOT verification against an original web source.
- gap_identified: cooking method requires a material item absent from the listed
  requirements; identify the item and actual evidence. Do not silently add it.
- needs_review: vague/short method, dependent subrecipe without details, missing
  state/quantity or unresolved terminology that prevents a firm consistency check.
- Classify serving suggestions separately from items needed to make the dish.
  'Serve with rice' does not prove rice is a missing ingredient of the dish.
- Nonfood headings/equipment/notes do not count as food or as automatic gaps.
- Original source checking remains pending except existing recorded comparisons.
  Do not claim external verification or independent human approval.

## Output

JSON array, exactly one record per input recipe id:

    {"recipe_id":"...",
     "cuisine_scope":{"decision":"proposed_in_scope|proposed_out_of_scope|needs_review","basis":"actual reason"},
     "internal_completeness":{"status":"no_obvious_gap|gap_identified|needs_review","basis":"actual dataset-context assessment","issues":[{"item":"...","evidence":"...","kind":"missing_ingredient|subrecipe_dependency|terminology|state_or_quantity|other"}]},
     "role_overrides":[{"line_number":1,"ingredient_id":"existing exact leaf ID","role":"essential|supporting|optional","basis":"recipe-specific reason"}],
     "dependency_notes":["..."],
     "notes":["..."],
     "annotation_type":"ai_recipe_semantic_review",
     "reviewer":"Codex AI-assisted recipe review; not independent human approval"}

No override needed when the existing draft role is appropriate. Review it anyway.
If a compound contains the same ID more than once, an override applies to those
occurrences in this same line only. Never invent an ingredient ID or line number.
Never change or fill owner approvals, original URLs, human relevance labels,
training files, or any shared Python file. Work only in the assigned output file
and a uniquely named scratch subfolder. Do not run training or training tests.
