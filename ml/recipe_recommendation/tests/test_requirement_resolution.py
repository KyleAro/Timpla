import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from resolve_ingredient_requirements import parse_requirement, context_resolution, build, leaves, BASE


class RequirementResolutionTests(unittest.TestCase):
    def test_alternatives_remain_alternatives(self):
        result = parse_requirement('water or beef broth', BASE)
        self.assertIn('any_of', result)
        self.assertEqual([leaves(r) for r in result['any_of']], [{'water'}, {'beef_broth'}])

    def test_shared_heads_do_not_turn_broth_into_meat(self):
        result = parse_requirement('beef or pork broth', BASE)
        self.assertEqual(leaves(result), {'beef_broth', 'pork_broth'})
        result = parse_requirement('white or cane vinegar', BASE)
        self.assertEqual(leaves(result), {'white_vinegar', 'cane_vinegar'})

    def test_unspecified_pepper_is_not_assumed_black(self):
        result = parse_requirement('salt and pepper to taste', BASE)
        self.assertEqual(leaves(result), {'salt', 'pepper_unspecified'})
        self.assertEqual(leaves(parse_requirement('ground pepper', BASE)), {'ground_pepper_unspecified'})

    def test_slurry_retains_both_explicit_ingredients(self):
        self.assertEqual(leaves(parse_requirement('cornstarch diluted in 1/2 cup water', BASE)), {'cornstarch', 'water'})

    def test_unknown_or_conflicting_text_stays_unresolved(self):
        for text in ['unknown ingredient', 'chicken broth with unknown powder',
                     'thai chili siling labuyo', 'salt or']:
            self.assertIsNone(parse_requirement(text, BASE), text)

    def test_meat_cube_context_uses_original_units(self):
        result, _ = context_resolution('1 kilo beef cubes', [], BASE)
        self.assertEqual(leaves(result), {'beef_meat_cube'})
        result, _ = context_resolution('2 pork cubes', [{'instructions': ['Dissolve the seasoning cubes in water.']}], BASE)
        # Without explicit evidence in the full count-unit pattern, leave pending.
        self.assertIsNone(result)

    def test_fragment_attaches_to_source_line_without_becoming_food(self):
        recipes = [{'id': 'example', 'full_ingredients': ['2 eggs', 'beaten', 'cooking procedure'], 'instructions': []}]
        data = build(recipes, {}, [])
        self.assertEqual(data['beaten']['status'], 'non_ingredient')
        self.assertEqual(data['beaten']['attached_to'], [{'recipe_id': 'example', 'line_number': 1}])
        self.assertEqual(data['cooking procedure']['status'], 'non_ingredient')
        self.assertEqual(leaves(data['2 eggs']['requirement']), {'egg'})


if __name__ == '__main__':
    unittest.main()
