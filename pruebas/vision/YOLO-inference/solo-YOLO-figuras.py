# ===========================================
# IMPORTS
# ===========================================
from ultralytics import YOLO
import cv2
import numpy as np
import time
from datetime import datetime
import subprocess
import os
import pandas as pd

clasesPorEncontrar = ["eje", "dino", "haptic"]
clasesEncontradas = []

comando = 'e'  # comando inicial
print("programa principal iniciado")

# ===========================================
# CARGAR MODELO YOLO
# ===========================================
MODEL_PATH = "modelos-YOLO-parcial3/v11n-640-50-aug-rgb-gray-reb-blur-2/weights/best.pt"
MODEL = YOLO(MODEL_PATH)
USANDO_YOLO = True

# ===========================================
# PARÁMETROS FPS
# ===========================================

prevFrameTime = time.time()
fps_ctr = 0
allFPS = []
inference_ctr = 0
INFERENCE_RATIO = 20  # inferir 1 de cada 20 frames

# ===========================================
# VIDEO
# ===========================================
CAP = cv2.VideoCapture(0)
IMAGE_SIZE = 1

# ===========================================
# EXPORTAR RESULTADOS
# ===========================================
TIME_STAMP = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
RESULTS_PATH = os.path.join(os.getcwd(),
                            'pruebas', 'vision', 'YOLO-inference',
                            'probarModeloYOLO', 'resultados.csv')

# ===========================================
# FUNCIONES
# ===========================================
def getFPS():
    global prevFrameTime
    newFrameTime = time.time()
    fps = 1 / (newFrameTime - prevFrameTime)
    prevFrameTime = newFrameTime
    return fps

def subirImagenes(clase,score,img):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")            
    filename = f"{timestamp}__{clase}__{score}__LabRobotica.jpg"
    cv2.imwrite(filename, img)

    subprocess.Popen(["rclone", "copy", filename, "vc:/imgs_colores/"])
    print("Subido a Drive:", filename)

def getInference_frame_boxes_pred(imgFrame):
    global MODEL, clasesPorEncontrar, clasesEncontradas
    if USANDO_YOLO:
        prediction = MODEL(imgFrame, verbose=False, conf=0.83)
        predictionBoxes = prediction[0].boxes
        frame = prediction[0].plot()

        if len(predictionBoxes) > 0:
            clase = int(predictionBoxes[0].cls.cpu().numpy()[0])   # ← número
            score = round(float(predictionBoxes[0].conf.cpu().numpy()[0]), 3)
            nombreClase = MODEL.names[clase]    
            if nombreClase not in clasesEncontradas:
                subirImagenes(nombreClase, score, frame)
                clasesEncontradas.append(nombreClase)
                clasesPorEncontrar.remove(nombreClase)
    else:
        predictionBoxes = []
        frame = imgFrame
        prediction = None
    return frame, predictionBoxes, prediction

# ===========================================
# LOOP PRINCIPAL
# ===========================================
while True:
    ret, frame = CAP.read()
    if not ret:
        break

    inference_ctr += 1
    fps = getFPS()
    allFPS.append(fps)

    frame = cv2.resize(frame, None, fx=IMAGE_SIZE, fy=IMAGE_SIZE)

    # --- INFERENCIA CADA N FRAMES ---
    if inference_ctr % INFERENCE_RATIO == 0:
        frame, predictionBoxes, prediction = getInference_frame_boxes_pred(frame)

    # Mostrar FPS en el frame
    fps_text = f"FPS: {fps:.2f}"
    cv2.putText(frame, fps_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
    cv2.imshow("YOLO Inference", frame)
    # Salir con Q
    if (cv2.waitKey(1) & 0xFF == ord('q')) or not clasesPorEncontrar:

        meanFPS = np.mean(allFPS)

        newResult = pd.DataFrame({
            "time stamp": [TIME_STAMP],
            "Se usó YOLO?": [USANDO_YOLO],
            "FPS": [round(meanFPS, 2)]
        })

        # Guardar CSV
        if not os.path.exists(os.path.dirname(RESULTS_PATH)):
            os.makedirs(os.path.dirname(RESULTS_PATH))

        newResult.to_csv(RESULTS_PATH, index=False)
        print(f"Resultados guardados en {RESULTS_PATH}")

        time.sleep(1)
        CAP.release()
        cv2.destroyAllWindows()
        break
