# Alejandro Lozano Vessi - UDEM
# Detección de rostros en tiempo real (Haar + Tracking + Logging)

import cv2
import os
import time
import csv
import json
import math
from datetime import datetime
from collections import OrderedDict

# ===============================
# CONFIGURACIÓN
# ===============================
VIDEO_SOURCE = 1
LOCATION = "Biblioteca_UDEM"
METHOD = "HaarCascade-Face"
RUN_TIME_SECONDS = 15 * 60
MAX_MISSING_SECONDS = 2.0  # tolerancia antes de eliminar ID

# ===============================
# CREAR CARPETA DE SESIÓN
# ===============================
session_time = datetime.now().strftime("%Y%m%d_%H%M")
BASE_OUTPUT = f"output/{session_time}_{LOCATION}"
CROPS_DIR = os.path.join(BASE_OUTPUT, "captures", "crops")
FRAMES_DIR = os.path.join(BASE_OUTPUT, "captures", "frames")
os.makedirs(CROPS_DIR, exist_ok=True)
os.makedirs(FRAMES_DIR, exist_ok=True)

LOG_FILE = os.path.join(BASE_OUTPUT, "log.csv")
CONFIG_FILE = os.path.join(BASE_OUTPUT, "config.json")

config = {
    "location": LOCATION,
    "method": METHOD,
    "video_source": str(VIDEO_SOURCE),
    "run_time_seconds": RUN_TIME_SECONDS,
    "max_missing_seconds": MAX_MISSING_SECONDS,
    "created": session_time
}
with open(CONFIG_FILE, "w") as f:
    json.dump(config, f, indent=4)

# ===============================
# TRACKER POR CENTROIDES
# ===============================
class CentroidTracker:
    def __init__(self, max_missing_seconds=2.0):
        self.objects = OrderedDict()
        self.bboxes = OrderedDict()
        self.last_seen = OrderedDict()
        self.next_object_id = 1
        self.max_missing_seconds = max_missing_seconds

    def register(self, centroid, bbox):
        oid = self.next_object_id
        self.objects[oid] = centroid
        self.bboxes[oid] = bbox
        self.last_seen[oid] = time.time()
        self.next_object_id += 1
        return oid

    def deregister(self, oid):
        if oid in self.objects:
            del self.objects[oid]
            del self.bboxes[oid]
            del self.last_seen[oid]

    def update(self, rects):
        now = time.time()
        if len(rects) == 0:
            to_remove = []
            for oid, last in list(self.last_seen.items()):
                if now - last > self.max_missing_seconds:
                    to_remove.append(oid)
            for oid in to_remove:
                self.deregister(oid)
            return {}, set()

        # centroides detectados
        input_centroids = []
        for (x1, y1, x2, y2) in rects:
            cX = int((x1 + x2) / 2.0)
            cY = int((y1 + y2) / 2.0)
            input_centroids.append((cX, cY))

        if len(self.objects) == 0:
            for i, c in enumerate(input_centroids):
                self.register(c, rects[i])
            return self.bboxes.copy(), set(self.bboxes.keys())

        object_ids = list(self.objects.keys())
        object_centroids = list(self.objects.values())

        # matriz de distancias
        D = [[math.hypot(oc[0]-ic[0], oc[1]-ic[1]) for ic in input_centroids] for oc in object_centroids]
        rows = sorted(range(len(D)), key=lambda r: min(D[r]))
        cols = [D[r].index(min(D[r])) for r in rows]

        usedRows, usedCols, active_ids = set(), set(), set()
        for row, col in zip(rows, cols):
            if row in usedRows or col in usedCols:
                continue
            if D[row][col] > 80:  # umbral de distancia
                continue
            oid = object_ids[row]
            self.objects[oid] = input_centroids[col]
            self.bboxes[oid] = rects[col]
            self.last_seen[oid] = now
            usedRows.add(row)
            usedCols.add(col)
            active_ids.add(oid)

        # nuevos
        unusedCols = set(range(len(input_centroids))).difference(usedCols)
        for col in unusedCols:
            new_id = self.register(input_centroids[col], rects[col])
            active_ids.add(new_id)

        # desaparecidos
        unusedRows = set(range(len(object_centroids))).difference(usedRows)
        for row in unusedRows:
            oid = object_ids[row]
            if now - self.last_seen[oid] > self.max_missing_seconds:
                self.deregister(oid)

        return self.bboxes.copy(), active_ids

