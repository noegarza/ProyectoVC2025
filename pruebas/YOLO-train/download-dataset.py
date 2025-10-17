from roboflow import Roboflow
import os
rf = Roboflow(api_key="X8dcp78gfishEDl9jWt5")
project = rf.workspace("joses-workspace-bfegj").project("tennis-balls")
version = project.version(1)

dataset = version.download("yolov8")