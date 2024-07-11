import requests
import pandas as pd

# Descargar datos STIX de MITRE ATT&CK para Enterprise
stix_url = "https://cti-taxii.mitre.org/taxii/"
response = requests.get(stix_url)

if response.status_code == 200:
    mitre_data = response.json()
else:
    print("Error al descargar los datos STIX de MITRE ATT&CK.")
    mitre_data = {}

# Función para buscar técnicas relacionadas con una alerta específica
def buscar_tecnicas(alerta, mitre_data):
    tecnicas = []
    for item in mitre_data.get('objects', []):
        if item.get('type') == 'attack-pattern':
            # Buscar coincidencias en 'name' y 'description'
            if any(alerta.lower() in item.get(field, '').lower() for field in ['name', 'description']):
                # Encontrar el external_id
                external_references = item.get('external_references', [])
                for ref in external_references:
                    if ref.get('source_name') == 'mitre-attack':
                        tecnicas.append({
                            "Technique ID": ref.get("external_id"),
                            "Description": item.get("description")
                        })
    return tecnicas

# Lista de alertas de ejemplo
alertas = [
    "SERVER-WEBAPP NetGear router default password login attempt admin/password",
    "Linux.IotReaper",
    "MALWARE-CNC Harakit botnet traffic",
    "Detects remote task creation via at.exe or API interacting with ATSVC namedpipe"
]

# Buscar técnicas para cada alerta
resultados = []
for alerta in alertas:
    tecnicas = buscar_tecnicas(alerta, mitre_data)
    for tecnica in tecnicas:
        resultados.append({
            "Alerta": alerta,
            "Technique ID": tecnica["Technique ID"],
            "Description": tecnica["Description"]
        })

# Mostrar los resultados
df_resultados = pd.DataFrame(resultados)
print(df_resultados)

# Guardar los resultados en un archivo CSV
df_resultados.to_csv("alertas_mitre_mapping.csv", index=False)
