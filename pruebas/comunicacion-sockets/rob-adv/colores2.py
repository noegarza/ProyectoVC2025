"""Este usa picamera2"""

import cv2
import numpy as np
import os
import time
import csv
from picamera2 import Picamera2
import signal

# --- Configuración de carpeta y CSV ---
CARPETA = "capturas"
os.makedirs(CARPETA, exist_ok=True)
data_csv = os.path.join(CARPETA, "datos.csv")

if not os.path.exists(data_csv):
    with open(data_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["id", "color", "perimetro", "area", "centroide_x", "centroide_y"])
    next_id = 1
else:
    with open(data_csv, newline='') as f:
        rows = list(csv.reader(f))
        if len(rows) <= 1:
            next_id = 1
        else:
            try:
                next_id = int(rows[-1][0]) + 1
            except:
                next_id = 1

# --- Configuración de colores HSV ---
colores = [
    {"nombre": "Amarillo_Fosfo", "lower": np.array([15, 100, 100]), "upper": np.array([60, 255, 255])},
    {"nombre": "Verde_Fosfo",    "lower": np.array([40, 100, 100]), "upper": np.array([90, 255, 255])},
    {"nombre": "Naranja_Fosfo",  "lower": np.array([5, 150, 150]),  "upper": np.array([20, 255, 255])}
]

kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7,7))
AREA_MIN = 2000
SOLIDEZ_MIN = 0.9
COBERTURA_MIN = 0.7

def detectar_forma(cnt):
    per = cv2.arcLength(cnt, True)
    approx = cv2.approxPolyDP(cnt, 0.04 * per, True)
    v = len(approx)
    if v == 3: return "Triángulo"
    if v == 4: return "Cuadrado/Rectángulo"
    return "Círculo"

# --- Configurar Picamera2 ---
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (640, 480), "format": "RGB888"})
picam2.configure(config)
picam2.start()

# Manejar Ctrl+C para limpieza

def cleanup(sig, frame):
    picam2.stop()
    cv2.destroyAllWindows()
    exit(0)

signal.signal(signal.SIGINT, cleanup)

# --- Bucle principal ---
while True:
    # Capturar frame RGB y convertir a BGR
    frame_rgb = picam2.capture_array()
    frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

    cv2.imshow("Original", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('g'):
        ts = time.strftime("%Y%m%d_%H%M%S")
        cv2.imwrite(os.path.join(CARPETA, f"{ts}_original.png"), frame)

        # Preprocesar HSV
        blur = cv2.GaussianBlur(frame, (9,9), 0)
        hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

        with open(data_csv, 'a', newline='') as f:
            writer = csv.writer(f)
            for cfg in colores:
                mask = cv2.inRange(hsv, cfg["lower"], cfg["upper"])
                mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN,  kernel)
                mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

                # Guardar filtrada
                filtered = cv2.bitwise_and(frame, frame, mask=mask)
                cv2.imwrite(os.path.join(CARPETA, f"{ts}_{cfg['nombre']}.png"), filtered)

                # Encontrar contornos válidos
                contornos, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                for cnt in contornos:
                    area = cv2.contourArea(cnt)
                    if area < AREA_MIN:
                        continue
                    hull = cv2.convexHull(cnt)
                    if cv2.contourArea(hull) == 0 or (area / cv2.contourArea(hull)) < SOLIDEZ_MIN:
                        continue
                    mask_cnt = np.zeros(mask.shape, dtype=np.uint8)
                    cv2.drawContours(mask_cnt, [cnt], -1, 255, -1)
                    pix_color = cv2.countNonZero(cv2.bitwise_and(mask, mask_cnt))
                    if (pix_color / area) < COBERTURA_MIN:
                        continue

                    per = cv2.arcLength(cnt, True)
                    M = cv2.moments(cnt)
                    if M.get("m00", 0) == 0:
                        continue
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    forma = detectar_forma(cnt)

                    writer.writerow([next_id, cfg["nombre"], f"{per:.2f}", f"{area:.1f}", cx, cy])
                    print(f"ID:{next_id} | Color:{cfg['nombre']} | Forma:{forma} | Per:{per:.2f} | Area:{area:.1f} | Centroide:({cx},{cy})")
                    next_id += 1

        print(f"Datos guardados en '{data_csv}' con prefijo {ts}")

    elif key == 27:
        cleanup(None, None)

# Nunca debería llegar aquí, pero por si acaso:
picam2.stop()
cv2.destroyAllWindows()
