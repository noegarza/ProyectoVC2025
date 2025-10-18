from ultralytics import YOLO
import cv2
import numpy as np

# Ruta al modelo entrenado
model_path = "modelos-YOLO/v8n-e10-imgsz640/weights/best.pt"
model = YOLO(model_path)

# Inicializar filtro de Kalman para (x, y) posición
kalman = cv2.KalmanFilter(4, 2)
kalman.measurementMatrix = np.array([[1,0,0,0],[0,1,0,0]], np.float32)
kalman.transitionMatrix = np.array([[1,0,1,0],[0,1,0,1],[0,0,1,0],[0,0,0,1]], np.float32)
kalman.processNoiseCov = np.eye(4, dtype=np.float32) * 2

# Abrir cámara
cap = cv2.VideoCapture(0)
while True:
	ret, frame = cap.read()
	if not ret:
		break
	# Inferencia YOLOv8 (sin verbose)
	results = model(frame, verbose=False)
	boxes = results[0].boxes
	detected = False
	if boxes is not None and len(boxes) > 0:
		# Tomar la primera detección (asume solo una pelota)
		box = boxes[0].xyxy[0].cpu().numpy()
		x1, y1, x2, y2 = box
		cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
		measurement = np.array([[np.float32(cx)], [np.float32(cy)]])
		kalman.correct(measurement)
		detected = True
	# Predicción Kalman
	prediction = kalman.predict()
	px, py = int(prediction[0]), int(prediction[1])
	# Mostrar resultados en ventana
	annotated_frame = results[0].plot()
	# Dibujar predicción Kalman (círculo azul)
	cv2.circle(annotated_frame, (px, py), 10, (255, 0, 0), 2)
	if detected:
		# Si hay detección, círculo verde
		cv2.circle(annotated_frame, (int(cx), int(cy)), 10, (0, 255, 0), 2)
	cv2.imshow("YOLO+Kalman", annotated_frame)
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break
cap.release()
cv2.destroyAllWindows()

