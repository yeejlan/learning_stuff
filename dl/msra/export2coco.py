#attrDict = {"images":[{"file_name":[],"height":[], "width":[],"id":[]}], "type":"instances", "annotations":[], "categories":[]}

from dataloader import register_msra
from detectron2.data import DatasetCatalog, MetadataCatalog
import os
import json

base_dataset = os.getenv('DETECTRON2_DATASETS')
base_dir=os.path.join(base_dataset, 'MSRA-TD500')

dataset = 'msra_train'
register_msra(dataset ,base_dir,'train','2007')
meta = MetadataCatalog.get(dataset)
dataset_dicts = DatasetCatalog.get(dataset)
print("data loaded, total={}".format(len(dataset_dicts)))

images = list()
annotations = list()
attrDict = dict()
idx = 1
for one in dataset_dicts:
    image = dict()
    image['file_name'] = str(one['file_name'])
    image['height'] = int(one['height'])
    image['width'] = int(one['width'])
    image['id'] = one['image_id']
    images.append(image)
    for ann in one['annotations']:
        annotation = dict()
        annotation["iscrowd"] = 0
        annotation["image_id"] = image['id']
        annotation["bbox"] = ann['bbox']
        annotation["area"] = float(ann["bbox"][2] * ann["bbox"][3])
        annotation["category_id"] = ann["category_id"]
        annotation["ignore"] = 0
        annotation["id"] = idx
        idx+=1
        annotations.append(annotation)

attrDict["images"] = images 
attrDict["annotations"] = annotations
attrDict["type"] = "instances"
attrDict["categories"]=[{"supercategory":"none","id":1,"name":"t"}
                  ]
jsonString = json.dumps(attrDict)
with open("instances_train2017.json", "w+") as f:
    f.write(jsonString)

print('done.')