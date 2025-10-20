# servidor.py
import socket
import threading
import pickle
import struct
import time
import cv2
import adafruit_dht
import board
import RPi.GPIO as GPIO
import traceback

# — Pines ultrasónico y DHT11 —
TRIG1, ECHO1 = 25, 8
TRIG2, ECHO2 = 7, 1
TRIG3, ECHO3 = 20,21
DHT_SENSOR   = adafruit_dht.DHT11(board.D6)

# — Pines BCM y PWM —  
IN1, IN2, ENA = 17, 27, 26      # Motor izquierdo  
BTS1, BTS2    = 15, 18          # Motor derecho  

VEL_IZQ = 100
VEL_DER = 95

# — GPIO setup —
"""GPIO.setwarnings(False)""" #descomentar en caso pasen cosas raras
GPIO.setmode(GPIO.BCM)
for t,e in ((TRIG1,ECHO1),(TRIG2,ECHO2),(TRIG3,ECHO3)):
    GPIO.setup(t, GPIO.OUT)
    GPIO.setup(e, GPIO.IN)
for pin in (IN1, IN2, ENA, BTS1, BTS2):
    GPIO.setup(pin, GPIO.OUT)

pwmA = GPIO.PWM(ENA, 1000)   # Izquierdo
pwmB = GPIO.PWM(BTS1, 1000)  # Derecho adelante
pwmC = GPIO.PWM(BTS2, 1000)  # Derecho atrás
pwmA.start(0); pwmB.start(0); pwmC.start(0)

def avanzar():
    GPIO.output(IN1, GPIO.HIGH); GPIO.output(IN2, GPIO.LOW)
    pwmA.ChangeDutyCycle(VEL_IZQ)
    pwmB.ChangeDutyCycle(VEL_DER); pwmC.ChangeDutyCycle(0)

def retroceder():
    GPIO.output(IN1, GPIO.LOW);  GPIO.output(IN2, GPIO.HIGH)
    pwmA.ChangeDutyCycle(VEL_IZQ)
    pwmB.ChangeDutyCycle(0);       pwmC.ChangeDutyCycle(VEL_DER)

def girar_izquierda():
    GPIO.output(IN1, GPIO.LOW);  GPIO.output(IN2, GPIO.HIGH)
    pwmA.ChangeDutyCycle(VEL_IZQ)
    pwmB.ChangeDutyCycle(VEL_DER); pwmC.ChangeDutyCycle(0)

def girar_derecha():
    GPIO.output(IN1, GPIO.HIGH); GPIO.output(IN2, GPIO.LOW)
    pwmA.ChangeDutyCycle(VEL_IZQ)
    pwmB.ChangeDutyCycle(0);       pwmC.ChangeDutyCycle(VEL_DER)

def parar():
    GPIO.output(IN1, GPIO.LOW);  GPIO.output(IN2, GPIO.LOW)
    pwmA.ChangeDutyCycle(0)
    pwmB.ChangeDutyCycle(0);       pwmC.ChangeDutyCycle(0)


# — Flags y estado —
camera_on    = False
ultra_on     = False
temp_on      = False
saving_temp  = False
server_run   = True
cam          = None

# — Configuración de sockets —
HOST       = '0.0.0.0'
CTRL_PORT  = 50000
VIDEO_PORT = 50001

srv_ctrl = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
srv_vid  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
srv_ctrl.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv_vid .setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

srv_ctrl.bind((HOST, CTRL_PORT))
srv_vid .bind((HOST, VIDEO_PORT))
srv_ctrl.listen(1); srv_vid.listen(1)
print(f"[SERVIDOR] Control en {HOST}:{CTRL_PORT}, vídeo en {HOST}:{VIDEO_PORT}")

conn_ctrl, addr_c = srv_ctrl.accept()
print(f"[SERVIDOR] Control conectado: {addr_c}")
conn_vid,  addr_v = srv_vid .accept()
print(f"[SERVIDOR] Video conectado:   {addr_v}")

