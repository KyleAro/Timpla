"""Draft full-corpus recipe requirements for review; never approve or train."""
import argparse
from collections import Counter
from copy import deepcopy
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

from prepare_full_dataset import digest, read, write_json

ROOT = Path(__file__).resolve().parent
ROLES = {'essential', 'supporting', 'optional'}
PANTRY = re.compile(r'(?:^|_)(?:salt|pepper|peppercorn|oil|water|sugar|vinegar|soy_sauce|fish_sauce|oyster_sauce|seasoning|bouillon|broth|stock|cube|butter|margarine|mayonnaise|ketchup|sauce|juice)(?:_|$)')
AROMATICS = {'onion', 'red_onion', 'white_onion', 'yellow_onion', 'garlic', 'ginger',
             'bay_leaf', 'dried_bay_leaf', 'tomato', 'spring_onion', 'spring_onion_leaf',
             'red_bell_pepper', 'green_bell_pepper', 'bell_pepper', 'black_pepper',
             'pepper_unspecified', 'ground_pepper_unspecified', 'annatto_seed', 'chicken_broth'}
BAKING = re.compile(r'\b(?:cake|muffin|cookie|bread|pandesal|pandesal|puto|kutsinta|bibingka|biko|suman|pudding|flan|dessert|ice cream|popsicle|pancake|brownie|polvoron|tart|pie|doughnut|donut|maja|yema|pastillas|kakanin|halaya)\b')
BAKING_CORE = re.compile(r'(?:sugar|flour|milk|cream|egg|butter|margarine|gelatin|agar|baking_powder|baking_soda|yeast|chocolate|cocoa|starch|rice|sweetener|honey)')


def food_nodes(expression, path=()):
    if not expression:
        return
    key = next(iter(expression))
    if key == 'ingredient_id':
        yield list(path), expression[key]
    elif key in {'all_of', 'any_of'}:
        for index, child in enumerate(expression[key]):
            yield from food_nodes(child, path + (key, index))


def defining_role(name, identity):
    """Finite proposals; these rules are not independent culinary validation."""
    if re.search(r'\badobo\b|adobong', name) and any(x in identity for x in ['vinegar', 'soy_sauce']):
        return 'Adobo variant explicitly includes this defining braising seasoning.'
    if re.search(r'paksiw|kilawin|kinilaw', name) and any(x in identity for x in ['vinegar', 'calamansi', 'lime_juice', 'lemon_juice']):
        return 'Acid is part of the named sour/cured preparation.'
    if re.search(r'sinigang', name) and any(x in identity for x in ['tamarind', 'sinigang', 'kamias', 'guava', 'santol', 'miso']):
        return 'This is an explicitly listed souring/base ingredient of the named sinigang variant.'
    if re.search(r'ginataan|ginataang|gata\b|bicol express|laing', name) and 'coconut' in identity and ('milk' in identity or 'cream' in identity):
        return 'Coconut milk/cream defines this named coconut-based preparation.'
    if re.search(r'binagoongan|binagoongang', name) and ('shrimp_paste' in identity or 'bagoong' in identity):
        return 'The named dish explicitly depends on fermented shrimp paste.'
    if re.search(r'bistek|beef steak tagalog', name) and any(x in identity for x in ['soy_sauce', 'calamansi', 'lemon_juice', 'lime_juice', 'onion']):
        return 'Listed citrus/soy/onion component defines the named bistek preparation.'
    if re.search(r'sinangag|garlic fried rice', name) and 'garlic' in identity:
        return 'Garlic is defining for sinangag/garlic fried rice.'
    if re.search(r'tinola|tinolang', name) and 'ginger' in identity:
        return 'Ginger is a defining aromatic of this tinola proposal.'
    # A title explicitly naming a condiment/aromatic prevents universal pantry treatment.
    label = identity.replace('_', ' ')
    for food in ['garlic', 'onion', 'ginger', 'tomato', 'coconut', 'soy sauce', 'vinegar',
                 'miso', 'peanut', 'cheese', 'butter', 'milk', 'cream', 'chili', 'calamansi']:
        if re.search(r'\b' + re.escape(food) + r'\b', name) and re.search(r'\b' + re.escape(food) + r'\b', label):
            return 'This ingredient is explicitly named in the recipe title; proposed defining role requires review.'
    if re.search(r'\bchili garlic oil\b|\bchili oil\b', name) and ('oil' in identity or 'chili' in identity):
        return 'Oil/chili is the product itself in this condiment recipe.'
    return None


def propose_role(name, original, identity):
    # Optional is a source assertion, never inferred merely from quantity or seasoning category.
    if re.search(r'\boptional\b|\bopsyonal\b|\bif desired\b|\bif available\b', original, re.I):
        return 'optional', 'Source explicitly marks this line optional/conditional; check scope over compound choices.'
    reason = defining_role(name.casefold(), identity)
    if reason:
        return 'essential', reason
    if BAKING.search(name.casefold()) and BAKING_CORE.search(identity):
        return 'essential', 'Proposed structural/sweetening ingredient of a baking/dessert recipe; omission is not assumed.'
    if identity in AROMATICS or PANTRY.search(identity):
        return 'supporting', 'Proposed supporting aromatic, cooking medium, liquid or seasoning; availability must still be confirmed.'
    return 'essential', 'Conservative substantive-food default; review whether this is defining, supporting, or an explicit garnish.'


