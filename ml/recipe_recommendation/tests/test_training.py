"""Synthetic engineering smoke test only; never a recipe-quality benchmark."""
import importlib.util
import csv
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import ranker


@unittest.skipUnless(importlib.util.find_spec('lightgbm') and importlib.util.find_spec('sklearn'),
                     'Install requirements.txt to exercise actual training')
class TrainingRoundTripTests(unittest.TestCase):
    def test_synthetic_training_export_and_reload(self):
        recipes=[]
        for i,major in enumerate([['egg'],['egg','tomato'],['egg','tomato','garlic']]):
            recipes.append({'id':f'fixture_{i}','name':f'Synthetic test fixture {i}',
                            'source_url':'https://example.org/synthetic-test-only',
                            'major':major,'supporting':['oil'],'optional':[],'minutes':5*(i+1),
                            'region':'test','reviewed_by':'synthetic test; not real reviews','reviewed_at':'2026-10-28'})
        queries=[]
        for i in range(18):
            split='train' if i<12 else 'validation' if i<15 else 'test'
            queries.append({'id':f'q{i}','available':['egg','tomato','garlic','oil',f'fixture_extra_{i}'],
                            'use_first':['tomato'],'excluded':[],'split':split,
                            'leakage_group':f'fixture_group_{i}','reviewed_by':'synthetic test only'})
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as temp:
            root=Path(temp)
            labels=root/'labels.csv'
            ranker.review_queue(recipes,queries,{},labels)
            with labels.open(newline='') as stream:
                reader=csv.DictReader(stream);fields=reader.fieldnames;rows=list(reader)
            for row in rows:
                row['relevance']={'fixture_0':'0','fixture_1':'2','fixture_2':'3'}[row['recipe_id']]
                row['reviewer']='Synthetic software test labels, not user judgments'
            with labels.open('w',newline='') as stream:
                writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader();writer.writerows(rows)
            output=root/'model'
            metrics=ranker.train(recipes,queries,labels,{},output,[labels])
            self.assertTrue((output/'ranker.txt').is_file())
            self.assertEqual(metrics['test']['query_count'],3)
            result=ranker.recommend(recipes,{'available':['egg','tomato','garlic','oil']},{},output)
            # This verifies a learned nonconstant ordering, not perfect fit or recipe quality.
            self.assertGreater(result[0]['ranking_score'], result[-1]['ranking_score'])
            self.assertTrue(all(isinstance(r['ranking_score'],float) for r in result))
            # Missing major ingredients still block high-scoring candidates after reloading.
            result=ranker.recommend(recipes,{'available':['egg','oil']},{},output)
            self.assertEqual([r['recipe_id'] for r in result],['fixture_0'])
            metadata=json.loads((output/'metadata.json').read_text())
            self.assertEqual(metadata['features'],ranker.FEATURES)
            with self.assertRaisesRegex(ValueError,'existing model'):
                ranker.train(recipes,queries,labels,{},output,[labels])


if __name__=='__main__': unittest.main()
