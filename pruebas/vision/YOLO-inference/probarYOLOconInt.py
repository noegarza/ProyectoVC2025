from ultralytics import YOLO
import cv2
import numpy as np

# Ruta al modelo entrenado
model_path = "modelos-YOLO/v8n-e10-imgsz640/weights/best.pt"
model = YOLO(model_path)

# Para guardar los últimos 2 puntos detectados
last_points = []  # cada punto es (frame_idx, x, y)
frame_idx = 0

# Abrir cámara
cap = cv2.VideoCapture(0)
while True:
	ret, frame = cap.read()
	if not ret:
		break
	# Inferencia YOLOv8 (sin verbose)
	frame = cv2.resize(frame, None, fx=0.5, fy=0.5)
	results = model(frame, verbose=False)
	boxes = results[0].boxes
	detected = False
	if boxes is not None and len(boxes) > 0:
		# Tomar la primera detección (asume solo una pelota)
		box = boxes[0].xyxy[0].cpu().numpy()
		x1, y1, x2, y2 = box
		cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
		last_points.append((frame_idx, cx, cy))
		if len(last_points) > 2:
			last_points.pop(0)
		detected = True
	# Interpolación lineal si no hay detección y hay 2 puntos previos
	if not detected and len(last_points) == 2:
		frames = np.array([p[0] for p in last_points])
		xs = np.array([p[1] for p in last_points])
		ys = np.array([p[2] for p in last_points])
		# Ajuste lineal para x y y por separado
		coef_x = np.polyfit(frames, xs, 1)
		coef_y = np.polyfit(frames, ys, 1)
		next_frame = frame_idx
		pred_x = np.polyval(coef_x, next_frame)
		pred_y = np.polyval(coef_y, next_frame)
		# Dibujar predicción lineal (círculo rojo)
		annotated_frame = results[0].plot()
		cv2.circle(annotated_frame, (int(pred_x), int(pred_y)), 10, (0,0,255), 2)
	else:
		annotated_frame = results[0].plot()
		if detected:
			# Dibujar detección (círculo verde)
			cv2.circle(annotated_frame, (int(cx), int(cy)), 10, (0,255,0), 2)
	cv2.imshow("YOLO+Lineal", annotated_frame)
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break
	frame_idx += 1
cap.release()
cv2.destroyAllWindows()

