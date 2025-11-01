from roboflow import Roboflow
import os
rf = Roboflow(api_key="")
project = rf.workspace("alex4").project("etiquetado-haptic-paddle-jry5s")
version = project.version(1)

dataset = version.download("yolov8")