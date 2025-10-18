from ultralytics import YOLO
import cv2
import numpy as np
try:
	from deep_sort_realtime.deepsort_tracker import DeepSort
except ImportError:
	raise ImportError("Instala deep_sort_realtime: pip install deep_sort_realtime")

# Ruta al modelo entrenado
model_path = "modelos-YOLO/v8n-e10-imgsz640/weights/best.pt"
model = YOLO(model_path)

# Inicializar Deep SORT
tracker = DeepSort(max_age=15)

# Abrir cámara
cap = cv2.VideoCapture(0)
while True:
	ret, frame = cap.read()
	if not ret:
		break
	# Inferencia YOLOv8 (sin verbose)
	results = model(frame, verbose=False)
	boxes = results[0].boxes
	detections = []
	if boxes is not None and len(boxes) > 0:
		for box in boxes:
			xyxy = box.xyxy[0].cpu().numpy()
			x1, y1, x2, y2 = xyxy
			conf = float(box.conf[0].cpu().numpy())
			cls = int(box.cls[0].cpu().numpy())
			detections.append([[x1, y1, x2, y2], conf, cls])
	# Actualizar tracker
	tracks = tracker.update_tracks(detections, frame=frame)
	# Dibujar resultados
	annotated_frame = results[0].plot()
	for track in tracks:
		if not track.is_confirmed():
			continue
		track_id = track.track_id
		ltrb = track.to_ltrb()
		x1, y1, x2, y2 = map(int, ltrb)
		cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 255), 2)
		cv2.putText(annotated_frame, f'ID {track_id}', (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)
	cv2.imshow("YOLO + DeepSORT", annotated_frame)
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break
cap.release()
cv2.destroyAllWindows()

