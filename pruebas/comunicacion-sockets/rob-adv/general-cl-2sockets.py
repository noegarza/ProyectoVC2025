# cliente.py
import socket
import threading
import pickle
import struct
import cv2
import csv
import os
import time
from datetime import datetime

HOST       = '172.32.194.124'
CTRL_PORT  = 50000
VIDEO_PORT = 50001

# — Carpeta y CSV de temperaturas —
csv_path = "datos_csv"
os.makedirs(csv_path, exist_ok=True)
csv_file = os.path.join(csv_path, "temperaturas.csv")

# — Conexiones —
ctrl_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ctrl_sock.connect((HOST, CTRL_PORT))

vid_sock  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
vid_sock.connect((HOST, VIDEO_PORT))

# — Variables globales —
streaming     = False
temp_data     = []
saving_active = False
payload_size  = struct.calcsize("Q")
data_buffer   = b""

# — Hilo de control/sensores —
def recv_control():
    global streaming, saving_active, temp_data
    while True:
        msg = ctrl_sock.recv(256)
        if not msg:
            break
        text = msg.decode(errors='ignore').strip()
        if text == 'CAMERA_ON':
            print("[CTRL] Cámara encendida.")
            streaming = True
        elif text == 'CAMERA_OFF':
            print("[CTRL] Cámara apagada.")
            streaming = False
            cv2.destroyAllWindows()
        elif text.startswith('DIST'):
            print(f"[CTRL] Ultrasonido: {text.split(':')[1]} cm")
        elif text.startswith('TEMP:'):
            parts = text.split(':')
            temp = parts[1]
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[CTRL] Temperatura: {temp} °C")
            if len(parts) > 2 and parts[2] == 'SAVE':
                temp_data.append([0,0,0,temp, now])
        elif text == 'ULTRA_ON':
            print("[CTRL] Sensor ultrasónico activado.")
        elif text == 'ULTRA_OFF':
            print("[CTRL] Sensor ultrasónico desactivado.")
        elif text == 'TEMP_ON':
            print("[CTRL] Sensor de temperatura activado.")
        elif text == 'TEMP_OFF':
            print("[CTRL] Sensor de temperatura desactivado.")
        elif text == 'TEMP_SAVE_START_OK':
            print("[CTRL] Inicio guardado de temperaturas.")
            saving_active = True
            temp_data.clear()
        elif text == 'TEMP_SAVE_STOP_OK':
            print("[CTRL] Detener guardado de temperaturas.")
            saving_active = False

threading.Thread(target=recv_control, daemon=True).start()

# — Hilo de vídeo —
def recv_video():
    global data_buffer, streaming
    while True:
        if not streaming:
            time.sleep(0.1)
            continue

        # leer tamaño
        while len(data_buffer) < payload_size:
            packet = vid_sock.recv(4096)
            if not packet:
                return
            data_buffer += packet
        frame_size = struct.unpack("Q", data_buffer[:payload_size])[0]
        data_buffer = data_buffer[payload_size:]

        # leer frame
        while len(data_buffer) < frame_size:
            data_buffer += vid_sock.recv(4096)
        frame_data = data_buffer[:frame_size]
        data_buffer = data_buffer[frame_size:]

        # reconstruir y mostrar
        frame = pickle.loads(frame_data)
        cv2.imshow("Stream RPi", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            ctrl_sock.sendall(b'END_CAMERA')
            streaming = False
            cv2.destroyAllWindows()

threading.Thread(target=recv_video, daemon=True).start()

# — Función para guardar CSV de temperaturas —
def guardar_csv():
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['pixelesU','pixelesV','totalPixeles','temperatura','tiempo'])
        w.writerows(temp_data)
    print(f"[CLIENTE] Guardado {len(temp_data)} entradas en {csv_file}")

# — Menú principal —
def menu():
    print("""
1) START_CAMERA
2) END_CAMERA
3) START_ULTRA
4) END_ULTRA
5) TEMP_ON
6) TEMP_OFF
7) TEMP_SAVE_START
8) TEMP_SAVE_STOP + guardar CSV
9) SHUTDOWN y salir
          
Motores con WASD. Detener con 'q'
""")

while True:
    menu()
    op = input("Opción: ").strip()
    if   op=='1': ctrl_sock.sendall(b'START_CAMERA')
    elif op=='2': ctrl_sock.sendall(b'END_CAMERA')
    elif op=='3': ctrl_sock.sendall(b'START_ULTRA')
    elif op=='4': ctrl_sock.sendall(b'END_ULTRA')
    elif op=='5': ctrl_sock.sendall(b'TEMP_ON')
    elif op=='6': ctrl_sock.sendall(b'TEMP_OFF')
    elif op=='7': ctrl_sock.sendall(b'TEMP_SAVE_START')
    elif op=='8':
        ctrl_sock.sendall(b'TEMP_SAVE_STOP')
        guardar_csv()
    elif op=='9':
        for cmd in (b'END_CAMERA',b'END_ULTRA',b'TEMP_OFF',b'TEMP_SAVE_STOP',b'SHUTDOWN'):
            ctrl_sock.sendall(cmd)
        break
    elif op in ['w', 'a', 's', 'd', 'q']:
        ctrl_sock.sendall(op.encode())
    else:
        print("Opción inválida.")

ctrl_sock.close()
vid_sock.close()
