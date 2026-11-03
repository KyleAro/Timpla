import csv
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from finish_normalization import expand, read_json
from propose_batch_mappings import propose


class AutomaticNormalizationTests(unittest.TestCase):
    def test_alternatives_and_unspecified_pepper_never_get_forced_ids(self):
        for text in ['salt and pepper', 'water or chicken broth', 'beef powder or 1 beef cube',
                     'lemon or calamansi juice', 'ground pepper', '', 'cooking procedure']:
            with self.subTest(text=text):
                self.assertEqual(propose(text)[0], [])

    def test_important_states_and_ingredient_types_stay_distinct(self):
        for text, expected in {
            'chicken broth': ['chicken_broth'], 'ground pork': ['ground_pork'],
            'rice cooked': ['cooked_rice'], 'rice uncooked': ['rice'],
            'hard boiled eggs': ['hard_boiled_egg'], 'raw eggs': ['egg'],
            'fresh coconut milk': ['fresh_coconut_milk'], 'coconut milk': ['coconut_milk'],
            'butter melted': ['melted_butter'], 'butter': ['butter'],
            'garlic peeled and diced': ['garlic'],
            '200-gram pack tomato sauce': ['tomato_sauce'],
        }.items():
            with self.subTest(text=text):
                self.assertEqual(propose(text)[0], expected)
        self.assertEqual(propose('chicken boiled')[0], ['boiled_chicken'])
        self.assertNotEqual(propose('chicken boiled')[0], propose('chicken')[0])

    def test_extended_grammar_cannot_discard_unknown_ingredients(self):
        from contextual_normalization import parse_flat
        from propose_batch_mappings import BASE
        self.assertEqual(parse_flat('400-gram pack spaghetti', BASE), ['spaghetti'])
        self.assertEqual(parse_flat('radish labanos peeled and sliced', BASE), ['radish'])
        self.assertEqual(parse_flat('2 and 1/2 tablespoons fish sauce patis', BASE), ['fish_sauce'])
        self.assertEqual(parse_flat('chicken broth with noodles', BASE), [])
        self.assertEqual(parse_flat('onion or garlic', BASE), [])
        self.assertEqual(parse_flat('unknown substance', BASE), [])
        self.assertEqual(parse_flat('whole chicken washed and dried', BASE), ['whole_chicken'])
        self.assertEqual(parse_flat('pork belly skin on', BASE), ['skin_on_pork_belly'])
        self.assertEqual(parse_flat('shrimp heads', BASE), [])
        self.assertEqual(parse_flat('onion chopped with garlic', BASE), [])

    def test_entire_corpus_is_covered_without_overwriting_owner_decisions(self):
        data = ROOT/'data/processed'
        with (data/'ingredient_groups.review.csv').open(encoding='utf-8-sig', newline='') as stream:
            groups = list(csv.DictReader(stream))
        original = read_json(data/'ingredient_mapping.approved.json')
        rows, accepted, exceptions, report = expand(groups,
            read_json(data/'ingredient_groups.members.json'),
            read_json(data/'ingredient_mapping.proposed.json'), original, 'test-only')
        self.assertEqual(len(rows), len(groups))
        for key, record in original.items():
            self.assertEqual(accepted[key], record)
        for before, after in zip(groups, rows):
            if before['decision'].strip():
                self.assertEqual(after, before)
        for key in set(accepted)-set(original):
            self.assertEqual(accepted[key]['review_type'], 'automated_rule_acceptance')
            self.assertNotEqual(accepted[key]['reviewed_by'], 'Kyle')
        self.assertFalse(report['model_training_performed'])

    def test_conflicting_earlier_mapping_is_preserved_and_flagged(self):
        groups = [{'lookup_text': 'garlic', 'decision': '', 'notes': '',
                   'suggested_ingredients': '', 'approved_ingredients': ''}]
        original = {'1 garlic': {'canonical_ingredients': ['garlic_powder'], 'reviewed_by': 'fixture'}}
        rows, accepted, exceptions, report = expand(groups, {'garlic': ['1 garlic', '2 garlic']},
            [{'ingredient_line': '1 garlic', 'lookup_text': 'garlic', 'occurrences': 1},
             {'ingredient_line': '2 garlic', 'lookup_text': 'garlic', 'occurrences': 1}], original, 'test')
        self.assertEqual(accepted, original)
        self.assertEqual(rows[0]['decision'], '')
        self.assertIn('conflicts', exceptions[0]['exception_reason'])


if __name__ == '__main__':
    unittest.main()
