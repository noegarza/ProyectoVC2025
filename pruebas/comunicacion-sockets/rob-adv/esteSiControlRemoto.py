import RPi.GPIO as GPIO
import socket

# Pines BCM
IN1 = 17   # Motor izquierdo adelante
IN2 = 27   # Motor izquierdo atrás
ENA = 26   # PWM izquierdo

BTS1 = 15  # PWM derecho adelante
BTS2 = 18  # PWM derecho atrás

# Calibración por lado
VEL_IZQ = 100
VEL_DER = 95  # Ajustar según observación

# Configuración GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
for pin in [IN1, IN2, ENA, BTS1, BTS2]:
    GPIO.setup(pin, GPIO.OUT)

# Inicializar PWM
pwmA = GPIO.PWM(ENA, 1000)   # Izquierdo
pwmB = GPIO.PWM(BTS1, 1000)  # Derecho adelante
pwmC = GPIO.PWM(BTS2, 1000)  # Derecho atrás

pwmA.start(0)
pwmB.start(0)
pwmC.start(0)

# Funciones de movimiento
def avanzar():
    # Izquierdo adelante
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    pwmA.ChangeDutyCycle(VEL_IZQ)
    # Derecho adelante
    pwmB.ChangeDutyCycle(VEL_DER)
    pwmC.ChangeDutyCycle(0)

def retroceder():
    # Izquierdo atrás
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    pwmA.ChangeDutyCycle(VEL_IZQ)
    # Derecho atrás
    pwmB.ChangeDutyCycle(0)
    pwmC.ChangeDutyCycle(VEL_DER)

def girar_izquierda():
    # Izquierdo atrás, derecho adelante
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    pwmA.ChangeDutyCycle(VEL_IZQ)
    pwmB.ChangeDutyCycle(VEL_DER)
    pwmC.ChangeDutyCycle(0)

def girar_derecha():
    # Izquierdo adelante, derecho atrás
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    pwmA.ChangeDutyCycle(VEL_IZQ)
    pwmB.ChangeDutyCycle(0)
    pwmC.ChangeDutyCycle(VEL_DER)

def parar():
    # Ambos motores detenidos
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    pwmA.ChangeDutyCycle(0)
    pwmB.ChangeDutyCycle(0)
    pwmC.ChangeDutyCycle(0)

# Servidor TCP
HOST = '172.32.194.124'
PORT = 50000
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(1)
print(f"Esperando conexión en {HOST}:{PORT}...")
conn, addr = server.accept()
print(f"Cliente conectado desde: {addr}")

try:
    while True:
        data = conn.recv(1024)
        if not data:
            print("Conexión perdida. Deteniendo motores.")
            break
        cmd = data.decode().strip().lower()
        if cmd == 'w':
            avanzar()
            conn.sendall(b'AVANZANDO\n')
        elif cmd == 's':
            retroceder()
            conn.sendall(b'RETROCEDIENDO\n')
        elif cmd == 'a':
            girar_izquierda()
            conn.sendall(b'GIRANDO_IZQUIERDA\n')
        elif cmd == 'd':
            girar_derecha()
            conn.sendall(b'GIRANDO_DERECHA\n')
        elif cmd == 'stop':
            parar()
            conn.sendall(b'DETENIDO\n')
        else:
            conn.sendall(b'COMANDO_NO_RECONOCIDO\n')
except KeyboardInterrupt:
    print("Servidor detenido manualmente.")
finally:
    parar()
    pwmA.stop()
    pwmB.stop()
    pwmC.stop()
    GPIO.cleanup()
    conn.close()
    server.close()
    print("GPIO liberado. Conexión cerrada.")
