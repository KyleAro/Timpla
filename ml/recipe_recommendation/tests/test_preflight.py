"""Preflight must report incomplete data without training or changing files."""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from preflight import check_preparation


class PreflightTests(unittest.TestCase):
    def test_full_snapshot_cannot_be_mistaken_for_ready_training_data(self):
        with patch('ranker.train', side_effect=AssertionError('Must never train')):
            report = check_preparation(ROOT/'data/preparation/v1')
        self.assertFalse(report['data_and_dependency_checks_passed'])
        self.assertFalse(report['model_training_performed'])
        self.assertEqual(report['recipes'], 2074)
        self.assertEqual(report['pending_recipe_counts']['ingredient_mapping_incomplete'], 2070)
        self.assertIn('relevance.review.csv', report['missing_supervised_training_files'])

    def test_missing_snapshot_is_a_clear_validation_failure(self):
        with tempfile.TemporaryDirectory() as folder:
            report = check_preparation(folder)
            self.assertEqual(list(Path(folder).iterdir()), [])
        self.assertFalse(report['data_and_dependency_checks_passed'])
        self.assertTrue(any('Data validation:' in b for b in report['blockers']))


if __name__ == '__main__':
    unittest.main()
