import torch

# Model
model = torch.hub.load('ultralytics/yolov5', 'yolov5l')  # or yolov5m, yolov5l, yolov5x, custom

import datetime

t_s = datetime.datetime.now()
# Images
img = 'D:/work/source/detectron2/image/2.png'  # or file, Path, PIL, OpenCV, numpy, list

# Inference
results = model(img)

t_e = datetime.datetime.now()
print(t_e-t_s)
# Results
results.show()  # or .show(), .save(), .crop(), .pandas(), etc.