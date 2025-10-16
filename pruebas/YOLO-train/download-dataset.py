from roboflow import Roboflow
import os
rf = Roboflow(api_key="X8dcp78gfishEDl9jWt5")
project = rf.workspace("viren-dhanwani").project("tennis-ball-detection")
version = project.version(6)

dataset = version.download("yolov8")