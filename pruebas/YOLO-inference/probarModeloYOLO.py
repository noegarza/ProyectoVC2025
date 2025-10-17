from ultralytics import YOLO
import cv2

# Ruta al modelo entrenado
model_path = "modelos-YOLO/train17/weights/best.pt"
model = YOLO(model_path)

# Abrir cámara
cap = cv2.VideoCapture(0)
while True:
	ret, frame = cap.read()
	if not ret:
		break
	# Inferencia YOLOv8 (sin verbose)
	results = model(frame, verbose=False)
	# Mostrar resultados en ventana
	annotated_frame = results[0].plot()
	cv2.imshow("YOLO Inference", annotated_frame)
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break
cap.release()
cv2.destroyAllWindows()

