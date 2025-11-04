"""
Hmm de lo poco que investigué está optimizado para arquitecturas ARM,
pero tiene pocos parámetros disponibles de exportación.

Por eso habrá que hacer pruebas. 

nombre dir salida(?): yolo11n_ncnn_model/
pero eso es si el modelo entrada es yolo11n.pt

asumo en nuestro caso será best...
"""

from ultralytics import YOLO

model_path = "modelos-YOLO-parcial3/v8n-640-50-aug-rgb-gray-reb-blur-2/weights/best.pt"
model = YOLO(model_path)

# exportar
model.export(format="ncnn",
             imgsz=640,
             half=True,
             device='cpu',
             batch=1) 