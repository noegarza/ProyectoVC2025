from roboflow import Roboflow
import os
rf = Roboflow(api_key="")
project = rf.workspace("amaro27").project("v2-axis-haptic-dino-x8w6i")
version = project.version(7)

dataset = version.download("yolov8")