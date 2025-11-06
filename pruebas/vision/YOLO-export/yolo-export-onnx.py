"""
Veamos con este

Args: format, imgsz, half, dynamic, simplify, opset, nms, batch, device
"""

from ultralytics import YOLO

model_path = "modelos-YOLO-parcial3/v8n-640-50-aug-rgb-gray-reb-blur-2/weights/best.pt"
model = YOLO(model_path)

# exportar
model.export(format="onnx",
             half=True,
             simplify=True,
             device="cpu")