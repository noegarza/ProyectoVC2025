from roboflow import Roboflow
import os
rf = Roboflow(api_key="")
project = rf.workspace("amaro27").project("tennis-balls-ciwdv")
version = project.version(1)

dataset = version.download("yolov8")