import os
import json

# Directorio raíz a recorrer
root_dir = r"C:\Users\pablo\Documents\Proyects\tfm\suricata-rules"

# Inicializa una lista para almacenar los datos
data = []

# Recorre todos los subdirectorios en el directorio raíz
for subdir, _, files in os.walk(root_dir):
    # Ignora el directorio raíz y solo procesa los subdirectorios
    if subdir == root_dir:
        continue
    
    # Nombre del subdirectorio
    dir_name = os.path.basename(subdir)
    
    # Busca el archivo que no tiene extensión .md
    for file in files:
        if not file.endswith('.md'):
            # Ruta completa del archivo
            file_path = os.path.join(subdir, file)
            
            try:
                # Lee el contenido del archivo
                with open(file_path, 'r', encoding='utf-8') as f:
                    alert_content = f.read()
                
                # Añade los datos a la lista
                data.append({
                    "directory": dir_name,
                    "alert": alert_content
                })
                break
            except UnicodeDecodeError:
                print(f"Error al decodificar el archivo: {file_path}")

# Guarda los datos en un archivo JSON
output_file = os.path.join(root_dir, "alerts.json")
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print(f"Archivo JSON generado en {output_file}")
