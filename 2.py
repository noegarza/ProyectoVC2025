import numpy as np 
import cv2
import serial
import time

from datetime import datetime
import subprocess


# Conexión al Arduino (ajusta si tu puerto es diferente)
arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
time.sleep(2)  # Esperar a que Arduino reinicie

webcam = cv2.VideoCapture(0)

# Variable temporal para guardar el frame anterior
prev_color = None

while True: 
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")

    # Read the video frame
    _, imageFrame = webcam.read()
     

    # Convert to HSV color space
    hsvFrame = cv2.cvtColor(imageFrame, cv2.COLOR_BGR2HSV) 

    # Define color ranges and masks (fine-tuned)
    # Red can wrap around the hue, so we use two ranges
    red_lower1 = np.array([0, 120, 70], np.uint8)
    red_upper1 = np.array([10, 255, 255], np.uint8)
    red_lower2 = np.array([170, 120, 70], np.uint8)
    red_upper2 = np.array([180, 255, 255], np.uint8)
    red_mask1 = cv2.inRange(hsvFrame, red_lower1, red_upper1)
    red_mask2 = cv2.inRange(hsvFrame, red_lower2, red_upper2)
    red_mask = cv2.addWeighted(red_mask1, 1.0, red_mask2, 1.0, 0.0)

    green_lower = np.array([36, 100, 100], np.uint8)
    green_upper = np.array([86, 255, 255], np.uint8)
    green_mask = cv2.inRange(hsvFrame, green_lower, green_upper)

    blue_lower = np.array([94, 80, 2], np.uint8)
    blue_upper = np.array([126, 255, 255], np.uint8)
    blue_mask = cv2.inRange(hsvFrame, blue_lower, blue_upper)

    white_lower = np.array([0, 0, 210], np.uint8)
    white_upper = np.array([180, 40, 255], np.uint8)
    white_mask = cv2.inRange(hsvFrame, white_lower, white_upper)

    # Morphological Transform (Dilation + Opening to reduce noise)
    kernel = np.ones((5, 5), "uint8") 
    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel)
    red_mask = cv2.dilate(red_mask, kernel)
    green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_OPEN, kernel)
    green_mask = cv2.dilate(green_mask, kernel)
    blue_mask = cv2.morphologyEx(blue_mask, cv2.MORPH_OPEN, kernel)
    blue_mask = cv2.dilate(blue_mask, kernel)
    white_mask = cv2.morphologyEx(white_mask, cv2.MORPH_OPEN, kernel)
    white_mask = cv2.dilate(white_mask, kernel)

    # Store contours and their metadata
    max_area = 1000  # Minimum area threshold
    max_contour = None
    max_color = None
    max_color_name = None
    max_bounding_rect = None

    # Process contours for each color
    color_masks = [
        (red_mask, "rojo", (0, 0, 255)), # atras
        (green_mask, "verde", (0, 255, 0)), # derecha
        (blue_mask, "azul", (255, 0, 0)), # izquierda
        (white_mask, "blanco", (255, 255, 255)) #adelante
    ]
    comando = '5'  # Default command for no color detected
    for mask, color_name, color_bgr in color_masks:
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > max_area:
                max_area = area
                max_contour = contour
                max_color = color_bgr
                max_color_name = color_name
                max_bounding_rect = cv2.boundingRect(contour)
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


    # Draw only the largest contour, if found
    if max_contour is not None:
        x, y, w, h = max_bounding_rect
        imageFrame = cv2.rectangle(imageFrame, (x, y), (x + w, y + h), max_color, 2)
        cv2.putText(imageFrame, max_color_name, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, max_color, 2)

    arduino.write(comando.encode())  # Envía el comando
    print("Arduino:", max_color_name)



    
    if prev_color is not max_color_name and max_color_name is not None:

        print("Color diferente detectado!")

        # Aquí puedes hacer lo que quieras (ej: guardar imagen, mandar señal, etc.)
        filename = f"{max_color_name}_{timestamp}.jpg"
        cv2.imwrite(filename, imageFrame)

        subprocess.Popen(["rclone", "copy", filename, "vc:/imgs_colores/"])
        print("Subido a Drive:", filename)

    prev_color = max_color_name

    # Display the result
    cv2.imshow("Multiple Color Detection in Real-Time", imageFrame) 
    if cv2.waitKey(1) & 0xFF == ord('q'): 
        webcam.release()