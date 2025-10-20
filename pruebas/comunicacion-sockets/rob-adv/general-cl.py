import threading
import pickle
import struct
import cv2
import csv
from datetime import datetime
import os
import socket

### VARIABLES GLOBALES DE CONEXION Y CLIENTE
HOST = '172.32.194.124'
PORT = 50000
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

streaming = False
temp_data = []
saving_active = False
payload_size = struct.calcsize("Q")
data = b""
csv_path = "datos_csv"
csv_file = os.path.join(csv_path, "temperaturas.csv")

if not os.path.exists(csv_path):
    os.makedirs(csv_path)

# funcion para recibir confirmaciones continuamente del servidor
def recibir():
    global streaming, data, saving_active, temp_data
    while True:
        try:
            if streaming:
                while len(data) < payload_size:
                    packet = client.recv(4096)
                    if not packet:
                        return
                    data += packet

                packed_msg_size = data[:payload_size]
                msg_size = struct.unpack("Q", packed_msg_size)[0]
                data = data[payload_size:]

                while len(data) < msg_size:
                    data += client.recv(4096)

                frame_data = data[:msg_size]
                data = data[msg_size:]

                frame = pickle.loads(frame_data)
                cv2.imshow("Vista desde la Raspberry Pi", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    streaming = False
                    cv2.destroyAllWindows()
                    client.sendall(b'END_CAMERA')
            else:
                msg = client.recv(1024).decode(errors='ignore').strip()
                if msg == 'CAMERA_ON':
                    print("Cámara encendida.")
                    streaming = True
                elif msg == 'CAMERA_OFF':
                    print("Cámara apagada.")
                    streaming = False
                    cv2.destroyAllWindows()
                elif msg == 'CAMERA_ERROR':
                    print("Error al iniciar la cámara.")
                    streaming = False
                elif msg.startswith('DIST:'):
                    print(f"Distancia: {msg.split(':')[1]} cm")
                elif msg.startswith('TEMP:'):
                    partes = msg.split(':')
                    temperatura = partes[1]
                    now = datetime.now()
                    print(f"Temperatura actual: {temperatura} °C")
                    if len(partes) > 2 and partes[2] == 'SAVE':
                        tiempo = now.strftime('%Y-%m-%d %H:%M:%S')
                        temp_data.append([0, 0, 0, temperatura, tiempo])
                elif msg == 'ULTRA_ON':
                    print("Sensor ultrasónico activado.")
                elif msg == 'ULTRA_OFF':
                    print("Sensor ultrasónico desactivado.")
                elif msg == 'TEMP_ON':
                    print("Sensor de temperatura activado.")
                elif msg == 'TEMP_OFF':
                    print("Sensor de temperatura desactivado.")
                elif msg == 'TEMP_SAVE_START_OK':
                    print("Guardado de temperatura iniciado.")
                    temp_data.clear()
                    saving_active = True
                elif msg == 'TEMP_SAVE_STOP_OK':
                    print("Guardado de temperatura detenido.")
                    saving_active = False
                else:
                    print("Estado:", msg)
        except Exception as e:
            print("Error general:", e)
            streaming = False
            cv2.destroyAllWindows()
            break

threading.Thread(target=recibir, daemon=True).start()


### FUNCIONES DEL MENU
def guardar_csv():
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['pixelesU', 'pixelesV', 'totalPixeles', 'temperatura', 'tiempo'])
        writer.writerows(temp_data)
    print(f"Archivo guardado como {csv_file}")
    print(f"Se guardaron {len(temp_data)} muestras.")


def mostrar_menu():
    print("\nMenu:")
    print("1. Encender cámara")
    print("2. Apagar cámara")
    print("3. Encender sensor ultrasónico")
    print("4. Apagar sensor ultrasónico")
    print("5. Prender sensor de temperatura")
    print("6. Apagar sensor de temperatura")
    print("7. Comenzar a guardar temperaturas")
    print("8. Detener el guardado de temperaturas")
    print("9. Salir")


### BUCLE PRINCIPAL PARA MENÚ ###
while True:
    mostrar_menu()
    opcion = input("Opción: ").strip()
    if opcion == '1':
        client.sendall(b'START_CAMERA')
    elif opcion == '2':
        client.sendall(b'END_CAMERA')
    elif opcion == '3':
        client.sendall(b'START_ULTRA')
    elif opcion == '4':
        client.sendall(b'END_ULTRA')
    elif opcion == '5':
        client.sendall(b'TEMP_ON')
    elif opcion == '6':
        client.sendall(b'TEMP_OFF')
    elif opcion == '7':
        client.sendall(b'TEMP_SAVE_START')
    elif opcion == '8':
        client.sendall(b'TEMP_SAVE_STOP')
        guardar_csv()
    elif opcion == '9':
        print("Saliendo...")
        client.sendall(b'END_CAMERA')
        client.sendall(b'END_ULTRA')
        client.sendall(b'TEMP_OFF')
        client.sendall(b'TEMP_SAVE_STOP')
        client.sendall(b'SHUTDOWN')
        break
    else:
        print("Opción no válida.")