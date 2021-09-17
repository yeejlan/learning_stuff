from pet_voc_cat_2 import register_pet_voc
#from pet37 import register_pet_voc
from detectron2.data import DatasetCatalog, MetadataCatalog
import os

base_dataset = os.getenv('DETECTRON2_DATASETS')
base_dir=os.path.join(base_dataset, 'pet')

dataset = 'pet_voc_cat_2_trainval'
register_pet_voc(dataset ,base_dir,'trainval','2007')
#register_pet_voc('pet_voc_cat_2_test',base_dir,'test','2007', False)

meta = MetadataCatalog.get(dataset)
dataset_dicts = DatasetCatalog.get(dataset)
print("data loaded, total={}".format(len(dataset_dicts)))
print(dataset_dicts[0])


import random
import cv2
from detectron2.utils.visualizer import Visualizer

for d in random.sample(dataset_dicts, 10):
	img = cv2.imread(d["file_name"])
	visualizer = Visualizer(img[:, :, ::-1], metadata=meta)
	visualized_output = visualizer.draw_dataset_dict(d)
	cv2.imshow('imshow', visualized_output.get_image()[:, :, ::-1])
	if cv2.waitKey(0) == 27:
		break;
