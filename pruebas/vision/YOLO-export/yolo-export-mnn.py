"""
Veamos con este

Args: imgsz, batch, int8, half, device
"""

from ultralytics import YOLO

model_path = "modelos-YOLO-parcial3/v8n-640-50-aug-rgb-gray-reb-blur-2/weights/best.pt"
model = YOLO(model_path)

# exportar
model.export(format="mnn",
             int8=True,
             device="cpu")