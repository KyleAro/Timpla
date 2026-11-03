"""Represent ingredient alternatives and contextual fragments without inventing food.

Leaves contain literal ingredient identities. any_of is never flattened to all_of.
Unrecognized or conflicting source text remains explicitly unresolved.
No recipe roles, relevance judgments, or model training are generated here.
"""
import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

from contextual_normalization import parse_flat, tidy, strip_amount, HANDLING, USAGE
from propose_batch_mappings import BASE, EXACT

ROOT = Path(__file__).resolve().parent
DATA = ROOT/'data/processed'
EQUIPMENT = {
    'foil': 'aluminum_foil', 'aluminum foil': 'aluminum_foil', 'aluminium foil': 'aluminum_foil',
    'bamboo sticks': 'bamboo_stick', 'bamboo barbecue sticks': 'bamboo_barbecue_stick',
    'bamboo skewers': 'bamboo_skewer', 'barbecue sticks': 'barbecue_stick',
    'barbeque sticks': 'barbecue_stick', 'wooden skewers': 'wooden_skewer',
    'popsicle sticks': 'popsicle_stick', 'kitchen string': 'kitchen_string',
    'kitchen twine': 'kitchen_twine', 'well-sealed jar': 'storage_jar',
    'a sterilized jar with lid': 'sterilized_jar', 'sterilized jar with lid': 'sterilized_jar',
}


def all_ids(ids):
    return {'all_of': [{'ingredient_id': value} for value in sorted(set(ids))]}


def leaves(expression):
    if 'equipment_id' in expression:
        return set()
    if 'ingredient_id' in expression:
        return {expression['ingredient_id']}
    key = 'all_of' if 'all_of' in expression else 'any_of'
    return set().union(*(leaves(child) for child in expression[key]))


def parse_requirement(text, roots, depth=0):
    if depth > 8:
        return None
    if ',' in text:
        # Commas are a conjunction only when every comma-delimited segment is a
        # complete named ingredient, never merely "peeled" or "chopped".
        segments, start, nesting = [], 0, 0
        for position, character in enumerate(text):
            if character in '([':
                nesting += 1
            elif character in ')]':
                nesting = max(0, nesting-1)
            elif character == ',' and nesting == 0:
                segments.append(text[start:position].strip())
                start = position+1
        segments.append(text[start:].strip())
        segments = [re.sub(r'^and\s+', '', segment) for segment in segments]
        if len(segments) > 1:
            parts = [parse_requirement(segment, roots, depth+1) for segment in segments]
            if all(parts):
                return {'all_of': parts}
    text = strip_amount(tidy(text))
    text = re.sub(r'^any ', '', text)
    text = re.sub(r'\bor (?:more to taste|more as needed|to taste|as needed)(?:\s|$)', '', text).strip()
    # Shape alternatives do not introduce alternative ingredient requirements.
    text = re.sub(r'\b(minced|chopped|grated|sliced|shredded|diced) or (minced|chopped|grated|sliced|shredded|diced)\b', r'\1', text)
    if not text or text.endswith(' or'):
        return None
    if text in EQUIPMENT:
        return {'equipment_id': EQUIPMENT[text]}
    if re.search(r'\bthai\b', text) and 'siling labuyo' in text and not re.search(r'\bor\b|\bo\b', text):
        return None  # Do not adjudicate conflicting varieties from a label alone.
    if text in EXACT:
        return all_ids(EXACT[text])
    state_choice = re.fullmatch(r'(.+?) (fried|baked|boiled|steamed|grilled|roasted) or (fried|baked|boiled|steamed|grilled|roasted)(.*)', text)
    if state_choice:
        options = [parse_requirement(state+' '+state_choice[1]+' '+state_choice[4], roots, depth+1)
                   for state in (state_choice[2], state_choice[3])]
        if all(options):
            return {'any_of': options}
    if re.fullmatch(r'(?:ground )?pepper(?: to taste| to season| paminta)?', text):
        return all_ids(['ground_pepper_unspecified' if text.startswith('ground ') else 'pepper_unspecified'])
    for pattern in [r'salt(?: asin)? (?:and|at) (?:pepper(?: paminta)?|paminta)(?: to taste(?: asin at paminta)?)?',
                    r'asin at paminta(?: salt and pepper)?(?: to taste)?',
                    r'salt & pepper(?: to taste)?']:
        if re.fullmatch(pattern, text):
            return all_ids(['salt', 'pepper_unspecified'])
    # Parsing alternatives is structural. Every branch must independently resolve.
    if re.search(r'\bor\b|\bo\b', text):
        parts = re.split(r'\s+(?:or|o)\s+', text)
        if len(parts) < 2 or any(not p for p in parts):
            return None
        parsed = []
        for part in parts:
            shared = None
            # Apply an explicitly shared head before accepting a bare animal as
            # meat: "beef or pork broth" requires broth, not beef meat.
            if part in {'beef', 'pork', 'chicken'}:
                for head in ('broth', 'stock', 'kidney'):
                    if any(re.fullmatch(r'(?:beef|pork|chicken) '+head, p) for p in parts):
                        shared = part+' '+head
                        break
            if part in {'lemon', 'lime', 'calamansi', 'orange'} and any(p.endswith(' juice') for p in parts):
                shared = part+' juice'
            result = parse_requirement(shared or part, roots, depth+1)
            if result is None:
                # A shared head: "white or cane vinegar", "beef or pork broth".
                for suffix in ('vinegar', 'oil', 'broth', 'stock', 'juice', 'kidney', 'cube', 'beans'):
                    if any(p.endswith(' '+suffix) for p in parts):
                        result = parse_requirement(part+' '+suffix, roots, depth+1)
                        if result:
                            break
            if result is None:
                # Shared animal prefix: "chicken breast or thigh".
                for animal in ('chicken', 'pork', 'beef'):
                    if parts[0].startswith(animal+' '):
                        result = parse_requirement(animal+' '+part, roots, depth+1)
                        if result:
                            break
            if result is None:
                return None
            parsed.append(result)
        unique = {json.dumps(p, sort_keys=True): p for p in parsed}
        return {'any_of': list(unique.values())}
    result = parse_flat(text, roots)
    if result:
        return all_ids(result)
    # A named slurry explicitly requires the starch/flour plus the named liquid.
    mixture = re.fullmatch(r'(.+?) (?:dissolved|diluted|mixed|soaked|steeped) in (.+)', text)
    if mixture:
        liquid = re.sub(r'\s+(?:overnight|for \d+ (?:minutes|hours))$', '', mixture[2])
        left = parse_requirement(mixture[1], roots, depth+1)
        right = parse_requirement(liquid, roots, depth+1)
        if left and right:
            return {'all_of': [left, right]}
    joined = re.fullmatch(r'(.+?) (?:combined with|seasoned with) (.+)', text)
    if joined:
        parts = [parse_requirement(segment, roots, depth+1) for segment in joined.groups()]
        if all(parts):
            return {'all_of': parts}
    if ' and ' in text:
        parts = text.split(' and ')
        parsed = []
        for part in parts:
            node = parse_requirement(part, roots, depth+1)
            if node is None:
                for animal in ('chicken', 'pork', 'beef'):
                    if parts[0].startswith(animal+' '):
                        node = parse_requirement(animal+' '+part, roots, depth+1)
                        if node:
                            break
            parsed.append(node)
        if all(parsed):
            return {'all_of': parsed}
    return None


