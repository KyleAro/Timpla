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


if __name__ == '__main__':
    unittest.main()
