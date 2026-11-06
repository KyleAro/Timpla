import sys
from pathlib import Path
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from preference_filters import eligible, contains_excluded
import quick_train


class PreferenceTests(unittest.TestCase):
    def test_common_allergen_derivatives(self):
        for allergy, food in [('Peanuts', 'peanut_butter'), ('Shellfish', 'shrimp_paste'),
                              ('Eggs', 'mayonnaise'), ('Dairy', 'cheddar_cheese'),
                              ('Soy', 'soy_sauce'), ('Wheat', 'bread_crumbs')]:
            with self.subTest(allergy=allergy):
                self.assertFalse(eligible({'all_food': [food]}, [allergy]))
        self.assertTrue(eligible({'all_food': ['eggplant', 'salt']}, ['Peanuts']))
        self.assertTrue(eligible({'all_food': ['eggplant', 'salt']}, ['Eggs']))
        self.assertFalse(eligible({'all_food': ['duck_egg']}, ['Eggs']))

    def test_exclusions_match_ingredient_forms(self):
        self.assertTrue(contains_excluded(['pork_belly'], ['pork']))
        self.assertTrue(contains_excluded(['garlic_powder'], ['garlic']))
        self.assertFalse(contains_excluded(['eggplant'], ['egg']))

    def test_unknown_allergy_and_diets_require_review(self):
        recipe = {'all_food': ['rice']}
        self.assertFalse(eligible(recipe, ['Sesame']))
        self.assertFalse(eligible(recipe, diet='Halal'))
        self.assertFalse(eligible(recipe, diet='Vegetarian'))
        recipe.update(verified_free_from=['sesame'], verified_diets=['Vegetarian'])
        self.assertTrue(eligible(recipe, ['Sesame'], 'Vegetarian'))
        self.assertFalse(eligible(recipe, ['Sesame'], 'Halal'))

    def test_filters_supporting_and_optional_foods_before_ranking(self):
        class Booster:
            def predict(self, rows):
                self.rows = rows
                return [1] * len(rows)
        booster = Booster()
        recipes = [dict(id=name, name=name, essential={'ingredient_id': 'eggplant'},
                        supporting=[], all_food=foods, source_urls=[])
                   for name, foods in [('blocked', ['eggplant', 'peanut_oil']),
                                       ('allowed', ['eggplant', 'salt'])]]
        with patch.object(quick_train, 'load_model', return_value=(recipes, booster)):
            results = quick_train.recommend(Path('.'), ['eggplant'], allergies=['Peanuts'])
        self.assertEqual([row['id'] for row in results], ['allowed'])
        self.assertEqual(results[0]['ingredient_match'], {'matched': 1, 'total': 2, 'percentage': 50})
        self.assertEqual(len(booster.rows), 1)

    def test_sinigang_manual_names_and_partial_results_keep_restrictions(self):
        import json
        catalog = json.loads((Path(__file__).resolve().parents[1] / 'models/quick_v1/catalog.json').read_text(encoding='utf-8'))
        recipe = next(row for row in catalog if row['name'] == 'Sinigang na Baboy')
        class Booster:
            def predict(self, rows): return [1] * len(rows)
        with patch.object(quick_train, 'load_model', return_value=([recipe], Booster())):
            inventory = ['Pork spare ribs', 'Gabi', 'Labanos', 'Siling haba', 'Sitaw', 'Talong', 'Okra', 'Sampalok', 'Pechay']
            result = quick_train.recommend(Path('.'), inventory)
            self.assertEqual(result[0]['name'], 'Sinigang na Baboy')
            self.assertEqual(result[0]['missing_essential'], [])
            partial = quick_train.recommend(Path('.'), ['Pork spare ribs', 'Gabi', 'Labanos', 'Sitaw', 'Talong', 'Okra'])
            self.assertTrue(partial[0]['missing_essential'])
            self.assertEqual(quick_train.recommend(Path('.'), inventory, excluded=['Baboy']), [])
            self.assertEqual(quick_train.recommend(Path('.'), inventory, excluded=['Patis']), [])
            self.assertEqual(quick_train.recommend(Path('.'), inventory, diet='Vegetarian'), [])


    def test_actual_manual_inventory_discovers_sinigang_without_claiming_complete(self):
        import json
        catalog = json.loads((Path(__file__).resolve().parents[1] / 'models/quick_v1/catalog.json').read_text(encoding='utf-8'))
        recipe = next(row for row in catalog if row['name'] == 'Sinigang na Baboy with Gabi')
        class Booster:
            def predict(self, rows): return [1] * len(rows)
        with patch.object(quick_train, 'load_model', return_value=(catalog, Booster())):
            result = quick_train.recommend(Path('.'), ['pork', 'white radish', 'kangkong', 'onion', 'siling haba'], limit=20)
        self.assertTrue(any('sinigang na baboy' in row['name'].lower() for row in result[:3]))
        match = next(row for row in result if row['name'] == 'Sinigang na Baboy with Gabi')
        self.assertIn('pork_belly', match['missing_essential'])
        self.assertNotIn('radish', match['missing_essential'])
        self.assertNotIn('kangkong_leaves', match['missing_essential'])


    def test_single_ingredient_discovers_recipes_and_preserves_missing_cuts(self):
        class Booster:
            def predict(self, rows): return [1] * len(rows)
        def recipe(name, foods):
            return dict(id=name, name=name, essential={'all_of': [{'ingredient_id': food} for food in foods]},
                        all_food=foods, supporting=[], source_urls=[])
        recipes = [recipe('chicken dish', ['chicken_breast', 'garlic']),
                   recipe('pork dish', ['pork_belly', 'onion']),
                   recipe('stock dish', ['chicken_stock', 'rice']),
                   recipe('vegetable dish', ['eggplant', 'egg'])]
        with patch.object(quick_train, 'load_model', return_value=(recipes, Booster())):
            for name in ['chicken', 'manok', 'chicken_generic']:
                result = quick_train.recommend(Path('.'), [name])
                self.assertEqual([row['id'] for row in result], ['chicken dish'])
                self.assertIn('chicken_breast', result[0]['missing_essential'])
            result = quick_train.recommend(Path('.'), ['talong'])
            self.assertEqual([row['id'] for row in result], ['vegetable dish'])
            self.assertEqual(result[0]['missing_essential'], ['egg'])
            self.assertEqual(quick_train.recommend(Path('.'), ['chicken'], excluded=['chicken']), [])
            self.assertEqual(quick_train.recommend(Path('.'), ['unknown ingredient']), [])
            self.assertEqual(quick_train.recommend(Path('.'), []), [])



if __name__ == '__main__':
    unittest.main()
