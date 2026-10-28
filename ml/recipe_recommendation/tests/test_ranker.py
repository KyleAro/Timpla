import csv
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import ranker


class RankerTests(unittest.TestCase):
    def setUp(self):
        # Synthetic unit-test fixtures, never shipped as training recipes or metrics.
        self.aliases={'talong':'eggplant','itlog':'egg'}
        self.recipes=[self.recipe('eggplant-dish',['eggplant','egg']),
                      self.recipe('egg-dish',['egg']),
                      self.recipe('rice-dish',['cooked_rice'])]
        self.query={'available':['talong','itlog'],'use_first':['talong'],'excluded':[]}

    def recipe(self,rid,major):
        return {'id':rid,'name':rid,'source_url':'https://example.org/test-fixture',
                'major':major,'supporting':['oil'],'optional':[],'minutes':10,
                'region':'test','reviewed_by':'synthetic unit-test fixture','reviewed_at':'2026-10-28'}

    def test_aliases_and_missing_majors(self):
        result=ranker.candidates(self.recipes,self.query,self.aliases)
        self.assertEqual([r['id'] for r in result],['eggplant-dish','egg-dish'])
        self.assertFalse(ranker.eligible(self.recipes[2],{'available':['rice']},self.aliases))
        self.assertFalse(ranker.eligible(self.recipe('specific-cut',['pork_belly']),{'available':['pork']},self.aliases))

    def test_supporting_ingredients_are_reported_not_assumed(self):
        result=ranker.candidate_result(self.recipes[0],self.query,self.aliases)
        self.assertEqual(result['missing_supporting'],['oil'])
        self.assertTrue(result['supporting_confirmation_needed'])
        self.assertTrue(result['quantity_check_needed'])
        self.assertEqual(result['uses_first'],['eggplant'])

    def test_exclusions_and_invalid_use_first(self):
        self.assertFalse(ranker.eligible(self.recipes[0],{**self.query,'excluded':['oil']},self.aliases))
        with self.assertRaises(ValueError):
            ranker.candidates(self.recipes,{**self.query,'use_first':['chicken']},self.aliases)

    def test_unreviewed_recipes_and_overlapping_roles_fail(self):
        records=deepcopy(self.recipes)
        records[0]['reviewed_by']=''
        with self.assertRaisesRegex(ValueError,'human review'):
            ranker.validate_recipes(records,self.aliases)
        records=deepcopy(self.recipes)
        records[0]['supporting']=['egg']
        with self.assertRaisesRegex(ValueError,'overlap'):
            ranker.validate_recipes(records,self.aliases)

    def labeled_inputs(self,path):
        queries=[]
        for i,split in enumerate(['train','validation','test']):
            queries.append({**self.query,'id':f'q{i}','available':['eggplant','egg',f'extra_{i}'],
                            'split':split,'leakage_group':f'family_{i}','reviewed_by':'unit test'})
        ranker.review_queue(self.recipes,queries,self.aliases,path)
        with path.open(newline='') as f:
            reader=csv.DictReader(f); fields=reader.fieldnames; rows=list(reader)
        for row in rows:
            row['relevance']='3' if row['recipe_id']=='eggplant-dish' else '1'
            row['reviewer']='synthetic test labels; not production'
        with path.open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
        return queries

    def test_review_queue_preserves_work_and_rejects_blank_labels(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as temp:
            path=Path(temp)/'review.csv'
            queries=[{**self.query,'id':'q'}]
            ranker.review_queue(self.recipes,queries,self.aliases,path)
            with self.assertRaisesRegex(ValueError,'overwrite'):
                ranker.review_queue(self.recipes,queries,self.aliases,path)
            with self.assertRaisesRegex(ValueError,'human relevance'):
                ranker.training_groups(self.recipes,queries,path,self.aliases)

    def test_grouped_split_leakage_and_full_candidate_labels(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as temp:
            path=Path(temp)/'labels.csv'
            queries=self.labeled_inputs(path)
            groups=ranker.training_groups(self.recipes,queries,path,self.aliases)
            self.assertEqual(set(groups),{'train','validation','test'})
            leaked=deepcopy(queries); leaked[1]['leakage_group']=leaked[0]['leakage_group']
            with self.assertRaisesRegex(ValueError,'cross dataset splits'):
                ranker.training_groups(self.recipes,leaked,path,self.aliases)
            leaked=deepcopy(queries);leaked[1]['available']=leaked[0]['available']
            with self.assertRaisesRegex(ValueError,'cross dataset splits'):
                ranker.training_groups(self.recipes,leaked,path,self.aliases)

    def test_stale_judgments_rejected_after_scenario_change(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as temp:
            path=Path(temp)/'labels.csv'
            queries=self.labeled_inputs(path)
            queries[0]['max_minutes']=15
            with self.assertRaisesRegex(ValueError,'changed since review'):
                ranker.training_groups(self.recipes,queries,path,self.aliases)

    def test_high_model_score_cannot_admit_ineligible_recipe(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as temp:
            model=Path(temp)
            (model/'metadata.json').write_text(json.dumps({'version':ranker.VERSION,'features':ranker.FEATURES,
                                                         'catalog_fingerprint':ranker.fingerprint(self.recipes,self.aliases)}))
            class FakeBooster:
                def __init__(self,**kwargs): pass
                def predict(self,xs):
                    if len(xs)!=2: raise AssertionError('Ineligible recipe reached ranking model')
                    return [0,100]
            import types
            with patch.dict(sys.modules,{'lightgbm':types.SimpleNamespace(Booster=FakeBooster)}):
                results=ranker.recommend(self.recipes,self.query,self.aliases,model)
            self.assertEqual([r['recipe_id'] for r in results],['egg-dish','eggplant-dish'])
            self.assertNotIn('rice-dish',[r['recipe_id'] for r in results])
            changed=deepcopy(self.recipes);changed[0]['major']=['chicken']
            with self.assertRaisesRegex(ValueError,'does not match'):
                ranker.recommend(changed,self.query,self.aliases,model)


if __name__=='__main__': unittest.main()
