import pycocotools
from pycocotools.coco import COCO
import os

#ref: https://zhuanlan.zhihu.com/p/29393415

base_dataset = os.getenv('DETECTRON2_DATASETS')
ann_train_file=os.path.join(base_dataset, 'coco/annotations/instances_train2017.json')
ann_val_file=os.path.join(base_dataset, 'coco/annotations/instances_val2017.json')

coco_val = COCO(ann_val_file)

print("categories: {}".format(len(coco_val.dataset['categories'])))
print("images: {}".format(len(coco_val.dataset['images'])))
print("annotations: {}".format(len(coco_val.dataset['annotations'])))


# for idx, one in enumerate(coco_val.dataset['annotations']):
#     if one['iscrow']

#print(coco_val.dataset['categories'][0]);
#quit()

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection

def show_ploygon(gemfield_polygons):
    fig, ax = plt.subplots()
    polygons = []
    gemfield_polygon = gemfield_polygons[0]
    max_value = max(gemfield_polygon) * 1.3
    gemfield_polygon = [i * 1.0/max_value for i in gemfield_polygon]
    poly = np.array(gemfield_polygon).reshape((int(len(gemfield_polygon)/2), 2))
    polygons.append(Polygon(poly,True))
    p = PatchCollection(polygons, cmap=matplotlib.cm.jet, alpha=0.4)
    colors = 100*np.random.rand(1)
    p.set_array(np.array(colors))

    ax.add_collection(p)
    plt.show()

def show_rle(w, h, rle):
    M = np.zeros(w*h)
    N = len(rle)
    n = 0
    val = 1
    for pos in range(N):
        val = not val
        for c in range(rle[pos]):
            M[n] = val
            n += 1

    GEMFIELD = M.reshape(([w, h]), order='F')
    plt.imshow(GEMFIELD)
    plt.show()    


#show_ploygon(coco_val.dataset['annotations'][7]['segmentation'])
#one = coco_val.dataset['annotations'][36335]['segmentation']
#show_rle(*one['size'], one['counts'])