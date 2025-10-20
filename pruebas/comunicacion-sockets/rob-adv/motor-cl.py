import socket
import msvcrt
import time


### VARIABLES GLOBALES DEL MOTOR PARA EL CLIENTE
HOST = '172.32.194.124'  # IP de la RPi
PORT = 50000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
current_key = None  # tecla que estamos enviando

# Procesos de inicio
print("Mantén pulsada W/Aw/S/D para mover, suelta para parar. Q para salir.")
def send_cmd(cmd):
    try:
        client.sendall(cmd.encode())
    except:
        pass
send_cmd('stop') # Arrancamos frenados


### BUCLE PRINCIPAL PARA DETECTAR LAS TECLAS DE LOS MOTORES ###
try:
    while True:
        # Si hay una tecla disponible
        if msvcrt.kbhit():
            key = msvcrt.getch()
            # Puede venir en bytes; ignoramos especiales
            if not key:
                continue
            try:
                k = key.decode('utf-8').lower()
            except:
                continue

            if k == 'q':
                break

            # Solo nos interesan WASD
            if k in ['w', 'a', 's', 'd']:
                # Si cambió la tecla activa, la enviamos
                if k != current_key:
                    send_cmd(k)
                    current_key = k

        else:
            # No hay tecla nueva: si antes había una pulsada, la solto
            if current_key is not None:
                send_cmd('stop')
                current_key = None

        time.sleep(0.05)  # reducir carga CPU

finally:
    client.close()
    print("Cliente cerrado.")
