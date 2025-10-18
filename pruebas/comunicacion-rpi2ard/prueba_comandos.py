import numpy as np 
import cv2
import serial
import time

arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
time.sleep(2)  # Esperar a que Arduino reinicie
comando = '0'

while True:

    max_color_name = input("sobres padrino: ")

    if max_color_name == "rojo":
        comando = '2'
    elif max_color_name == "verde":
        comando = '3'
    elif max_color_name == "blanco":
        comando = '1'
    elif max_color_name == "azul":
        comando = '4'
    else:
        comando = '5'

    print(comando)

    time.sleep(2)