"""
Bruh esto en windows va mucho más lento. Esperemos en RPi no 
"""

# en colab con gen AI

from ultralytics import YOLO
import cv2
import time
import os
import pandas as pd
from datetime import datetime
import numpy as np

# Parámetros YOLO
model_path = "modelos-YOLO-parcial3/v8n-640-50-aug-rgb-gray-reb-blur-2/weights/best_ncnn_model/"
model = YOLO(model_path)

# Parámetros de cálculo de FPS
USANDO_YOLO = True
prevFrameTime = time.time()
newFrameTime = 0
ctr = 0; allFPS = []
FRAME_RATIO = 100 # agregar fps a fps global cada n frame

# Parámetros visualización
CAP = cv2.VideoCapture(0)
IMAGE_SIZE = 1 # tamaño del frame a visualizar

# Guardar evidencias
TIME_STAMP = datetime.now().strftime('%Y-%m-%d_%H-%M-%S') # las minusculas se usan para la fecha y las mayusculas para horas!
RESULTS_PATH = os.path.join(os.getcwd(), #asumiendo que root dir es el repo.
                         'pruebas',
                         'vision',
                         'YOLO-inference',
                         'probarModeloYOLO',
						 'resultados.csv')


# Funciones -----------------------------------------------------------------------
def getFPS():
	global prevFrameTime, newFrameTime
	newFrameTime = time.time()
	fps = 1 / (newFrameTime - prevFrameTime)
	prevFrameTime = newFrameTime
	return fps

def getRectArea(x1, y1, x2, y2):
	area = (x2 - x1)*(y2 - y1)
	return area


def getGreatestBoxCords(predictionBoxes):
	greatestArea = 0
	best_coords = None
	if predictionBoxes is not None and len(predictionBoxes) > 0:
		for box in predictionBoxes:
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
	
def left():
	print("izquierda")

def right():
	print("derecha")

def forward():
	print("hacia adelante")

def stop():
	print("detenerse")

def getInference_frame_boxes_pred(imgFrame):
	global USANDO_YOLO
	if USANDO_YOLO:
		prediction = model(imgFrame, verbose=False, conf=0.83)
		predictionBoxes = prediction[0].boxes
		annotatedFrame = prediction[0].plot()

	else:
		predictionBoxes = []
		annotatedFrame = imgFrame
		prediction = None
	return annotatedFrame, predictionBoxes, prediction



# Loop principal -----------------------------------------------------------------------
while True:
	ret, frame = CAP.read()
	if not ret:
		break
	ctr += 1
	fps = getFPS()	
	if ctr % 100 == 0: allFPS.append(fps)
	frame = cv2.resize(frame, None, fx=IMAGE_SIZE, fy=IMAGE_SIZE)
	annotatedFrame, predictionBoxes, prediction = getInference_frame_boxes_pred(frame)
	
	"""h, w, _ = frame.shape
	xCoordL = w//3
	xCoordR = 2*w//3
	x1, y1, x2, y2 = getGreatestBoxCords(predictionBoxes)
	if None not in (x1, y1, x2, y2):
		xCenter = (x1+x2)//2
		if xCenter < xCoordL: left()
		elif xCenter > xCoordR: right()
		else: forward()
	else:
		stop()"""
	
	# HUD
	#cv2.line(annotatedFrame, (xCoordL, 0), (xCoordL, h), (0, 0, 255), 2)
	#cv2.line(annotatedFrame, (xCoordR, 0), (xCoordR, h), (0, 0, 255), 2)
	cv2.imshow("YOLO Inference", annotatedFrame)
	if cv2.waitKey(1) & 0xFF == ord('q'):
		meanFPS = np.median(allFPS)
		newResult = pd.DataFrame({
			"time stamp": [TIME_STAMP],
			"Se usó YOLO?": [USANDO_YOLO],
			"FPS": [round(meanFPS, 2)]
		})
		
		# Si el archivo existe, concatenar; si no, crearlo
		if os.path.exists(RESULTS_PATH):
			old_df = pd.read_csv(RESULTS_PATH)
			df = pd.concat([old_df, newResult], ignore_index=True)
		else:
			df = newResult
		df.to_csv(RESULTS_PATH, index=False)
		
		break

CAP.release()
cv2.destroyAllWindows()