def build_drafts(recipes, prepared):
    snapshots = {r['id']: r for r in prepared}
    if set(snapshots) != {r['id'] for r in recipes}:
        raise ValueError('Preparation must cover the exact full corpus')
    result = []
    for recipe in recipes:
        prior = snapshots[recipe['id']]
        if [a['original_line'] for a in prior['ingredients']] != recipe['full_ingredients']:
            raise ValueError('Ingredient lines changed after normalization')
        owner_review = prior.get('ingredient_role_review')
        owner = {value: ('essential' if role == 'major' else role)
                 for role in ('major', 'supporting', 'optional') for value in prior[role]} if owner_review else {}
        lines = []
        for index, annotation in enumerate(prior['ingredients'], start=1):
            resolution = annotation['requirement_resolution']
            if resolution['status'] not in {'resolved', 'non_ingredient'}:
                raise ValueError('Finish ingredient normalization before drafting recipe roles')
            expression = deepcopy(resolution.get('requirement'))
            roles = []
            for path, identity in food_nodes(expression):
                role, basis = propose_role(recipe['name'], annotation['original_line'], identity)
                if owner_review:
                    if identity not in owner:
                        raise ValueError('Existing owner roles no longer cover the normalized identities')
                    role, basis = owner[identity], 'Preserved existing owner-approved recipe-specific role.'
                roles.append({'path': path, 'ingredient_id': identity, 'proposed_role': role, 'basis': basis})
            lines.append({'line_number': index, 'original_line': annotation['original_line'],
                          'normalization_status': resolution['status'], 'requirement': expression,
                          'roles': roles, 'terminology_review_required': bool(resolution.get('terminology_review_required')),
                          'source_gloss': resolution.get('source_gloss')})
        flags = list(prior['quality_flags'])
        if not recipe.get('instructions'):
            flags.append('instructions_missing')
        if not any(role['proposed_role'] == 'essential' for line in lines for role in line['roles']):
            flags.append('no_proposed_essential_ingredient')
        result.append({'id': recipe['id'], 'name': recipe['name'], 'lines': lines,
                       'instructions': recipe.get('instructions', []),
                       'source_urls': prior['source_urls'], 'original_source_rows': prior['original_source_rows'],
                       'ingredient_lines_sha256': digest(recipe['full_ingredients']),
                       'instructions_sha256': digest(recipe.get('instructions', [])),
                       'prior_owner_role_review': deepcopy(owner_review),
                       'preserved_owner_roles': {k: deepcopy(prior[k]) for k in ('major','supporting','optional')} if owner_review else None,
                       'preserved_source_check': deepcopy(prior['source_check']),
                       'role_annotation_status': 'owner_approved_preserved' if owner_review else 'automated_draft_pending_semantic_review',
                       'cuisine_scope': {'decision': 'pending', 'basis': 'Dataset membership alone does not establish Filipino cuisine scope.'},
                       'internal_completeness': {'status': 'pending', 'basis': 'Compare the supplied ingredient list with its own instructions; original source checking is separate.'},
                       'quality_flags': sorted(set(flags)), 'human_review_status': 'pending' if not owner_review else 'existing_role_approval_only',
                       'ready_for_training': False})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit('Use a new review folder; reviewer work is never overwritten')
    paths = [ROOT/'data/processed/recipes.cleaned.json', ROOT/'data/preparation/v6/recipes.prepared.json']
    result = build_drafts(*[read(p) for p in paths])
    args.output.mkdir(parents=True)
    write_json(args.output/'recipes.draft.json', result)
    # Deterministic balanced partitions; each source recipe belongs to exactly one reviewer batch.
    batches = [[], [], []]
    loads = [0, 0, 0]
    for record in sorted(result, key=lambda r: (-len(r['lines']), r['id'])):
        target = min(range(3), key=lambda i: (loads[i], len(batches[i]), i))
        batches[target].append(record)
        loads[target] += len(record['lines'])
    for i, batch in enumerate(batches, 1):
        write_json(args.output/f'partition_{i:02d}.json', batch)
    report = {'recipes': len(result), 'ingredient_line_occurrences': sum(len(r['lines']) for r in result),
              'existing_owner_role_reviews_preserved': sum(bool(r['prior_owner_role_review']) for r in result),
              'proposed_role_leaf_counts': dict(Counter(role['proposed_role'] for r in result for line in r['lines'] for role in line['roles'])),
              'partition_recipe_counts': [len(b) for b in batches], 'partition_line_counts': loads,
              'annotation_status': 'draft_pending_semantic_review', 'ready_for_training': False, 'model_training_performed': False}
    write_json(args.output/'draft_report.json', report)
    write_json(args.output/'manifest.json', {'created_at': datetime.now(timezone.utc).isoformat(),
               'input_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
               'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               'output_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in args.output.iterdir() if p.is_file()},
               'model_training_performed': False})
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
