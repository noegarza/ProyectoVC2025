import numpy as np 
import cv2
import serial
import time

webcam = cv2.VideoCapture(1)

while True: 
    xd, frame = webcam.read()
    cv2.imshow("Multiple Color Detection in Real-Time", frame) 
    if cv2.waitKey(10) & 0xFF == ord('q'): 
        webcam.release()
        cv2.destroyAllWindows() 
        break