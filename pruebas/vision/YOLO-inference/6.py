# en colab con gen AI

from ultralytics import YOLO
import cv2
import numpy as np
import serial
import time

from datetime import datetime
import subprocess

arduino = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
time.sleep(2) 
# Ruta al modelo entrenado
model_path = "modelos-YOLO/v8n-e30-imgsz40/weights/best.pt"
model = YOLO(model_path)

# Variables HUD
prev_time = time.time()
fps = 0
max_inliers = 1  # para calcular el ratio
font = cv2.FONT_HERSHEY_SIMPLEX


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



# en colab con gen AI


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
last_comando = '0'

# Abrir cámara
cap = cv2.VideoCapture(0)
while True:
	ret, frame = cap.read()
	if not ret:
		break

	# Calcular FPS
	current_time = time.time()
	fps = 1.0 / (current_time - prev_time)
	prev_time = current_time

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

    # Calcular número de “inliers” (áreas azules detectadas)
	inliers = len(contours)
	max_inliers = max(max_inliers, inliers)
	inlier_ratio = inliers / max_inliers if max_inliers > 0 else 0

	# Dibujar líneas verticales en xd1 y xd2
	cv2.line(annotated_frame, (xd1, 0), (xd1, h), (0, 0, 255), 2)
	cv2.line(annotated_frame, (xd2, 0), (xd2, h), (0, 0, 255), 2)
	boxes = results[0].boxes
	x1, y1, x2, y2 = getGreatestBoxCords(boxes)
	comando = '0'
	
	if None not in (x1, y1, x2, y2):
		xCenter = (x1+x2)//2
		if xCenter < xd1:
			#print("a la ihquierda")
			comando = '2'
			
		elif xCenter > xd2:
			#print("a la derehcha")
			comando = '3'
		else:
			#print("al chaaave")
			comando = '1'
	else:
		#print("detente chaaave")
		comando = '0'
	#time.sleep(0.01)
	if comando != last_comando:
		arduino.write(comando.encode())
		last_comando = comando
	

	 # ===============================
    # HUD (Heads-Up Display)
    # ===============================
	cv2.putText(frame, f"Estado: Lab Robotica", (10, 30), font, 0.7, color_status, 2)
	cv2.putText(frame, f"FPS: {fps:.1f}", (10, 60), font, 0.7, (255, 255, 0), 2)
	cv2.putText(frame, f"Inliers: {inliers}", (10, 90), font, 0.7, (0, 255, 0), 2)
	cv2.putText(frame, f"Inlier Ratio: {inlier_ratio:.2f}", (10, 120), font, 0.7, (255, 0, 255), 2)
	cv2.imshow("YOLO Inference", annotated_frame)



	if cv2.waitKey(1) & 0xFF == ord('q'):
		break
cap.release()
cv2.destroyAllWindows()

