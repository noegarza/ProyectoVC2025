# servidor.py
import socket
import threading
import pickle
import struct
import time
import cv2
import traceback


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

conn_vid,  addr_v = srv_vid .accept()
print(f"[SERVIDOR] Video conectado:   {addr_v}")


# — Hilo de vídeo —

cap = cv2.VideoCapture(1)
while True:
    ret, frame = cap.read()
    if not ret:
        break
    else:
        _, encimg = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
        data = encimg.tobytes()
        try:
            conn_vid.sendall(struct.pack("Q", len(data)) + data)
        except Exception as e:
            print("Error enviando frame:", e)
            break
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cap.release()
            break
