import cv2
import numpy as np
from matplotlib import pyplot as plt
import datetime
import os

def show_histogram(image):
    hueChannel = image[:, :, 2]
    hist = cv2.calcHist([hueChannel], [0], None, [256], [0, 256])
    hist_img = np.zeros((300, 256, 3), dtype=np.uint8)
    cv2.normalize(hist, hist, 0, 300, cv2.NORM_MINMAX)
    for x, y in enumerate(hist):
        cv2.line(hist_img, (x, 300), (x, 300 - int(float(y))), (0, 0, 255), 1)
    return hist_img

cap = cv2.VideoCapture(0)
captured_image = None

# definir dónde guardar imágenes 
dirTimestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
dirTitle = f'exp {dirTimestamp}'
outputDir = os.path.join(os.getcwd(), #asumiendo que root dir es el repo.
                         'pruebas-no-entregables',
                         'histogramaFotos',
                         'output')
imgDir = os.path.join(outputDir, f"{dirTitle}")
os.makedirs(imgDir, exist_ok=True)

# loop principal
numImgsGuardadas = 0
while True:
    ret, frame = cap.read()
    if not ret:
        break
    cv2.imshow('Camera', frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('t'):
        """
        Segun chat:
            Matplotlib internamente detecta eventos de teclado y mouse en su propia ventana, 
            y si presionas 'q', la ventana se cierra. Solo después de cerrar la ventana, 
            el control regresa a tu código y el loop de OpenCV continúa.
        """
        # Generar canales histograma
        captured_image = frame.copy()
        processedImage = cv2.cvtColor(captured_image, cv2.COLOR_BGR2HLS_FULL)
        h, s, l = cv2.split(processedImage)
        hHist = cv2.calcHist([h], [0], None, [256], [0, 256])
        sHist = cv2.calcHist([s], [0], None, [256], [0, 256])
        lHist = cv2.calcHist([l], [0], None, [256], [0, 256])
        
        # Mostrar histograma con matplotlib
        plt.figure('Histograma Matplotlib', figsize=(12, 6))
        plt.plot(hHist, color='black', label='H')
        plt.plot(sHist, color='green', label='S')
        plt.plot(lHist, color='yellow', label='L')
        plt.legend()
        plt.title('Histograma HSL')
        plt.xlabel('Valor de pixel')
        plt.ylabel('Frecuencia')
        plt.xticks(np.arange(0, 256, 10))
        plt.grid()

        # guardar imagenes de frame actual e histograma en carpeta correspondiente
        numImgsGuardadas += 1
        cv2.imwrite(os.path.join(imgDir, f'img-{numImgsGuardadas}.jpg'), captured_image)
        plt.savefig(os.path.join(imgDir, f'hist-hsl-{numImgsGuardadas}.png'))
        
        # se ocupa hacer todo ANTES del plt.show()
        plt.show()
        
        

cap.release()
cv2.destroyAllWindows()