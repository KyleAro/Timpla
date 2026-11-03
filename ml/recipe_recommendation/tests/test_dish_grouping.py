import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import quick_train


class DishGroupingTests(unittest.TestCase):
    def test_group_before_limit_and_choose_better_supporting_fit(self):
        families = __import__('json').loads((quick_train.ROOT/'data/recipe_families.json').read_text())
        ids = [key for key, value in families.items() if value == 'tortang talong'][:2]
        rows = [dict(id=ids[0], name='Variant A', essential={'ingredient_id': 'egg'}, supporting=['garlic'], all_food=['egg', 'garlic'], source_urls=[]),
                dict(id=ids[1], name='Variant B', essential={'ingredient_id': 'egg'}, supporting=[], all_food=['egg'], source_urls=[]),
                dict(id='other', name='Other dish', essential={'ingredient_id': 'egg'}, supporting=[], all_food=['egg'], source_urls=[])]
        class Booster:
            def predict(self, vectors):
                return [1, 1, .5]
        with patch.object(quick_train, 'load_model', return_value=(rows, Booster())):
            result = quick_train.recommend(Path('.'), ['egg'], limit=2)
        self.assertEqual([r['id'] for r in result], [ids[1], 'other'])


if __name__ == '__main__':
    unittest.main()
