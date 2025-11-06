"""
La idea, inicialmente, era repartirnos las tareas de modificar labels entre miembros del equipo
Esto nos llevó a crear varios proyectos de roboflow, pero al descargarlos pues todos tienen label 0.
Si esto pasa, YOLO se va a confundir, ya que no sabrá qué clase es cada cosa.

Por tanto, este script permite modificar los labels de un conjunto de imágenes y sus ficheros .txt asociados

Código creado en colaboración con IA generativa
"""
import os


"""
Modifica el label de una clase en un archivo de etiquetas YOLO.
Lee el archivo de texto especificado, busca todas las líneas donde el primer elemento (label)
coincide con old_label y lo reemplaza por new_label. Escribe los cambios en el mismo archivo.
Args:
    txt_file_path (str): Ruta al archivo de etiquetas (.txt) a modificar.
    old_label (int or str): Label original que se desea cambiar.
    new_label (int or str): Nuevo label que reemplazará al original.
"""
def setLabelInFile(txt_file_path, old_label, new_label):
    with open(txt_file_path, 'r') as file:
        lines = file.readlines()

    with open(txt_file_path, 'w') as file:
        for line in lines:
            parts = line.strip().split()
            if parts[0] == str(old_label):
                parts[0] = str(new_label)
            file.write(' '.join(parts))


"""
Modifica la label en cada archivo .txt en un directorio dado.
Args:
    directory_path (str): Ruta al directorio que contiene los archivos .txt.
    old_label (int or str): Label original que se desea cambiar.
    new_label (int or str): Nuevo label que reemplazará al original.
"""
def modifyLabelsInDirectory(directory_path, old_label, new_label):
    for filename in os.listdir(directory_path):
        if filename.endswith('.txt'):
            txt_file_path = os.path.join(directory_path, filename)
            setLabelInFile(txt_file_path, old_label, new_label)


def main():
    train_Path = "DINOSAURS-LABELING-2/train/labels"
    test_Path = "DINOSAURS-LABELING-2/test/labels"
    valid_Path = "DINOSAURS-LABELING-2/valid/labels"
    old_label = 1  # Label a cambiar
    new_label = 0  # Nuevo label

    modifyLabelsInDirectory(train_Path, old_label, new_label)
    modifyLabelsInDirectory(test_Path, old_label, new_label)
    modifyLabelsInDirectory(valid_Path, old_label, new_label)


if __name__ == "__main__":
    main()
