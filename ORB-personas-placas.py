import cv2
import numpy as np
import os

# === 1. Cargar imagen de referencia de placa ===
placa_ref = cv2.imread('imgs/placa_ref.jpg', 0)  # Debe existir en tu proyecto
if placa_ref is None:
    raise FileNotFoundError('No se encontró placa_ref.jpg')

# === 2. Inicializar ORB y matcher ===
orb = cv2.ORB_create(nfeatures=1000)
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

# === 3. Detectar y describir puntos clave en la referencia ===
kp_des = []
for img in os.scandir("imgs/orb-placas-personas"):
    kp, des = orb.detectAndCompute(cv2.imread(img), None)    
    kp_des.append((kp, des))

# === 4. Abrir video/cámara ===
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    kp_frame, des_frame = orb.detectAndCompute(gray, None)
    if des_frame is not None and not kp_des:
        for kpDesTuple in kp_des:
            matches = bf.match(kpDesTuple[1], des_frame)
            matches = sorted(matches, key=lambda x: x.distance)
            # Usar los mejores 30 matches
            good_matches = matches[:30]
            if len(good_matches) > 10:
                src_pts = np.float32([kpDesTuple[0][m.queryIdx].pt for m in good_matches]).reshape(-1,1,2)
                dst_pts = np.float32([kp_frame[m.trainIdx].pt for m in good_matches]).reshape(-1,1,2)
                M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
                if M is not None:
                    h, w = placa_ref.shape
                    pts = np.float32([[0,0],[w,0],[w,h],[0,h]]).reshape(-1,1,2)
                    dst = cv2.perspectiveTransform(pts, M)
                    frame = cv2.polylines(frame, [np.int32(dst)], True, (0,255,0), 3)
    cv2.imshow('ORB Detección de Placa', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
