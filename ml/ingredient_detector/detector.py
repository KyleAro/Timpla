"""Load the team's released ingredient detector and return actual image predictions."""
from pathlib import Path
import hashlib
import io
import json
import os
import time
import warnings

ROOT = Path(__file__).resolve().parents[2]
os.environ.setdefault('YOLO_CONFIG_DIR', str(ROOT/'tmp/ultralytics'))
os.environ.setdefault('MPLCONFIGDIR', str(ROOT/'tmp/matplotlib'))
os.environ['YOLO_AUTOINSTALL'] = 'False'

from PIL import Image, ImageOps
import torch
from ultralytics import YOLO
# Ultralytics patches Image.open globally and tries to install pi-heif on any
# decode failure. Use its saved Pillow opener so invalid files stay validation
# errors, regardless of the order in which this module was imported.
from ultralytics.utils.patches import _image_open as OPEN_IMAGE
import pillow_avif  # Registers AVIF support for the pinned Pillow 11.2 runtime.

MAX_BYTES = 5_000_000
MAX_PIXELS = 40_000_000
MODEL_DIR = ROOT/'models/ingredient_detector'
WEIGHTS = MODEL_DIR/'YOLOv12n_Best.pt'
EXPECTED_SHA256 = '5eaa3205138c11d71cbbddda946a51aa92180bed8afeb7bbe0de23746aac9f2d'
PRODUCE_WEIGHTS = ROOT/'models/produce/author-yolov8m.pt'
PRODUCE_SHA256 = 'a18624d446e2fea08384949115de0b49446f0be2487fc954a37a9d962f71e5d3'
TEAM_MIN_CONFIDENCE = 0.10
PRODUCE_MIN_CONFIDENCE = 0.50
FUSION_POLICY = ('Produce-model labels are handled by YOLOv8m at confidence >= 0.50; '
                 'the team model handles remaining labels at >= 0.10. No two-model agreement is required. '
                 'Overlapping non-produce team predictions >= 0.5 block conflicting produce boxes '
                 '(IoU > 0.3). Empty results are allowed. Thresholds are provisional, not calibrated.')

# Only equivalent labels are combined. Specific cuts, onion varieties and
# distinct vegetables retain their own names. IDs remain local to each model.
ALIASES = {'bean curd':'tofu','bell pepper':'bell pepper','eggplant':'talong',
           'green onion':'spring onions','edible corn':'corn','sili':'chili'}


def ingredient_name(label):
    name=label.split('/')[0].replace('_',' ').strip().lower()
    return ALIASES.get(name,name)


def box_iou(first,second):
    left=max(first[0],second[0]); top=max(first[1],second[1])
    right=min(first[2],second[2]); bottom=min(first[3],second[3])
    overlap=max(0,right-left)*max(0,bottom-top)
    union=(first[2]-first[0])*(first[3]-first[1])+(second[2]-second[0])*(second[3]-second[1])-overlap
    return overlap/union if union>0 else 0


def merge_detections(candidates,produce_names=()):
    # Assign labels to a specialist rather than requiring both models to detect
    # them. Team-only vegetables (for example pechay) remain with the team model.
    non_produce_team=[item for item in candidates if item['source_model']==WEIGHTS.name and
                      item['name'] not in produce_names and item['confidence']>=0.5]
    accepted=[]
    for item in candidates:
        if item['source_model']==WEIGHTS.name:
            if item['name'] in produce_names or item['confidence']<TEAM_MIN_CONFIDENCE:
                continue
        else:
            if item['confidence']<PRODUCE_MIN_CONFIDENCE:
                continue
            if any(box_iou(item['bbox_xyxy'],other['bbox_xyxy'])>0.3 for other in non_produce_team):
                continue
        accepted.append(item)
    candidates=accepted
    detections=[]
    for candidate in sorted(candidates,key=lambda item:item['confidence'],reverse=True):
        if any(item['name']==candidate['name'] and box_iou(item['bbox_xyxy'],candidate['bbox_xyxy'])>0.5 for item in detections):
            continue
        detections.append(candidate)
    ingredients={}
    for item in detections:
        if item['name'] not in ingredients:
            ingredients[item['name']]={key:item[key] for key in ('label','name','confidence','source_model')}
    return detections,list(ingredients.values())

try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    pass


