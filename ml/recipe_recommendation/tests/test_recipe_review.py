"""Protect recipe review scope, logical choices, owner decisions and provenance."""
from copy import deepcopy
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from prepare_recipe_review import build_drafts, propose_role
from merge_recipe_review import merge, export


def fixture(owner=False):
    expression = {'any_of': [{'ingredient_id': 'chicken_breast'}, {'ingredient_id': 'chicken_thigh'}]}
    recipe = {'id': 'r1', 'name': 'Chicken Adobo', 'full_ingredients': ['chicken breast or thigh', 'soy sauce', 'vinegar'],
              'instructions': ['Simmer chicken with soy sauce and vinegar.']}
    annotations = [{'original_line': recipe['full_ingredients'][0], 'requirement_resolution': {'status': 'resolved', 'requirement': expression}}]
    annotations.extend({'original_line': line, 'requirement_resolution': {'status': 'resolved', 'requirement': {'ingredient_id': identity}}}
                       for line,identity in [('soy sauce','soy_sauce'), ('vinegar','vinegar')])
    prior = {'id': 'r1', 'ingredients': annotations,
             'ingredient_role_review': {'status': 'approved', 'reviewed_by': 'Fixture owner', 'reviewed_at': 'fixture'} if owner else None,
             'major': ['chicken_breast','chicken_thigh','soy_sauce','vinegar'] if owner else [],
             'supporting': [], 'optional': [], 'quality_flags': [], 'source_urls': [],
             'original_source_rows': [{'collection': 'fixture', 'csv_record_number': 1}], 'source_check': None}
    draft = build_drafts([recipe], [prior])[0]
    decision = {'recipe_id': 'r1', 'cuisine_scope': {'decision': 'proposed_in_scope', 'basis': 'Adobo fixture'},
                'internal_completeness': {'status': 'no_obvious_gap', 'basis': 'Same listed items appear in the supplied method', 'issues': []},
                'role_overrides': [], 'dependency_notes': [], 'notes': [],
                'annotation_type': 'ai_recipe_semantic_review', 'reviewer': 'AI fixture'}
    return recipe, prior, draft, decision


class RecipeReviewTests(unittest.TestCase):
    def test_defining_sauces_are_not_universally_supporting(self):
        for identity in ['soy_sauce','vinegar']:
            self.assertEqual(propose_role('Chicken Adobo', identity, identity)[0], 'essential')
        self.assertEqual(propose_role('Fried Fish', 'oil', 'cooking_oil')[0], 'supporting')
        self.assertEqual(propose_role('Butter Cake', 'butter', 'butter')[0], 'essential')
        self.assertEqual(propose_role('Chicken Adobo', 'garlic optional', 'garlic')[0], 'optional')

    def test_alternatives_survive_draft_merge_and_export(self):
        recipe, prior, draft, decision = fixture()
        records = merge([draft], [[draft]], [[decision]])
        self.assertEqual(records[0]['lines'][0]['requirement'], prior['ingredients'][0]['requirement_resolution']['requirement'])
        self.assertEqual([r['path'] for r in records[0]['lines'][0]['roles']], [['any_of',0],['any_of',1]])
        with tempfile.TemporaryDirectory() as folder:
            report = export(Path(folder), records)
            self.assertEqual(report['new_human_approvals'], 0)
            self.assertFalse(report['ready_for_training'])
            self.assertEqual(report['original_source_rows_preserved'], 1)

    def test_existing_owner_roles_cannot_be_replaced(self):
        _, _, draft, decision = fixture(owner=True)
        decision['role_overrides'] = [{'line_number':1,'ingredient_id':'chicken_breast', 'role':'supporting','basis':'Bad override'}]
        with self.assertRaisesRegex(ValueError,'owner-approved'):
            merge([draft],[[draft]],[[decision]])
        self.assertEqual(draft['prior_owner_role_review']['reviewed_by'], 'Fixture owner')

    def test_missing_or_duplicate_recipes_and_changed_partitions_fail(self):
        _, _, draft, decision = fixture()
        for judgments in [[],[decision,decision]]:
            with self.assertRaisesRegex(ValueError,'exactly once'):
                merge([draft],[[draft]],[judgments])
        changed = deepcopy(draft)
        changed['instructions'].append('Changed source text')
        with self.assertRaisesRegex(ValueError,'frozen draft'):
            merge([draft],[[changed]],[[decision]])

    def test_overrides_need_real_food_leaf_and_gap_needs_evidence(self):
        _, _, draft, decision = fixture()
        decision['role_overrides'] = [{'line_number':1,'ingredient_id':'pork','role':'essential','basis':'Invented identity'}]
        with self.assertRaisesRegex(ValueError,'existing food leaf'):
            merge([draft],[[draft]],[[decision]])
        decision['role_overrides'] = []
        decision['internal_completeness']['status'] = 'gap_identified'
        with self.assertRaisesRegex(ValueError,'specific evidence'):
            merge([draft],[[draft]],[[decision]])

    def test_proposed_scope_exclusion_does_not_delete_or_approve_recipe(self):
        _, _, draft, decision = fixture()
        decision['cuisine_scope'] = {'decision':'proposed_out_of_scope','basis':'Fixture for a proposed exclusion'}
        records = merge([draft],[[draft]],[[decision]])
        self.assertEqual(len(records),1)
        self.assertEqual(records[0]['human_review_status'],'pending')
        self.assertFalse(records[0]['ready_for_training'])


if __name__ == '__main__':
    unittest.main()
