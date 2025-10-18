import serial
import time

# Ajusta este puerto según tu caso
puerto = '/dev/ttyACM0'
baudrate = 9600

# Abrir conexión serial
arduino = serial.Serial(puerto, baudrate, timeout=1)
time.sleep(2)  # Espera a que el Arduino se reinicie

def enviar_comando(cmd):
    """Envía un comando como texto (por ejemplo '1', '2', '3') al Arduino."""
    arduino.write((cmd + '\n').encode())
    print(f"Comando enviado: {cmd}")

try:
    while True:
        cmd = input("Ingresa comando (1,2,3,q para salir): ").strip()
        if cmd == 'q':
            break
        if cmd in ['1', '2', '3']:
            enviar_comando(cmd)
        else:
            print("Comando no válido.")
finally:
    arduino.close()
    print("Conexión cerrada.")
