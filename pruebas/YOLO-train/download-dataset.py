from roboflow import Roboflow
rf = Roboflow(api_key="your_API_key")
project = rf.workspace("viren-dhanwani").project("tennis-ball-detection")
version = project.version(6)
dataset = version.download("yolov8")