# servidor.py
import socket
import threading
import pickle
import struct
import time
import cv2
import traceback

HOST       = ''
VIDEO_PORT = 50000

vid_sock  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
vid_sock.connect((HOST, VIDEO_PORT))

# — Variables globales —
streaming     = False
temp_data     = []
saving_active = False
payload_size  = struct.calcsize("Q")
data_buffer   = b""