from pet_voc_cat_2 import register_pet_voc
#from pet37 import register_pet_voc
from detectron2.data import DatasetCatalog
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