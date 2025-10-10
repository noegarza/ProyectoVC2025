import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

"""imgDir = os.path.join(os.getcwd(), #asumiendo que root dir es el repo.
                         'pruebas',
                         'vision',
                         'hsv-visualizer',
                         'output')"""


"""while True:
    try:
        print("---------------------------------")
        h = int(input('Valor H (0-179): '))
        s = int(input('Valor S (0-255): '))
        v = int(input('Valor V (0-255): '))
    except ValueError:
        print('Por favor ingresa valores numéricos válidos.')
        continue
    if not (0 <= h <= 179 and 0 <= s <= 255 and 0 <= v <= 255):
        print('Valores fuera de rango. Intenta de nuevo.')
        continue

    hsv_color = np.uint8([[[h, s, v]]])
    bgr_color = cv2.cvtColor(hsv_color, cv2.COLOR_HSV2BGR)[0][0]
    color_img = np.full((100, 200, 3), bgr_color, dtype=np.uint8)

    plt.figure(figsize=(3, 2))
    plt.imshow(cv2.cvtColor(color_img, cv2.COLOR_BGR2RGB))
    plt.axis('off')
    plt.text(10, 90, f'H:{h} S:{s} V:{v}', color='black', fontsize=12, bbox=dict(facecolor='white', alpha=0.7))
    plt.title('Color HSV visualizado')
    plt.savefig(os.path.join(imgDir, f'hsl_{h}-{s}-{v}.png'))
    plt.show()"""

# Visualizador HSV en tiempo real con sliders usando OpenCV
cv2.namedWindow('HSV Visualizer')

def nothing(x):
    pass

# Crear sliders para H, S, V
cv2.createTrackbar('H', 'HSV Visualizer', 0, 179, nothing)
cv2.createTrackbar('S', 'HSV Visualizer', 0, 255, nothing)
cv2.createTrackbar('V', 'HSV Visualizer', 0, 255, nothing)

while True:
    h = cv2.getTrackbarPos('H', 'HSV Visualizer')
    s = cv2.getTrackbarPos('S', 'HSV Visualizer')
    v = cv2.getTrackbarPos('V', 'HSV Visualizer')

    hsv_color = np.uint8([[[h, s, v]]])
    bgr_color = cv2.cvtColor(hsv_color, cv2.COLOR_HSV2BGR)[0][0]
    color_img = np.full((200, 400, 3), bgr_color, dtype=np.uint8)

    # Mostrar texto HSV en la imagen
    text = f'H:{h} S:{s} V:{v}'
    cv2.putText(color_img, text, (10, 180), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)

    cv2.imshow('HSV Visualizer', color_img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cv2.destroyAllWindows()