def context_resolution(line, recipes, roots):
    text = tidy(line)
    # Unit evidence distinguishes meat chunks from seasoning without using the
    # quantity-stripped group, which has lost precisely this information.
    match = re.fullmatch(r'[\d ./]+\s*(?:kilograms?|kilos?|kg|grams?|g|lbs?\.?|pounds?)\s+(beef|pork) cubes', text)
    if match:
        return all_ids([match[1]+'_meat_cube']), 'Explicit mass unit and meat-cube phrase retained.'
    if re.fullmatch(r'[\d ./]+\s*(?:pieces?\s+)?(?:beef|pork) cube(?: optional)?', text):
        animal = 'beef' if 'beef' in text else 'pork'
        evidence = all(any(re.search(r'\b(?:dissolve|bouillon|seasoning|add.*cube)', instruction, re.I)
                           for instruction in recipe['instructions']) for recipe in recipes)
        if recipes and evidence:
            return all_ids([animal+'_seasoning_cube']), 'Count-unit cube with supporting instruction context in every occurrence.'
    return None, None


def build(recipes, approved, groups, context_corrections=()):
    roots = dict(BASE)
    roots.update({tidy(name): ids[0] for name, ids in EXACT.items() if len(ids) == 1})
    for group in groups:
        if group['decision'] == 'approve' and ';' not in group['approved_ingredients']:
            roots[tidy(group['lookup_text'])] = group['approved_ingredients']
    references = {}
    for recipe in recipes:
        for index, line in enumerate(recipe['full_ingredients']):
            references.setdefault(line.casefold(), []).append((recipe, index))
    corrections = {}
    for correction in context_corrections:
        line = correction['ingredient_line']
        refs = references.get(line, [])
        if set(correction['recipe_ids']) != {recipe['id'] for recipe, _ in refs}:
            raise ValueError('Contextual correction recipe scope changed: '+line)
        for recipe, _ in refs:
            actual = hashlib.sha256(json.dumps(recipe['full_ingredients'],ensure_ascii=False).encode('utf-8')).hexdigest()
            if actual != correction['recipe_ingredient_sha256'][recipe['id']]:
                raise ValueError('Contextual correction is stale: '+line)
        if line in corrections:
            raise ValueError('Duplicate contextual correction')
        corrections[line] = correction
    resolutions = {}
    for line, refs in references.items():
        if line in approved:
            resolutions[line] = {'status': 'resolved', 'requirement': all_ids(approved[line]['canonical_ingredients']),
                                 'method': approved[line].get('review_type', 'owner_recorded_review'),
                                 'reviewer': approved[line]['reviewed_by'], 'basis': 'Preserved accepted mapping.'}
            continue
        if line in corrections:
            resolutions[line] = dict(corrections[line], status='resolved')
            continue
        text = tidy(line)
        equipment_text = strip_amount(text)
        if equipment_text in EQUIPMENT:
            resolutions[line] = {'status': 'non_ingredient', 'method': 'automated_context_review',
                                 'equipment_id': EQUIPMENT[equipment_text],
                                 'basis': 'Explicit equipment/container entry; retained separately from food requirements.'}
            continue
        if text in {'cooking procedure', 'marinade ingredients', 'sauce ingredients', 'basting ingredients'}:
            resolutions[line] = {'status': 'non_ingredient', 'method': 'automated_context_review',
                                 'basis': 'Section heading, not an ingredient. Original source row retained.'}
            continue
        if text in {'to taste', 'beaten', 'quartered', 'finely diced', 'minced',
                    'finely chopped', 'peeled and finely minced', 'juiced',
                    'adjustable to taste', 'plus extra for topping'}:
            # Retain attachment references instead of silently deleting fragments.
            if all(index > 0 for recipe, index in refs):
                resolutions[line] = {'status': 'non_ingredient', 'method': 'automated_context_review',
                                     'basis': 'Detached preparation/usage note. Kept as a note on the preceding source line.',
                                     'attached_to': [{'recipe_id': recipe['id'], 'line_number': index}
                                                     for recipe, index in refs]}
                continue
        requirement, basis = context_resolution(line, [r for r, _ in refs], roots)
        if requirement is None:
            requirement = parse_requirement(line, roots)
            basis = 'Explicit ingredient expression; generic varieties stay unspecified; alternatives remain any_of.'
        resolutions[line] = {'status': 'resolved' if requirement else 'unresolved',
                             'method': 'automated_structured_normalization',
                             'reviewer': 'Codex automated rules (user-authorized)',
                             'requirement': requirement,
                             'basis': basis if requirement else 'No complete conservative parse; inspect source and recipe context.'}
    return resolutions


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit('Use a new versioned resolution output directory.')
    paths = [DATA/'recipes.cleaned.json', DATA/'ingredient_mapping.approved.json', DATA/'ingredient_groups.review.csv']
    recipes, approved = [json.loads(p.read_text(encoding='utf-8')) for p in paths[:2]]
    with paths[2].open(encoding='utf-8-sig', newline='') as stream:
        groups = list(csv.DictReader(stream))
    correction_path = ROOT/'data/ingredient_context_corrections.json'
    corrections = []
    if correction_path.is_file():
        corrections = json.loads(correction_path.read_text(encoding='utf-8'))
        paths.append(correction_path)
    resolutions = build(recipes, approved, groups, corrections)
    counts = Counter(line.casefold() for r in recipes for line in r['full_ingredients'])
    recipes_by_line = {}
    for recipe in recipes:
        for line in set(x.casefold() for x in recipe['full_ingredients']):
            recipes_by_line.setdefault(line, []).append(recipe)
    occurrences = Counter()
    for line, resolution in resolutions.items():
        occurrences[resolution['status']] += counts[line]
    report = {'created_at': datetime.now(timezone.utc).isoformat(), 'recipes': len(recipes),
              'total_distinct_lines': len(resolutions), 'total_occurrences': sum(counts.values()),
              'occurrence_status_counts': dict(occurrences),
              'resolved_ingredient_occurrence_percent': round(100*occurrences['resolved']/sum(counts.values()), 2),
              'unresolved_recipe_count': sum(any(resolutions[line.casefold()]['status']=='unresolved' for line in r['full_ingredients']) for r in recipes),
              'model_training_performed': False, 'ready_for_training': False,
              'note': 'All records examined. Resolved identity coverage is separate from source issues, roles, and ranking-label readiness.'}
    args.output.mkdir(parents=True)
    for name, data in [('requirements.json', resolutions), ('report.json', report)]:
        (args.output/name).write_text(json.dumps(data, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    with (args.output/'unresolved.csv').open('x', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=['ingredient_line', 'occurrences', 'recipe_ids', 'recipe_examples', 'reason'])
        writer.writeheader()
        for line, resolution in resolutions.items():
            if resolution['status']=='unresolved':
                examples = recipes_by_line[line]
                writer.writerow({'ingredient_line': line, 'occurrences': counts[line],
                                 'recipe_ids': ' | '.join(r['id'] for r in examples),
                                 'recipe_examples': ' | '.join(r['name'] for r in examples[:3]), 'reason': resolution['basis']})
    manifest = {'input_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
                'rule_sha256': {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['resolve_ingredient_requirements.py','contextual_normalization.py','propose_batch_mappings.py']},
                'output_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in args.output.iterdir() if p.is_file()}}
    (args.output/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
