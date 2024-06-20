import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Función para leer datos desde un archivo con manejo de errores
def leer_datos_desde_archivo(file_path):
    data = {}
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
        for line in lines:
            if ':' in line:  # Validar el formato esperado
                key, value = line.split(':', 1)
                value = value.strip().split()[0]  # Obtener solo el valor numérico
                data[key.strip()] = int(value)
    except Exception as e:
        print(f"Error al leer el archivo {file_path}: {e}")
    return data

# Función para obtener el nombre del modelo limpio
def obtener_nombre_modelo(file_name):
    return file_name.split('_')[0].replace('.txt.stats', '')  # Eliminar la extensión y tomar la primera parte

# Función para leer todos los archivos .txt.stats en todos los subdirectorios y crear un DataFrame
def crear_dataframe_desde_carpeta_principal(principal_folder_path):
    data_list = []
    for root, dirs, files in os.walk(principal_folder_path):
        for file_name in files:
            if file_name.endswith('.txt.stats'):
                file_path = os.path.join(root, file_name)
                model_name = obtener_nombre_modelo(file_name)  # Usar la función para limpiar el nombre del modelo
                data = leer_datos_desde_archivo(file_path)
                if data:  # Asegurarse de que se haya leído algún dato
                    data['LLM'] = model_name
                    data['Alerta'] = os.path.basename(root)  # Añadir el nombre del subdirectorio como alerta
                    data_list.append(data)
    
    if not data_list:
        print("No se encontraron datos válidos en la carpeta.")
        return pd.DataFrame()
    
    return pd.DataFrame(data_list)

# Ruta de la carpeta principal que contiene los subdirectorios
principal_folder_path = './outputs'

# Crear el DataFrame
df = crear_dataframe_desde_carpeta_principal(principal_folder_path)
if df.empty:
    print("El DataFrame está vacío. No se generarán gráficos.")
else:
    # Renombrar las columnas para mayor claridad
    df.rename(columns={
        'Total duration': 'Total Duration (ns)',
        'Load duration': 'Load Duration (ns)',
        'Prompt evaluation count': 'Prompt Evaluation Count',
        'Evaluation duration': 'Evaluation Duration (ns)'
    }, inplace=True)

    # Mostrar el DataFrame para asegurarnos de que los datos se han cargado correctamente
    print("DataFrame cargado:\n", df.head())

    # Seleccionar solo las columnas numéricas y la columna 'LLM'
    numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
    grouped_columns = ['LLM'] + numeric_columns

    # Agrupar por modelo y calcular la media solo de las columnas numéricas
    df_grouped = df[grouped_columns].groupby('LLM').mean().reset_index()

    # Mostrar el DataFrame agrupado para verificar
    print("DataFrame agrupado por modelos (media de valores numéricos):\n", df_grouped)

    # Crear la carpeta 'figures' dentro de la carpeta de entrada
    figures_folder = os.path.join(principal_folder_path, 'figures')
    os.makedirs(figures_folder, exist_ok=True)

    # Configuración de estilo para los gráficos
    sns.set(style="whitegrid")

    # 1. Gráfico de Barras para el Tiempo Total de Respuesta Promedio
    plt.figure(figsize=(10, 6))
    sns.barplot(x='LLM', y='Total Duration (ns)', data=df_grouped, palette='viridis')

    plt.title('Tiempo Total de Respuesta Promedio de los Modelos LLM')
    plt.xlabel('Modelos LLM')
    plt.ylabel('Duración Total Promedio (ns)')
    plt.xticks(rotation=45)

    # Guardar el gráfico como PNG
    total_duration_file = os.path.join(figures_folder, 'total_duration_avg.png')
    plt.savefig(total_duration_file)
    plt.close()  # Cerrar la figura para liberar memoria

    # 2. Gráfico de Barras Apiladas para Duración de Carga y Evaluación Promedio
    df_grouped['Other Duration'] = df_grouped['Total Duration (ns)'] - df_grouped['Load Duration (ns)'] - df_grouped['Evaluation Duration (ns)']

    plt.figure(figsize=(12, 7))

    # Crear el gráfico apilado
    p1 = plt.bar(df_grouped['LLM'], df_grouped['Load Duration (ns)'], color='skyblue', label='Duración de Carga Promedio')
    p2 = plt.bar(df_grouped['LLM'], df_grouped['Evaluation Duration (ns)'], bottom=df_grouped['Load Duration (ns)'], color='orange', label='Duración de Evaluación Promedio')
    p3 = plt.bar(df_grouped['LLM'], df_grouped['Other Duration'], bottom=df_grouped['Load Duration (ns)'] + df_grouped['Evaluation Duration (ns)'], color='gray', label='Otra Duración Promedio')

    plt.title('Duración de Carga y Evaluación Promedio de los Modelos LLM')
    plt.xlabel('Modelos LLM')
    plt.ylabel('Duración Promedio (ns)')
    plt.xticks(rotation=45)
    plt.legend()

    # Guardar el gráfico como PNG
    stacked_duration_file = os.path.join(figures_folder, 'stacked_duration_avg.png')
    plt.savefig(stacked_duration_file)
    plt.close()  # Cerrar la figura para liberar memoria

    # 3. Gráfico de Líneas para el Número de Evaluaciones Promedio y Duración de Evaluación Promedio
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Gráfico de línea para el número de evaluaciones
    color = 'tab:blue'
    ax1.set_xlabel('Modelos LLM')
    ax1.set_ylabel('Número de Evaluaciones Promedio', color=color)
    ax1.plot(df_grouped['LLM'], df_grouped['Prompt Evaluation Count'], color=color, marker='o', label='Número de Evaluaciones Promedio')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.legend(loc='upper left')

    # Crear un segundo eje Y
    ax2 = ax1.twinx()
    color = 'tab:red'
    ax2.set_ylabel('Duración de Evaluación Promedio (ns)', color=color)
    ax2.plot(df_grouped['LLM'], df_grouped['Evaluation Duration (ns)'], color=color, marker='o', linestyle='--', label='Duración de Evaluación Promedio')
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.legend(loc='upper right')

    plt.title('Número de Evaluaciones y Duración de Evaluación Promedio de los Modelos LLM')
    plt.xticks(rotation=45)
    fig.tight_layout()

    # Guardar el gráfico como PNG
    evaluation_comparison_file = os.path.join(figures_folder, 'evaluation_comparison_avg.png')
    plt.savefig(evaluation_comparison_file)
    plt.close()  # Cerrar la figura para liberar memoria

    # Imprimir la ruta de los archivos guardados
    print(f'Los gráficos se han guardado en la carpeta: {figures_folder}')
