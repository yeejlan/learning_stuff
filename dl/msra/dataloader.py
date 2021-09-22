# -*- coding: utf-8 -*-
# Copyright (c) Facebook, Inc. and its affiliates.

import numpy as np
import os
import xml.etree.ElementTree as ET
from typing import List, Tuple, Union

from detectron2.data import DatasetCatalog, MetadataCatalog
from detectron2.structures import BoxMode
from detectron2.utils.file_io import PathManager
from PIL import Image

__all__ = ["load_msra_instances", "register_msra"]


# fmt: off
CLASS_NAMES = (
    "t",
)
# fmt: on


def load_msra_instances(dirname: str, split: str, class_names: Union[List[str], Tuple[str, ...]]):
    """
    Load Pascal VOC detection annotations to Detectron2 format.

    Args:
        dirname: Contain "Annotations", "ImageSets", "JPEGImages"
        split (str): one of "train", "test", "val", "trainval"
        class_names: list or tuple of class names
    """
    with PathManager.open(os.path.join(dirname, "ImageSets", "Main", split + ".txt")) as f:
        fileids = np.loadtxt(f, dtype=np.str)

    # Needs to read many small annotation files. Makes sense at local
    annotation_dirname = PathManager.get_local_path(os.path.join(dirname, "Annotations/"))
    dicts = []

    for file in fileids:
        anno_file = os.path.join(annotation_dirname, file + ".gt")
        jpeg_file = os.path.join(dirname, "JPEGImages", file + ".jpg")

        im = Image.open(jpeg_file)

        r = {
            "file_name": jpeg_file,
            "image_id": file,
            "height": im.size[1],
            "width": im.size[0],
        }
        instances = []

        with PathManager.open(anno_file) as f:
            while True:
                line = f.readline()
                if not line:
                    break
        #XYWHA_ABS = 4
        #(xc, yc, w, h, a) in absolute floating points coordinates.
        #(xc, yc) is the center of the rotated box, and the angle a is in degrees ccw.
                vals = [float(i) for i in line.split(" ")]
                bbox = vals[2:]
                bbox[0] = bbox[0]+bbox[2]*0.5
                bbox[1] = bbox[1]+bbox[3]*0.5
                bbox[4] = 0-bbox[4]*180/3.1415926
                instances.append(
                    {"category_id": 0, "bbox": bbox, "bbox_mode": BoxMode.XYWHA_ABS}
                )
        r["annotations"] = instances
        dicts.append(r)
    return dicts


def register_msra(name, dirname, split, year, class_names=CLASS_NAMES):
    DatasetCatalog.register(name, lambda: load_msra_instances(dirname, split, class_names))
    MetadataCatalog.get(name).set(
        thing_classes=list(class_names), dirname=dirname, year=year, split=split, evaluator_type="pascal_voc",
    )
