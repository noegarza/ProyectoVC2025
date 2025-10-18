# en colab con gen AI

from ultralytics import YOLO
import cv2

# Ruta al modelo entrenado
model_path = "modelos-YOLO/v8n-e30-imgsz40/weights/best.pt"
model = YOLO(model_path)


def getRectArea(x1, y1, x2, y2):
	area = (x2 - x1)*(y2 - y1)
	return area


def getGreatestBoxCords(boxes):
	greatestArea = 0
	best_coords = None
	if boxes is not None and len(boxes) > 0:
		for box in boxes:
			xyxy = box.xyxy[0].cpu().numpy()
			x1, y1, x2, y2 = xyxy
			rectArea = getRectArea(x1, y1, x2, y2)
			if rectArea > greatestArea:
				greatestArea = rectArea
				best_coords = (x1, y1, x2, y2)
	if best_coords is not None:
		return best_coords
	else:
		return None, None, None, None

imageSize = 1.5

# Abrir cámara
cap = cv2.VideoCapture(0)
while True:
	ret, frame = cap.read()
	if not ret:
		break
	frame = cv2.resize(frame, None, fx=imageSize, fy=imageSize)
	# Dividir el frame en 3 partes iguales en X
	h, w, _ = frame.shape
	xd1 = w//3
	xd2 = 2 * w // 3
	# Inferencia YOLOv8 (sin verbose)
	results = model(frame, verbose=False)
	# Mostrar resultados en ventana
	annotated_frame = results[0].plot()
	#annotated_frame= frame.copy()
	# Dibujar líneas verticales en xd1 y xd2
	cv2.line(annotated_frame, (xd1, 0), (xd1, h), (0, 0, 255), 2)
	cv2.line(annotated_frame, (xd2, 0), (xd2, h), (0, 0, 255), 2)
	boxes = results[0].boxes
	x1, y1, x2, y2 = getGreatestBoxCords(boxes)
	
	if None not in (x1, y1, x2, y2):
		xCenter = (x1+x2)//2
		if xCenter < xd1:
			print("a la ihquierda")
		elif xCenter > xd2:
			print("a la derehcha")
		else:
			print("al chaaave")
	else:
		print("detente chaaave")
	cv2.imshow("YOLO Inference", annotated_frame)
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break
cap.release()
cv2.destroyAllWindows()

