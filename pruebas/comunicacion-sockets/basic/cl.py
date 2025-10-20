# servidor.py
import socket
import threading
import pickle
import struct
import numpy as np
import time
import cv2
import traceback

HOST       = '172.32.190.73'
VIDEO_PORT = 50000

vid_sock  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
vid_sock.connect((HOST, VIDEO_PORT))

# — Variables globales —
streaming     = False
temp_data     = []
saving_active = False
payload_size  = struct.calcsize("Q")
data_buffer   = b""


# — Hilo de vídeo —

while True:

    # leer tamaño
    while len(data_buffer) < payload_size:
        packet = vid_sock.recv(4096)
        if not packet:
            break
        data_buffer += packet
    frame_size = struct.unpack("Q", data_buffer[:payload_size])[0]
    data_buffer = data_buffer[payload_size:]

    # leer frame
    while len(data_buffer) < frame_size:
        data_buffer += vid_sock.recv(4096)
    frame_data = data_buffer[:frame_size]
    data_buffer = data_buffer[frame_size:]

    # reconstruir y mostrar
    img_array = np.frombuffer(frame_data, dtype=np.uint8)
    frame     = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    cv2.imshow("Stream RPi", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        