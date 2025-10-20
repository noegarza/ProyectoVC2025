#!/usr/bin/env python3
import socket
import threading
import time
import RPi.GPIO as GPIO

# — Pines BCM y PWM —  
IN1, IN2, ENA = 17, 27, 26      # Motor izquierdo  
BTS1, BTS2    = 15, 18          # Motor derecho  

VEL_IZQ = 100
VEL_DER = 95

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
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

srv_ctrl.listen(1)
srv_vid .listen(1)

print(f"[SERVIDOR] Control en {HOST}:{CTRL_PORT}")
print(f"[SERVIDOR] Vídeo  en {HOST}:{VIDEO_PORT}")

conn_ctrl, addr_ctrl = srv_ctrl.accept()
print(f"[SERVIDOR] Cliente control conectado desde {addr_ctrl}")

conn_vid, addr_vid = srv_vid.accept()
print(f"[SERVIDOR] Cliente vídeo   conectado desde {addr_vid}")

server_running = True

def handle_commands():
    global server_running
    while server_running:
        data = conn_ctrl.recv(1024)
        if not data:
            print("[SERVIDOR] Control desconectado, parando.")
            break
        cmd = data.decode().strip().lower()
        if   cmd == 'w':
            avanzar();     conn_ctrl.sendall(b'AVANZANDO\n')
        elif cmd == 's':
            retroceder();  conn_ctrl.sendall(b'RETROCEDIENDO\n')
        elif cmd == 'a':
            girar_izquierda(); conn_ctrl.sendall(b'GIRANDO_IZQUIERDA\n')
        elif cmd == 'd':
            girar_derecha();   conn_ctrl.sendall(b'GIRANDO_DERECHA\n')
        elif cmd == 'q':
            parar();       conn_ctrl.sendall(b'DETENIDO\n')
        elif cmd == 'shutdown':
            parar();       conn_ctrl.sendall(b'SERVIDOR_APAGADO\n')
            server_running = False
            break
        else:
            conn_ctrl.sendall(b'COMANDO_NO_RECONOCIDO\n')

def handle_video_socket():
    # Aceptamos la conexión de vídeo y luego no hacemos nada
    # Se mantiene para que el cliente pueda conectar el segundo socket
    try:
        while server_running:
            time.sleep(1)
    except:
        pass

# Lanzar hilos
threading.Thread(target=handle_commands, daemon=True).start()
threading.Thread(target=handle_video_socket, daemon=True).start()

# Esperar a shutdown
try:
    while server_running:
        time.sleep(0.1)
except KeyboardInterrupt:
    pass
finally:
    print("[SERVIDOR] Cerrando conexiones...")
    parar()
    pwmA.stop(); pwmB.stop(); pwmC.stop()
    GPIO.cleanup()
    conn_ctrl.close()
    conn_vid.close()
    srv_ctrl.close()
    srv_vid.close()
    print("[SERVIDOR] Recursos liberados. Servidor apagado.")
