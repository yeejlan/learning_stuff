from pet_voc_cat_2 import register_pet_voc
from detectron2.data import DatasetCatalog
import os

base_dataset = os.getenv('DETECTRON2_DATASETS')
train_dir=os.path.join(base_dataset, 'pet')
register_pet_voc('pet_voc_cat_2_trainval',train_dir,'trainval','2007')
register_pet_voc('pet_voc_cat_2_test',train_dir,'test','2007')
# later, to access the data:
data = DatasetCatalog.get("pet_voc_cat_2_trainval")

print("data loaded, total={}".format(len(data)))
print(data[0])