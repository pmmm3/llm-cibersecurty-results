import locale
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from datetime import datetime, timedelta
locale.setlocale(locale.LC_TIME,'es_ES')
# Define tasks and their start and end dates
tasks = [
    {"Task": "Estudio del estado del arte", "Start": "2024-01-01", "End": "2024-02-25"},
    {"Task": "Desarrollo del marco de trabajo", "Start": "2024-03-01", "End": "2024-03-30"},
    {"Task": "Definición del entorno de experimentación", "Start": "2024-03-18", "End": "2024-04-10"},
    {"Task": "Implementación del sistema ChatIDS", "Start": "2024-04-01", "End": "2024-04-30"},
    {"Task": "Evaluación y pruebas del sistema", "Start": "2024-05-01", "End": "2024-05-30"},
    {"Task": "Definición de las metodologías de evaluación", "Start": "2024-05-31", "End": "2024-06-25"},
    {"Task": "Redacción del informe final", "Start": "2024-01-20", "End": "2024-06-30"}
]

# Define meetings and their dates
meetings = [
    {"Meeting": "Primera reunión", "Date": "2024-01-12"},
    {"Meeting": "Revisión inicial", "Date": "2024-01-25"},
    {"Meeting": "Segunda revisión", "Date": "2024-02-21"},
    {"Meeting": "Ajuste de objetivos", "Date": "2024-04-08"},
    {"Meeting": "Evaluación del estado", "Date": "2024-05-15"},
    {"Meeting": "Ajustes de metodología", "Date": "2024-06-12"},
    {"Meeting": "Última revisión", "Date": "2024-07-03"},
    {"Meeting": "Preparación de la presentación", "Date": "2024-07-10"}
]

# Convert to DataFrame
tasks_df = pd.DataFrame(tasks)
meetings_df = pd.DataFrame(meetings)

# Convert date strings to datetime objects
tasks_df['Start'] = pd.to_datetime(tasks_df['Start'])
tasks_df['End'] = pd.to_datetime(tasks_df['End'])
meetings_df['Date'] = pd.to_datetime(meetings_df['Date'])

# Plot Gantt chart
fig, ax = plt.subplots(figsize=(10, 6))

# Plot tasks
for idx, task in tasks_df.iterrows():
    ax.barh(task['Task'], (task['End'] - task['Start']).days, left=task['Start'], color='skyblue')

# Plot meetings
for idx, meeting in meetings_df.iterrows():
    ax.plot(meeting['Date'], len(tasks_df) - idx - 1, 'ro')  # Place a red dot for each meeting

# Format x-axis
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%B"))
plt.xticks(rotation=45)

# Labels and grid
ax.set_xlabel('Fecha')
ax.set_ylabel('Tareas')
ax.set_title('Diagrama de Gantt del Proyecto')
ax.grid(True)

plt.tight_layout()
plt.savefig("./gantt_chart.png")
plt.show()
