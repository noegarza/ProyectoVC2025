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
HOST       = '172.32.172.199'
VIDEO_PORT = 50000

srv_vid  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
srv_vid .setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

srv_vid .bind((HOST, VIDEO_PORT))
srv_vid.listen(1)
print(f"[SERVIDOR] Video en {HOST}:{VIDEO_PORT}")

conn_vid,  addr_v = srv_vid .accept()
print(f"[SERVIDOR] Video conectado:   {addr_v}")