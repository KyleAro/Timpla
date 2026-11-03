# Partition 03 continuation checkpoint

Reviewed and persisted: partition indices 0 through 239 inclusive (240 records).
Next index: 240. Remaining indices 240 through 691 (452 records).
No index >= 240 has been inspected yet. Do not emit uninspected reviews.

Output: ../partition_03.decisions.json
Original input: ../partition_03.json
Required policy: ../REVIEW_POLICY.md (read completely before continuing).

Each saved record was individually read through compact display of every ingredient line, exact normalized role leaf IDs, draft roles, and the full supplied instructions. Truncated display 75-99 was repaired by explicitly reading 86-90. No ML/training, no external source verification, no human approvals.

Scripts:
- read.py start end renders complete supplied ingredient/role lines and instructions (end exclusive).
- build.py loads existing output and input; add(index,...) records a reviewed entry; save() orders records by input.
- batch01.py through batch12.py reproduce all 0-239, preserving prior output. Run in numeric order if reproducing.
- validate_checkpoint.py validates current 240-row checkpoint only; update expected count after further review.

Use batches <=20 records while methods are long to avoid output truncation. Exact override leaf IDs/line numbers asserted by build helper. add arguments: scope in/out/?; why; status ok/gap/?; issues triples (item,evidence,kind), over ov(line,id,role,basis), deps list, notes list. Status needs_review does not need invented source food gaps. Missing cooking water is material when needed for the dish/broth; bath/soaking water classified as process media unless meaningful state mismatch.

Owner-approved record exists at index 664: Basic Tortang Talong Recipe. preserved_owner_roles has major chinese_eggplant, egg; supporting salt, black_pepper, cooking_oil; optional empty. Preserve exactly, never role-override owner records.

Parent normalization guidance: Keep requirement tree/IDs untouched. If food leaf disagrees with original line, append note prefix 'Normalization concern:' with exact line/currentID/proposed identity. Material annotation error uses completeness needs_review and issue kind other; distinguish it from source-missing ingredients. Already tagged index33 line10 boiled_pork_belly plus pork duplicate, index197 line11 banana fruit leaf from banana chili, index208 line5 spice cloves from garlic-clove count. Index197's issue says banana leaf ID but means current ingredient_id banana; normalize wording on continuation if desired.

Current counts: completeness no_obvious_gap157, gap_identified50, needs_review33. Scope in215, out13, needs_review12.

Important semantic cautions: supporting items still required/disclosed. Optional only source-explicit; plus more if desired never makes whole required line optional. Preserve OR/all_of trees. Define adobo soy/vinegar, paksiw vinegar, kare-kare peanut bases, sinigang sour bases, ginataan coconut, tinola ginger, garlic rice garlic according to method. Prepared broth, reserved marinade, pineapple juice, squid ink derive from listed foods when evidenced; notes record dependencies. Generic foreign dishes do not automatically become Filipino because of Tagalog glosses or dataset source.
