# en colab con gen AI

from ultralytics import YOLO
import cv2
import numpy as np
import serial
import time

import socket
import threading
import pickle
import struct
import time
import cv2
import traceback

from datetime import datetime
import subprocess

arduino = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
time.sleep(2) 
comando = 'e'  # e de 'evasion' o de 'enable' o de 'empecemos' o de 'este pues ya, no?' o de 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'
arduino.write(comando.encode())  # Envía el comando
print(f"programa principal iniciado")
# Ruta al modelo entrenado
model_path = "modelos-YOLO/v8n-e30-imgsz40/weights/best.pt"
model = YOLO(model_path)

# Variables HUD
prev_time = time.time()
fps = 0
max_inliers = 1  # para calcular el ratio
font = cv2.FONT_HERSHEY_SIMPLEX


# — Flags y estado —
camera_on    = False
ultra_on     = False
temp_on      = False
saving_temp  = False
server_run   = True
cam          = None

# — Configuración de sockets —
HOST       = '0.0.0.0'
VIDEO_PORT = 50000

srv_vid = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
srv_vid.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

srv_vid.bind((HOST, VIDEO_PORT))
srv_vid.listen(1)
print(f"[SERVIDOR] Video en {HOST}:{VIDEO_PORT}")

conn_vid,  addr_v = srv_vid.accept()
print(f"[SERVIDOR] Video conectado:   {addr_v}")



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
	contornos, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #for cnt in contornos:
	# Inferencia YOLOv8 (sin verbose)
	results = model(frame, verbose=False)
	# Mostrar resultados en ventana
	annotated_frame = results[0].plot()
	#annotated_frame= frame.copy()

    # Calcular número de “inliers” (áreas azules detectadas)
	#inliers = len(contours)
	"""max_inliers = max(max_inliers, inliers)
	inlier_ratio = inliers / max_inliers if max_inliers > 0 else 0"""

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
		time.sleep(0.3)
		last_comando = comando
	

	 # ===============================
    # HUD (Heads-Up Display)
    # ===============================
	#cv2.putText(annotated_frame, f"Estado: Lab Robotica", (10, 30), font, 0.7, color_status, 2)
	cv2.putText(annotated_frame, f"FPS: {fps:.1f}", (10, 60), font, 0.7, (255, 255, 0), 2)
	#cv2.putText(annotated_frame, f"Inliers: {inliers}", (10, 90), font, 0.7, (0, 255, 0), 2)
	#cv2.putText(annotated_frame, f"Inlier Ratio: {inlier_ratio:.2f}", (10, 120), font, 0.7, (255, 0, 255), 2)
	#cv2.imshow("YOLO Inference", annotated_frame)
	#annotated_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2GRAY)
	_, encimg = cv2.imencode('.jpg', annotated_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
	data = encimg.tobytes()
	try:
		conn_vid.sendall(struct.pack("Q", len(data)) + data)
	except Exception as e:
		print("Error enviando frame:", e)
		break
	key = cv2.waitKey(1) & 0xFF
	if key == ord('q'):
		# Enviar comando de parada y volver al modo inactivo
		arduino.write(b'x')  # 'x' = detener y desactivar evasión
		print("Programa detenido. Señal enviada al Arduino.")
		time.sleep(1)  # breve pausa para asegurar envío
		cap.release()
		cv2.destroyAllWindows()

