"""Protect full-corpus retention and the boundary between proposals and approvals."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from prepare_full_dataset import assemble, read


class FullPreparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = {
            "recipes": read(ROOT / "data/processed/recipes.cleaned.json"),
            "proposals": read(ROOT / "data/processed/ingredient_mapping.proposed.json"),
            "approved": read(ROOT / "data/processed/ingredient_mapping.approved.json"),
            "role_reviews": read(ROOT / "data/processed/recipes.pilot.roles.json"),
            "source_checks": read(ROOT / "data/source_checks.json"),
        }

    def test_every_recipe_and_source_row_is_retained(self):
        corpus, mappings, roles, sources, report = assemble(**self.inputs)
        original = self.inputs["recipes"]
        self.assertEqual({r["id"] for r in original}, {r["id"] for r in corpus})
        self.assertEqual(sum(len(r["sources"]) for r in original), report["source_rows_preserved"])
        self.assertEqual(sum(len(r["full_ingredients"]) for r in original), report["ingredient_line_occurrences"])
        self.assertEqual(len(sources), len(original))
        self.assertTrue(all(not r["ready_for_training"] for r in corpus))

    def test_proposals_are_never_promoted_to_approved_labels(self):
        inputs = dict(self.inputs, approved={}, role_reviews=[])
        corpus, mappings, roles, sources, report = assemble(**inputs)
        self.assertEqual(report["approved_mapping_occurrences"], 0)
        self.assertTrue(all(not row["decision"] for row in mappings))
        self.assertTrue(all(not row["role"] and not row["decision"] for row in roles))
        self.assertTrue(all(not r["approved_ingredient_ids"] for r in corpus))

    def test_changed_source_checked_ingredients_require_new_comparison(self):
        inputs = deepcopy(self.inputs)
        checked = inputs["source_checks"][0]["recipe_id"]
        recipe = next(r for r in inputs["recipes"] if r["id"] == checked)
        recipe["full_ingredients"] = list(reversed(recipe["full_ingredients"]))
        with self.assertRaisesRegex(ValueError, "changed after source comparison"):
            assemble(**inputs)

    def test_role_overlap_is_rejected(self):
        inputs = deepcopy(self.inputs)
        recipe = inputs["role_reviews"][0]
        recipe["supporting"].append(recipe["major"][0])
        with self.assertRaisesRegex(ValueError, "roles overlap"):
            assemble(**inputs)

    def test_stale_or_incomplete_vocabulary_is_rejected(self):
        inputs = dict(self.inputs, proposals=self.inputs["proposals"][:-1])
        with self.assertRaisesRegex(ValueError, "vocabulary does not match"):
            assemble(**inputs)

    def test_deferred_decision_is_preserved_without_becoming_an_approval(self):
        line = next(p["ingredient_line"] for p in self.inputs["proposals"]
                    if p["ingredient_line"] not in self.inputs["approved"])
        _, mappings, _, _, _ = assemble(**self.inputs, deferred_reviews=[{
            "ingredient_line": line, "decision": "defer", "notes": "Needs clarification"}])
        row = next(r for r in mappings if r["ingredient_line"] == line)
        self.assertEqual(row["decision"], "defer")
        self.assertEqual(row["approved_ingredients"], "")
        self.assertEqual(row["notes"], "Needs clarification")

    def test_structured_alternative_is_preserved_without_flattening(self):
        resolutions = {p['ingredient_line']: {'status': 'unresolved', 'requirement': None,
                        'basis': 'Test fixture'} for p in self.inputs['proposals']}
        line = next(p['ingredient_line'] for p in self.inputs['proposals'] if p['ingredient_line'] not in self.inputs['approved'])
        expression = {'any_of': [{'ingredient_id': 'water'}, {'ingredient_id': 'beef_broth'}]}
        resolutions[line] = {'status': 'resolved', 'requirement': expression, 'basis': 'Explicit alternative fixture'}
        corpus, _, _, _, report = assemble(**self.inputs, requirement_resolutions=resolutions)
        annotations = [a for r in corpus for a in r['ingredients'] if a['original_line'].casefold() == line]
        self.assertTrue(annotations)
        self.assertTrue(all(a['requirement_resolution']['requirement'] == expression for a in annotations))
        self.assertTrue(all(a['canonical_ingredients'] == [] for a in annotations))
        self.assertEqual(report['structured_normalization_occurrence_counts']['resolved'], len(annotations))
        self.assertTrue(all(not r['ready_for_training'] for r in corpus))

    def test_empty_structured_requirement_is_rejected(self):
        resolutions = {p['ingredient_line']: {'status': 'unresolved', 'requirement': None,
                        'basis': 'Test fixture'} for p in self.inputs['proposals']}
        resolutions[next(iter(resolutions))] = {'status': 'resolved', 'requirement': {'any_of': []}, 'basis': 'Invalid fixture'}
        with self.assertRaisesRegex(ValueError, 'Invalid requirement children'):
            assemble(**self.inputs, requirement_resolutions=resolutions)


if __name__ == "__main__":
    unittest.main()
