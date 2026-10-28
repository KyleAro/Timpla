"""Integration checks against the actual team checkpoint; not an accuracy benchmark."""
import json
import io
from pathlib import Path
import unittest
from unittest.mock import patch
from PIL import Image

from fastapi.testclient import TestClient
from backend.main import app
from ml.ingredient_detector.detector import ROOT, MAX_BYTES, ingredient_name, merge_detections, WEIGHTS, PRODUCE_WEIGHTS


class DetectorApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context=TestClient(app)
        cls.client=cls.context.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.context.__exit__(None,None,None)

    def test_checkpoint_and_health(self):
        response=self.client.get('/health')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json()['classes'],66)
        self.assertEqual(response.json()['class_names']['25'],'egg')
        self.assertEqual(len(response.json()['models']),2)
        self.assertEqual(response.json()['models'][1]['classes'],63)
        self.assertIn('banana',response.json()['ingredient_names'])
        self.assertEqual(self.client.get('/').status_code,200)

    def test_invalid_uploads(self):
        for name,data,mime,expected in [('empty.jpg',b'','image/jpeg',413),
                                       ('text.txt',b'text','text/plain',415),
                                       ('corrupt.jpg',b'not a photo','image/jpeg',422),
                                       ('large.jpg',b'x'*(MAX_BYTES+1),'image/jpeg',413),
                                       ('body.jpg',b'x'*(MAX_BYTES+150_000),'image/jpeg',413)]:
            with self.subTest(name=name):
                response=self.client.post('/detect',files={'image':(name,data,mime)})
                self.assertEqual(response.status_code,expected,response.text)

    def test_real_photos(self):
        folder=ROOT/'tmp/ingredient-detector-samples'
        output=[]
        for filename in ['eggs.jpg','tomato-onion.jpg']:
            path=folder/filename
            self.assertTrue(path.exists(),f'Test photo missing: {path}')
            response=self.client.post('/detect',files={'image':(filename,path.read_bytes(),'image/jpeg')})
            self.assertEqual(response.status_code,200,response.text)
            payload=response.json()
            self.assertEqual(payload['model'],'YOLOv12n_Best.pt')
            if filename=='tomato-onion.jpg':
                self.assertTrue(any(item['name']=='tomato' and item['source_model']==PRODUCE_WEIGHTS.name for item in payload['ingredients']),payload)
            self.assertGreater(payload['width'],0)
            for detection in payload['detections']:
                self.assertGreaterEqual(detection['confidence'],0.1)
                self.assertLessEqual(detection['confidence'],1)
                x1,y1,x2,y2=detection['bbox_xyxy']
                self.assertTrue(0<=x1<x2<=payload['width']+0.01)
                self.assertTrue(0<=y1<y2<=payload['height']+0.01)
            output.append({'file':filename,**payload})
        (ROOT/'models/ingredient_detector/smoke-test.json').write_text(json.dumps(output,indent=2)+'\n')
        print(json.dumps([{'file':r['file'],'ingredients':r['ingredients'],'seconds':r['inference_seconds']} for r in output],indent=2),flush=True)

    def test_avif_upload_and_corrupt_avif(self):
        # A real AVIF encode/decode reproduces the format that crashed uploads.
        photo=Image.new('RGB',(64,48),(120,40,20))
        encoded=io.BytesIO()
        photo.save(encoded,format='AVIF')
        response=self.client.post('/detect',files={'image':('photo.avif',encoded.getvalue(),'image/avif')})
        self.assertEqual(response.status_code,200,response.text)
        self.assertEqual((response.json()['width'],response.json()['height']),(64,48))
        response=self.client.post('/detect',files={'image':('broken.avif',encoded.getvalue()[:32],'image/avif')})
        self.assertEqual(response.status_code,422,response.text)
        self.assertIn('detail',response.json())

    def test_inference_failure_returns_json(self):
        with patch.object(app.state.detector,'predict',side_effect=RuntimeError('test failure')):
            response=self.client.post('/detect',files={'image':('photo.jpg',b'photo','image/jpeg')})
        self.assertEqual(response.status_code,500,response.text)
        self.assertIn('detail',response.json())

    def test_combining_models_preserves_distinct_objects_and_team_labels(self):
        def detection(name,confidence,box,source):
            return {'name':name,'label':name,'confidence':confidence,'bbox_xyxy':box,'source_model':source,'class_id':1}
        boxes,ingredients=merge_detections([
            detection('egg',0.8,[0,0,50,50],WEIGHTS.name),
            detection('orange',0.99,[0,0,50,50],PRODUCE_WEIGHTS.name),
            detection('banana',0.9,[100,100,150,150],PRODUCE_WEIGHTS.name),
            detection('banana',0.7,[101,101,151,151],PRODUCE_WEIGHTS.name),
            detection('banana',0.88,[200,200,250,250],PRODUCE_WEIGHTS.name)])
        self.assertEqual(len(boxes),3)
        self.assertEqual({item['name'] for item in ingredients},{'egg','banana'})
        self.assertEqual(ingredient_name('eggplant/aubergine'),'talong')
        self.assertEqual(ingredient_name('bell pepper/capsicum'),ingredient_name('bell_pepper'))
        self.assertNotEqual(ingredient_name('green bean'),ingredient_name('sitaw'))

    def test_specialist_routing_accepts_produce_without_team_agreement(self):
        def candidate(name,score,source,box=None):
            return {'name':name,'label':name,'confidence':score,'source_model':source,
                    'class_id':1,'bbox_xyxy':box or [0,0,100,100]}
        produce_names={'tomato','talong','mushroom'}
        for name in ['tomato','talong','mushroom']:
            boxes,ingredients=merge_detections([candidate(name,0.50,PRODUCE_WEIGHTS.name)],produce_names)
            self.assertEqual(ingredients[0]['name'],name)
            self.assertEqual(ingredients[0]['source_model'],PRODUCE_WEIGHTS.name)
        # A wrong/high-confidence shared team label must not override produce.
        boxes,ingredients=merge_detections([candidate('mushroom',0.99,WEIGHTS.name),
                                          candidate('tomato',0.9,PRODUCE_WEIGHTS.name)],produce_names)
        self.assertEqual([item['name'] for item in ingredients],['tomato'])
        # Meat and eggs keep the team model; different objects may coexist.
        boxes,ingredients=merge_detections([candidate('chicken generic',0.9,WEIGHTS.name),
                                          candidate('mushroom',0.99,PRODUCE_WEIGHTS.name),
                                          candidate('tomato',0.8,PRODUCE_WEIGHTS.name,[200,200,300,300])],produce_names)
        self.assertEqual({item['name'] for item in ingredients},{'chicken generic','tomato'})
        self.assertEqual(merge_detections([candidate('tomato',0.49,PRODUCE_WEIGHTS.name),
                                          candidate('egg',0.09,WEIGHTS.name)],produce_names),([],[]))
        self.assertEqual(merge_detections([candidate('tomato',0.99,WEIGHTS.name)],produce_names),([],[]))
        _,ingredients=merge_detections([candidate('egg',0.10,WEIGHTS.name)],produce_names)
        self.assertEqual(ingredients[0]['name'],'egg')


if __name__=='__main__': unittest.main()
