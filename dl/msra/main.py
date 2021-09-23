from dataloader import register_msra
#from pet37 import register_pet_voc
from detectron2.data import DatasetCatalog, MetadataCatalog
import os

base_dataset = os.getenv('DETECTRON2_DATASETS')
base_dir=os.path.join(base_dataset, 'MSRA-TD500')

dataset = 'msra_train'
#register_msra(dataset ,base_dir,'test','2007')
#register_msra(dataset ,base_dir,'test','2007')

from detectron2.data.datasets import register_coco_instances
register_coco_instances(dataset, {}, os.path.join(base_dir, 'train.json'), os.path.join(base_dir, 'JPEGImages'))
# register_coco_instances(dataset, {}, os.path.join(base_dir, 'test.json'), os.path.join(base_dir, 'JPEGImages'))

meta = MetadataCatalog.get(dataset)
dataset_dicts = DatasetCatalog.get(dataset)
print("data loaded, total={}".format(len(dataset_dicts)))
print(dataset_dicts[0])


import random
import cv2
from detectron2.utils.visualizer import Visualizer

for d in random.sample(dataset_dicts, 10):
	#print(d)
	img = cv2.imread(d["file_name"])
	visualizer = Visualizer(img[:, :, ::-1], metadata=meta, scale=0.5)
	visualized_output = visualizer.draw_dataset_dict(d)
	cv2.imshow('imshow', visualized_output.get_image()[:, :, ::-1])
	if cv2.waitKey(0) == 27:
		break;
