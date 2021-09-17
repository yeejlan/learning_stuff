from detectron2.data import DatasetCatalog, MetadataCatalog
import os

dataset = "voc_2007_trainval"
# dataset = "voc_2007_test"

meta = MetadataCatalog.get(dataset)
dataset_dicts = DatasetCatalog.get(dataset)
print("data loaded, total={}".format(len(dataset_dicts)))
print(meta)
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
