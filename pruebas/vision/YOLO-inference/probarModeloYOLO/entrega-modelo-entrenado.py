# en colab con gen AI

from ultralytics import YOLO
import cv2
import time
import os
import pandas as pd
from datetime import datetime
import numpy as np

# Parámetros YOLO
model_path = "modelos-YOLO-parcial3/v11n-320-50-aug-rgb-gray-reb-blur-2/weights/best.pt"
model = YOLO(model_path)
USANDO_YOLO = True
INFERENCE_RATIO = 10; inference_ctr = 0

# Parámetros de cálculo de FPS
prevFrameTime = time.time(); newFrameTime = 0
allFPS = []

# Parámetros visualización
CAP = cv2.VideoCapture(0)
IMAGE_SIZE = 1 # tamaño del frame a visualizar; dejar en 1 para convervar tamaño original

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
	"""
	Calcula los fotogramas por segundo (FPS) basándose en el tiempo transcurrido entre dos frames.
	Utiliza las variables globales prevFrameTime y newFrameTime para medir el intervalo de tiempo entre el frame anterior y el actual.
	Actualiza prevFrameTime con el tiempo actual después de calcular el FPS.
	Retorna:
		float: El valor de FPS calculado.
	"""
	
	global prevFrameTime, newFrameTime
	newFrameTime = time.time()
	fps = 1 / (newFrameTime - prevFrameTime)
	prevFrameTime = newFrameTime
	return fps


def getInference_frame_boxes_pred(imgFrame):
	"""
	Realiza la inferencia sobre un frame de imagen utilizando el modelo YOLO si está habilitado.
	Args:
		imgFrame (numpy.ndarray): Imagen/frame sobre el cual se realizará la inferencia.
	Returns:
		frame (numpy.ndarray): Imagen anotada con las predicciones (si YOLO está activo).
		predictionBoxes (list): Lista de cajas de predicción detectadas por el modelo YOLO.
		prediction (Any): Resultado completo de la inferencia del modelo YOLO, o None si no se utiliza YOLO.
	Nota:
		- Si la variable global USANDO_YOLO es False, no se realiza inferencia y se retorna la imagen original,
		  una lista vacía de cajas y None como predicción.
		- El parámetro 'conf' controla el umbral de confianza para las detecciones del modelo YOLO.
	"""

	global USANDO_YOLO
	if USANDO_YOLO:
		prediction = model(imgFrame, verbose=False, conf=0.75)
		predictionBoxes = prediction[0].boxes
		frame = prediction[0].plot()

	else:
		predictionBoxes = []
		frame = imgFrame
		prediction = None
	return frame, predictionBoxes, prediction



# Loop principal -----------------------------------------------------------------------
while True:
	ret, frame = CAP.read()
	if not ret:
		break
	fps = getFPS()
	allFPS.append(fps)
	frame = cv2.resize(frame, None, fx=IMAGE_SIZE, fy=IMAGE_SIZE)
	inference_ctr += 1
	if inference_ctr % INFERENCE_RATIO == 0:
		frame, predictionBoxes, prediction = getInference_frame_boxes_pred(frame)
	
	# HUD
	cv2.imshow("YOLO Inference", frame)
	if cv2.waitKey(1) & 0xFF == ord('q'):
		meanFPS = np.mean(allFPS)
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

