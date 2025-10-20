import socket
import threading
import cv2
import pickle
import struct
import time
import adafruit_dht
import board
import RPi.GPIO as GPIO
import traceback

# === Pines ===
TRIG1 = 25 #PIN 22
ECHO1 = 8 #PIN 24

# el del medio
TRIG2 = 7 #PIN 26
ECHO2 = 1 #PIN 28

# el de la derecha
TRIG3 = 20 #PIN 38
ECHO3 = 21 #PIN 40


DHT_SENSOR = adafruit_dht.DHT11(board.D6)

# === GPIO Setup ===
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG1, GPIO.OUT)
GPIO.setup(ECHO1, GPIO.IN)
GPIO.setup(TRIG2, GPIO.OUT)
GPIO.setup(ECHO2, GPIO.IN)
GPIO.setup(TRIG3, GPIO.OUT)
GPIO.setup(ECHO3, GPIO.IN)

# === Estados globales ===
camera_on = False
ultra_on = False
temp_on = False
saving_temp = False
server_running = True
cam = None

# === Socket Setup ===
HOST = '172.32.194.124'
PORT =50000
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)
print(f"🔌 Esperando conexión en {HOST}:{PORT}...")
conn, addr = server.accept()
print(f"✅ Cliente conectado desde: {addr}")

def stream_camera():
    global cam
    while server_running:
        try:
            if camera_on:
                if cam is None or not cam.isOpened():
                    if cam is not None:
                        cam.release()
                    cam = cv2.VideoCapture(0, cv2.CAP_V4L2)
                    cam.set(3, 640)
                    cam.set(4, 480)
                    cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))

                    if not cam.isOpened():
                        print(" No se pudo abrir la cámara.")
                        conn.sendall(b'CAMERA_ERROR\n')
                        cam = None
                        time.sleep(2)
                        continue
                    else:
                        print(" Cámara iniciada correctamente.")

                ret, frame = cam.read()
                if ret:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    data = pickle.dumps(gray)
                    conn.sendall(struct.pack("Q", len(data)) + data)
            else:
                if cam is not None:
                    cam.release()
                    cam = None
                    print("Cámara apagada.")
                time.sleep(0.1)
        except Exception as e:
            print("Error en cámara:", e)
            traceback.print_exc()

def read_ultrasonic_all():
    while server_running:
        try:
            if ultra_on:
                for idx, (trig, echo) in enumerate([(TRIG1, ECHO1), (TRIG2, ECHO2), (TRIG3, ECHO3)], start=1):
                    GPIO.output(trig, True)
                    time.sleep(0.00001)
                    GPIO.output(trig, False)

                    pulse_start = time.time()
                    while GPIO.input(echo) == 0:
                        pulse_start = time.time()
                    while GPIO.input(echo) == 1:
                        pulse_end = time.time()

                    duration = pulse_end - pulse_start
                    distance = round(duration * 17150, 2)
                    conn.sendall(f'DIST{idx}:{distance}\n'.encode())
                    time.sleep(0.2)  # pequeña pausa entre sensores
            time.sleep(0.8)
        except Exception as e:
            print("Error en sensores ultrasónicos:", e)
            traceback.print_exc()


def read_temperature():
    while server_running:
        try:
            if temp_on:
                temperature = DHT_SENSOR.temperature
                if temperature is not None:
                    msg = f'TEMP:{temperature}'
                    if saving_temp:
                        msg += ":SAVE"
                    conn.sendall((msg + '\n').encode())
            time.sleep(1)
        except RuntimeError:
            pass
        except Exception as e:
            print("Error en sensor de temperatura:", e)
            traceback.print_exc()

def handle_commands():
    global camera_on, ultra_on, temp_on, saving_temp, server_running
    while server_running:
        try:
            data = conn.recv(1024).decode().strip()
            if data == 'START_CAMERA':
                camera_on = True
                conn.sendall(b'CAMERA_ON\n')
            elif data == 'END_CAMERA':
                camera_on = False
                conn.sendall(b'CAMERA_OFF\n')
            elif data == 'START_ULTRA':
                ultra_on = True
                conn.sendall(b'ULTRA_ON\n')
            elif data == 'END_ULTRA':
                ultra_on = False
                conn.sendall(b'ULTRA_OFF\n')
            elif data == 'TEMP_ON':
                temp_on = True
                conn.sendall(b'TEMP_ON\n')
            elif data == 'TEMP_OFF':
                temp_on = False
                conn.sendall(b'TEMP_OFF\n')
            elif data == 'TEMP_SAVE_START':
                saving_temp = True
                conn.sendall(b'TEMP_SAVE_START_OK\n')
            elif data == 'TEMP_SAVE_STOP':
                saving_temp = False
                conn.sendall(b'TEMP_SAVE_STOP_OK\n')
            elif data == 'SHUTDOWN':
                server_running = False
                print(" Servidor finalizado por el cliente.")
                break
        except Exception as e:
            print("Error en comandos:", e)
            traceback.print_exc()
            break

# === Lanzar hilos ===
threading.Thread(target=handle_commands, daemon=True).start()
threading.Thread(target=stream_camera, daemon=True).start()
threading.Thread(target=read_ultrasonic_all, daemon=True).start()
threading.Thread(target=read_temperature, daemon=True).start()

# === Bucle principal ===
try:
    while server_running:
        time.sleep(0.1)
except KeyboardInterrupt:
    print("Servidor detenido manualmente.")

# === Limpieza ===
if cam is not None:
    cam.release()
conn.close()
server.close()
GPIO.cleanup()
print("✅ Recursos liberados. Servidor cerrado.")
