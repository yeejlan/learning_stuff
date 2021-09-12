from pet_voc_cat_2 import register_pet_voc
#from pet37 import register_pet_voc
from detectron2.data import DatasetCatalog, MetadataCatalog
import os

base_dataset = os.getenv('DETECTRON2_DATASETS')
base_dir=os.path.join(base_dataset, 'pet')
register_pet_voc('pet_voc_cat_2_trainval',base_dir,'trainval','2007')
#register_pet_voc('pet_voc_cat_2_test',base_dir,'test','2007', False)


trainval_data = DatasetCatalog.get("pet_voc_cat_2_trainval")
print("data loaded, trainval total={}".format(len(trainval_data)))
print(trainval_data[0])

#test_data = DatasetCatalog.get("pet_voc_cat_2_test")
#print("data loaded, test total={}".format(len(test_data)))
#print(test_data)

# register_pet_voc('pet37',base_dir,'trainval','2007')
# trainval_data = DatasetCatalog.get("pet37")
# print("data loaded, trainval total={}".format(len(trainval_data)))
# print(trainval_data[2289])

import random
import cv2
from detectron2.utils.visualizer import Visualizer

meta = MetadataCatalog.get('pet_voc_cat_2_trainval')
dataset_dicts = trainval_data
for d in random.sample(dataset_dicts, 10):
	img = cv2.imread(d["file_name"])
	visualizer = Visualizer(img[:, :, ::-1], metadata=meta)
	visualized_output = visualizer.draw_dataset_dict(d)
	cv2.imshow('imshow', visualized_output.get_image()[:, :, ::-1])
	if cv2.waitKey(0) == 27:
		break;