# — Hilo de comandos/control —
def handle_commands():
    global camera_on, ultra_on, temp_on, saving_temp, server_run
    while server_run:
        try:
            cmd = conn_ctrl.recv(128).decode().strip()
            if not cmd:
                break
            if   cmd=='START_CAMERA':     camera_on=True;  conn_ctrl.sendall(b'CAMERA_ON\n')
            elif cmd=='END_CAMERA':       camera_on=False; conn_ctrl.sendall(b'CAMERA_OFF\n')
            elif cmd=='START_ULTRA':      ultra_on=True;   conn_ctrl.sendall(b'ULTRA_ON\n')
            elif cmd=='END_ULTRA':        ultra_on=False;  conn_ctrl.sendall(b'ULTRA_OFF\n')
            elif cmd=='TEMP_ON':          temp_on=True;    conn_ctrl.sendall(b'TEMP_ON\n')
            elif cmd=='TEMP_OFF':         temp_on=False;   conn_ctrl.sendall(b'TEMP_OFF\n')
            elif cmd=='TEMP_SAVE_START':  saving_temp=True;  conn_ctrl.sendall(b'TEMP_SAVE_START_OK\n')
            elif cmd=='TEMP_SAVE_STOP':   saving_temp=False; conn_ctrl.sendall(b'TEMP_SAVE_STOP_OK\n')
            elif   cmd == 'w':            avanzar();     conn_ctrl.sendall(b'AVANZANDO\n')
            elif cmd == 's':              retroceder();  conn_ctrl.sendall(b'RETROCEDIENDO\n')
            elif cmd == 'a':              girar_izquierda(); conn_ctrl.sendall(b'GIRANDO_IZQUIERDA\n')
            elif cmd == 'd':              girar_derecha();   conn_ctrl.sendall(b'GIRANDO_DERECHA\n')
            elif cmd == 'q':              parar();       conn_ctrl.sendall(b'DETENIDO\n')
            elif cmd=='SHUTDOWN':
                parar()         
                server_run=False
                conn_ctrl.sendall(b'SERVIDOR_APAGADO\n')
                break
        except Exception:
            traceback.print_exc()
            break

# — Hilo de streaming de cámara —
def stream_camera():
    global cam
    payload_size = struct.calcsize("Q")
    while server_run:
        if camera_on:
            if cam is None or not cam.isOpened():
                if cam: cam.release()
                cam = cv2.VideoCapture(0, cv2.CAP_V4L2)
                cam.set(3, 640); cam.set(4, 480)
                cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
            ret, frame = cam.read()
            if ret:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                data = pickle.dumps(gray)
                conn_vid.sendall(struct.pack("Q", len(data)) + data)
            else:
                time.sleep(0.05)
        else:
            if cam: 
                cam.release(); cam = None
            time.sleep(0.1)

# — Hilo de lectura ultrasónicos —
def read_ultrasonic():
    while server_run:
        if ultra_on:
            for idx, (t,e) in enumerate(((TRIG1,ECHO1),(TRIG2,ECHO2),(TRIG3,ECHO3)), start=1):
                GPIO.output(t, True); time.sleep(1e-5); GPIO.output(t, False)
                start = time.time()
                while GPIO.input(e)==0: start = time.time()
                while GPIO.input(e)==1: end   = time.time()
                dist = round((end-start)*17150, 2)
                conn_ctrl.sendall(f'DIST{idx}:{dist}\n'.encode())
                time.sleep(0.2)
        time.sleep(0.8)

# — Hilo de lectura temperatura —
def read_temperature():
    while server_run:
        if temp_on:
            try:
                t = DHT_SENSOR.temperature
                if t is not None:
                    msg = f'TEMP:{t}' + (":SAVE" if saving_temp else "")
                    conn_ctrl.sendall((msg+"\n").encode())
            except RuntimeError:
                pass
        time.sleep(1)

# — Arrancar hilos —
threading.Thread(target=handle_commands, daemon=True).start()
threading.Thread(target=stream_camera,    daemon=True).start()
threading.Thread(target=read_ultrasonic,   daemon=True).start()
threading.Thread(target=read_temperature,  daemon=True).start()

# — Bucle principal —
try:
    while server_run:
        time.sleep(0.1)
finally:
    parar()
    pwmA.stop(); pwmB.stop(); pwmC.stop()
    if cam: cam.release()
    conn_ctrl.close(); conn_vid.close()
    srv_ctrl.close(); srv_vid.close()
    GPIO.cleanup()
    print("[SERVIDOR] Cerrado.")