def decode_image(content):
    if not 0 < len(content) <= MAX_BYTES:
        raise ValueError('Photo must be nonempty and 5 MB or smaller.')
    with warnings.catch_warnings():
        warnings.simplefilter('error', Image.DecompressionBombWarning)
        with OPEN_IMAGE(io.BytesIO(content)) as source:
            if source.format not in {'JPEG','PNG','WEBP','HEIF','AVIF','BMP','TIFF'}:
                raise ValueError('Unsupported image format.')
            if source.width * source.height > MAX_PIXELS or getattr(source,'n_frames',1) != 1:
                raise ValueError('Choose a still image no larger than 40 megapixels.')
            source.load()
            return ImageOps.exif_transpose(source).convert('RGB')


class IngredientDetector:
    def __init__(self):
        if not WEIGHTS.is_file():
            raise FileNotFoundError(f'Download the team checkpoint first: {WEIGHTS}')
        if hashlib.sha256(WEIGHTS.read_bytes()).hexdigest() != EXPECTED_SHA256:
            raise ValueError('Checkpoint does not match the verified team release.')
        torch.set_num_threads(min(4, os.cpu_count() or 1))
        self.model = YOLO(str(WEIGHTS), task='detect')
        self.names = {int(key):value for key,value in self.model.names.items()}
        if not self.names or not all(isinstance(value,str) and value.strip() for value in self.names.values()):
            raise ValueError('Checkpoint ingredient names are invalid.')
        self.device = 0 if torch.cuda.is_available() else 'cpu'
        if not PRODUCE_WEIGHTS.is_file() or hashlib.sha256(PRODUCE_WEIGHTS.read_bytes()).hexdigest()!=PRODUCE_SHA256:
            raise ValueError('Download the verified fruit-and-vegetable checkpoint first.')
        self.produce_model=YOLO(str(PRODUCE_WEIGHTS),task='detect')
        self.produce_names={int(key):value for key,value in self.produce_model.names.items()}
        self.models=[{'file':WEIGHTS.name,'architecture':'YOLOv12n','classes':len(self.names)},
                     {'file':PRODUCE_WEIGHTS.name,'architecture':'YOLOv8m','classes':len(self.produce_names),
                      'excluded_labels':['Tomato','Strawberry']}]
        self.models[0]['role']='Ingredients not covered by the produce model'
        self.models[1]['role']='Fruit-and-vegetable model labels'
        self.supported_names=sorted({ingredient_name(label) for label in self.names.values()} |
                                    {ingredient_name(label) for label in self.produce_names.values() if label not in {'Tomato','Strawberry'}})
        self.produce_ingredient_names={
            ingredient_name(label) for label in self.produce_names.values() if label not in {'Tomato','Strawberry'}}

    def warmup(self):
        for model in (self.model,self.produce_model):
            model.predict(Image.new('RGB',(64,64)),device=self.device,imgsz=640,conf=0.35,iou=0.5,verbose=False)

    def predict(self,content):
        picture = decode_image(content)
        start = time.perf_counter()
        candidates=[]
        for model,names,weights in ((self.model,self.names,WEIGHTS),(self.produce_model,self.produce_names,PRODUCE_WEIGHTS)):
            result=model.predict(picture,device=self.device,imgsz=640,conf=TEAM_MIN_CONFIDENCE if weights==WEIGHTS else PRODUCE_MIN_CONFIDENCE,iou=0.5,verbose=False)[0]
            for box in result.boxes:
                class_id=int(box.cls.item())
                label=names[class_id]
                if weights==PRODUCE_WEIGHTS and label in {'Tomato','Strawberry'}:
                    continue
                candidates.append({'class_id':class_id,'label':label,'name':ingredient_name(label),
                                   'confidence':round(float(box.conf.item()),4),'source_model':weights.name,
                                   'bbox_xyxy':[round(float(v),2) for v in box.xyxy[0].tolist()]})
        detections,ingredients=merge_detections(candidates,self.produce_ingredient_names)
        return {'model':WEIGHTS.name,'architecture':'YOLOv12n + YOLOv8m','models':self.models,
                'fusion_policy':FUSION_POLICY,'rejected_detections':len(candidates)-len(detections),
                'width':picture.width,'height':picture.height,
                'inference_seconds':round(time.perf_counter()-start,3),'detections':detections,
                'ingredients':ingredients}
