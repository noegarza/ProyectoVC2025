import cv2
import os

def extraer_frames(video_path, output_folder, intervalo=1):
    """
    Extrae frames de un video y los guarda como imágenes.
    
    Args:
        video_path: Ruta del video
        output_folder: Carpeta donde guardar las imágenes
        intervalo: Tomar 1 frame cada N frames (1 = todos los frames)
    """
    # Crear carpeta de salida si no existe
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Abrir el video
    video = cv2.VideoCapture(video_path)
    
    # Obtener información del video
    fps = video.get(cv2.CAP_PROP_FPS)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"FPS del video: {fps}")
    print(f"Total de frames: {total_frames}")
    
    frame_count = 0
    saved_count = 0
    
    while True:
        success, frame = video.read()
        
        if not success:
            break
        
        # Guardar frame según el intervalo
        if frame_count % intervalo == 0:
            filename = os.path.join(output_folder, f'frame_{saved_count:04d}.jpg')
            cv2.imwrite(filename, frame)
            saved_count += 1
            
            if saved_count % 10 == 0:
                print(f"Frames guardados: {saved_count}")
        
        frame_count += 1
    
    video.release()
    print(f"\n¡Listo! Se guardaron {saved_count} frames en '{output_folder}'")

# Uso
video_path = "ram.mp4"
output_folder = "frames_extraidos"

# Extraer todos los frames
extraer_frames(video_path, output_folder, intervalo=10)

# O si quieres exactamente 100 frames distribuidos uniformemente:
"""def extraer_n_frames(video_path, output_folder, n_frames=0.1):
    #Extrae exactamente N frames distribuidos uniformemente
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    video = cv2.VideoCapture(video_path)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Calcular intervalo para obtener exactamente n_frames
    intervalo = total_frames // n_frames
    
    saved_count = 0
    
    for i in range(n_frames):
        frame_pos = i * intervalo
        video.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
        success, frame = video.read()
        
        if success:
            filename = os.path.join(output_folder, f'frame_{saved_count:04d}.jpg')
            cv2.imwrite(filename, frame)
            saved_count += 1
    
    video.release()
    print(f"Se guardaron {saved_count} frames en '{output_folder}'")

# Para exactamente 100 fotos
extraer_n_frames("mi_video.mp4", "frames_extraidos", 100)"""