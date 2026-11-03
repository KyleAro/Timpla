"""Protect frozen reviews, contextual meanings, and explicit source problems."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from merge_semantic_review import merge, project, align_decisions
from prepare_full_dataset import assemble, digest


class SemanticReviewTests(unittest.TestCase):
    def setUp(self):
        self.baseline = {'reserved broth': {'status': 'unresolved', 'requirement': None, 'basis': 'Needs context'},
                         'salt': {'status': 'resolved', 'requirement': {'ingredient_id': 'salt'}, 'basis': 'Prior review'}}
        self.batch = [{'ingredient_line': 'reserved broth', 'recipes': [
            {'id': 'a', 'ingredient_lines_sha256': 'hash_a'}, {'id': 'b', 'ingredient_lines_sha256': 'hash_b'}]}]
        self.decision = {'ingredient_line': 'reserved broth', 'status': 'contextual',
                         'annotation_type': 'ai_semantic_annotation', 'reviewer': 'AI semantic annotation',
                         'per_recipe': {
                             'a': {'status': 'resolved', 'requirement': {'ingredient_id': 'chicken_broth'}, 'basis': 'Chicken cooking liquid'},
                             'b': {'status': 'resolved', 'requirement': {'ingredient_id': 'pork_broth'}, 'basis': 'Pork cooking liquid'}}}

    def test_contexts_do_not_become_universal_alternatives(self):
        merged = merge(self.baseline, [self.batch], [[self.decision]])
        self.assertEqual(project(merged['reserved broth'], 'a')['requirement'], {'ingredient_id': 'chicken_broth'})
        self.assertEqual(project(merged['reserved broth'], 'b')['requirement'], {'ingredient_id': 'pork_broth'})
        self.assertEqual(merged['salt'], self.baseline['salt'])
        self.assertEqual(merged['reserved broth']['previous_resolution'], self.baseline['reserved broth'])
        self.assertEqual(self.baseline['reserved broth']['status'], 'unresolved')

    def test_id_alignment_preserves_original_annotation_and_choice(self):
        decision = dict(self.decision, status='resolved', requirement={
            'any_of': [{'ingredient_id': 'taro_root'}, {'ingredient_id': 'cooked_taro'}]}, basis='Explicit choice fixture')
        decision.pop('per_recipe')
        aligned = align_decisions([[decision]], {'aliases': {'taro_root': 'taro'},
                                                'basis': 'Same root identity', 'reviewer': 'AI consistency check'})
        result = aligned[0][0]
        self.assertEqual(result['requirement']['any_of'], [{'ingredient_id': 'taro'}, {'ingredient_id': 'cooked_taro'}])
        self.assertEqual(result['before_identity_alignment'], decision)
        self.assertEqual(decision['requirement']['any_of'][0]['ingredient_id'], 'taro_root')

    def test_omissions_duplicates_and_unknown_contexts_fail(self):
        for rows in [[], [self.decision, self.decision]]:
            with self.assertRaisesRegex(ValueError, 'exactly once'):
                merge(self.baseline, [self.batch], [rows])
        bad = deepcopy(self.decision)
        bad['per_recipe'].pop('b')
        with self.assertRaisesRegex(ValueError, 'exact assigned recipe contexts'):
            merge(self.baseline, [self.batch], [[bad]])

    def test_alternatives_preserved_and_source_problem_not_food(self):
        decision = dict(self.decision, status='resolved', requirement={
            'any_of': [{'ingredient_id': 'water'}, {'ingredient_id': 'chicken_broth'}]}, basis='Explicit either/or')
        decision.pop('per_recipe')
        merged = merge(self.baseline, [self.batch], [[decision]])
        self.assertIn('any_of', merged['reserved broth']['requirement'])
        decision.update(status='source_issue', requirement=None, basis='Source omits liquid identity and instructions do not identify it')
        merged = merge(self.baseline, [self.batch], [[decision]])
        self.assertIsNone(merged['reserved broth']['requirement'])
        self.assertEqual(merged['reserved broth']['status'], 'source_issue')

    def test_source_issue_retains_recipe_and_blocks_normalization_readiness(self):
        recipe = {'id': 'a', 'name': 'Source fixture', 'full_ingredients': ['unknown liquid'],
                  'sources': [{'collection': 'fixture', 'csv_record_number': 1}]}
        resolutions = {'unknown liquid': {'status': 'source_issue', 'requirement': None,
                         'basis': 'Original omits ingredient identity'}}
        corpus, _, _, _, report = assemble([recipe], [{'ingredient_line': 'unknown liquid', 'canonical_ingredients': []}],
                                           {}, [], [], requirement_resolutions=resolutions)
        self.assertEqual(len(corpus), 1)
        self.assertFalse(corpus[0]['requirement_resolution_complete'])
        self.assertFalse(report['ready_for_training'])
        self.assertEqual(report['review_disposition_percent'], 100)
        self.assertEqual(report['structured_identity_resolution_percent'], 0)
        self.assertEqual(report['recipes_with_ingredient_source_issues'], 1)

    def test_stale_context_cannot_be_reused(self):
        recipe = {'id': 'a', 'name': 'Fixture', 'full_ingredients': ['broth'],
                  'sources': [{'collection': 'fixture', 'csv_record_number': 1}]}
        record = {'status': 'resolved', 'requirement': {'ingredient_id': 'chicken_broth'},
                  'basis': 'Original instructions identify chicken broth',
                  'context_ingredient_hashes': {'a': digest(['broth before edit'])}}
        with self.assertRaisesRegex(ValueError, 'changed after semantic annotation'):
            assemble([recipe], [{'ingredient_line': 'broth', 'canonical_ingredients': []}], {}, [], [],
                     requirement_resolutions={'broth': record})

    def test_instruction_changes_invalidate_contextual_meaning(self):
        recipe = {'id': 'a', 'name': 'Fixture', 'full_ingredients': ['broth'], 'instructions': ['Boil pork. Reserve broth.'],
                  'sources': [{'collection': 'fixture', 'csv_record_number': 1}]}
        record = {'status': 'resolved', 'requirement': {'ingredient_id': 'chicken_broth'},
                  'basis': 'Original instructions identify chicken broth',
                  'context_instruction_hashes': {'a': digest(['Boil chicken. Reserve broth.'])}}
        with self.assertRaisesRegex(ValueError, 'instructions changed after semantic annotation'):
            assemble([recipe], [{'ingredient_line': 'broth', 'canonical_ingredients': []}], {}, [], [],
                     requirement_resolutions={'broth': record})


if __name__ == '__main__':
    unittest.main()