# ===============================
# CARGAR CLASIFICADOR HAAR
# ===============================
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
if face_cascade.empty():
    raise RuntimeError("No se pudo cargar haarcascade_frontalface_default.xml")

# ===============================
# VIDEO + LOG
# ===============================
cap = cv2.VideoCapture(VIDEO_SOURCE)
csv_f = open(LOG_FILE, "w", newline="", encoding="utf-8")
csv_writer = csv.writer(csv_f)
csv_writer.writerow(["timestamp", "person_id", "event", "total_count", "location", "method", "notes"])

tracker = CentroidTracker(MAX_MISSING_SECONDS)
start_time = time.time()
end_time = start_time + RUN_TIME_SECONDS
counted_ids, active_ids = set(), set()

# ===============================
# LOOP PRINCIPAL
# ===============================
while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    faces = face_cascade.detectMultiScale(gray, 1.1, 6, minSize=(60,60))
    rects = [(x, y, x+w, y+h) for (x, y, w, h) in faces]

    objects, current_ids = tracker.update(rects)

    entered = current_ids - active_ids
    exited = active_ids - current_ids
    seen = current_ids & active_ids

    # === Eventos ===
    for oid in entered:
        counted_ids.add(oid)
        (x1, y1, x2, y2) = objects[oid]
        crop = frame[y1:y2, x1:x2].copy()
        ts_safe = datetime.now().strftime("%Y%m%d_%H%M%S")
        crop_name = os.path.join(CROPS_DIR, f"{oid}_{ts_safe}.jpg")
        frame_name = os.path.join(FRAMES_DIR, f"frame_{ts_safe}.jpg")
        if crop.size > 0:
            cv2.imwrite(crop_name, crop)
        cv2.imwrite(frame_name, frame)
        csv_writer.writerow([timestamp, oid, "ENTER", len(counted_ids), LOCATION, METHOD, "Nuevo ID"])
        csv_f.flush()

    for oid in seen:
        csv_writer.writerow([timestamp, oid, "SEEN", len(counted_ids), LOCATION, METHOD, ""])
        csv_f.flush()

    for oid in exited:
        csv_writer.writerow([timestamp, oid, "EXIT", len(counted_ids), LOCATION, METHOD, "Salió"])
        csv_f.flush()

    active_ids = current_ids

    # === Dibujar solo los que están activos en este frame ===
    for oid in current_ids:
        (x1, y1, x2, y2) = objects[oid]
        cv2.rectangle(frame, (x1,y1), (x2,y2), (0,255,0), 2)
        cv2.putText(frame, f"ID {oid}", (x1, y1-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

    # HUD
    now_sec = time.time()
    time_left = max(0, int(end_time - now_sec))
    mins, secs = divmod(time_left, 60)
    cv2.putText(frame, f"Personas Detectadas: {len(counted_ids)}", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)
    cv2.putText(frame, f"Tiempo restante: {mins:02d}:{secs:02d}", (10,60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,0,0), 2)
    cv2.putText(frame, timestamp, (10,90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200,200,200), 1)

    cv2.imshow("Detección y Conteo de Rostros", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
    if now_sec >= end_time:
        break

# ===============================
# CIERRE
# ===============================
csv_writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "", "SUMMARY", len(counted_ids), LOCATION, METHOD, "Fin de sesión"])
csv_f.close()
cap.release()
cv2.destroyAllWindows()
print(f"[INFO] Sesión finalizada. Total Personas: {len(counted_ids)}")
print(f"[INFO] Resultados en: {BASE_OUTPUT}")
