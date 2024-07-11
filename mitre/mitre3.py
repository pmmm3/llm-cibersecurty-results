import csv
from stix2 import TAXIICollectionSource, Filter, MemorySource
from taxii2client.v20 import Collection
import tqdm

# URL de la colección de MITRE ATT&CK Enterprise
ENTERPRISE_ATTACK_URL = "https://cti-taxii.mitre.org/stix/collections/95ecc380-afe9-11e4-9b6c-751b66dd541e/"

# Función para obtener la fuente de datos TAXII de MITRE ATT&CK
def get_mitre_attack_data(collection_url):
    collection = Collection(collection_url)
    taxii_source = TAXIICollectionSource(collection)
    return MemorySource(stix_data=taxii_source.query())

# Función para buscar técnicas relacionadas con una alerta
def map_alert_to_techniques(alert_description, attack_data):
    matched_techniques = []
    keywords = alert_description.lower().split()
    
    techniques = attack_data.query([
        Filter("type", "=", "attack-pattern")
    ])
    
    for technique in techniques:
        technique_text = (technique.get("name", "") + " " + technique.get("description", "")).lower()
        if any(keyword in technique_text for keyword in keywords):
            matched_techniques.append(technique)
            if len(matched_techniques) >= 10:  # Limitar a 10 técnicas
                break
    
    return matched_techniques

# Lista de alertas de IDS
alerts = [
    "MALWARE-CNC Harakit botnet traffic",
    "SERVER-WEBAPP NetGear router default password login attempt admin/password",
    "SURICATA MQTT unassigned message type (0 or >15)",
    "SURICATA HTTP Response abnormal chunked for transfer-encoding",
    "Mirai Botnet TR-069 Worm - Generic Architecture",
    "Linux.IotReaper",
    "Identifies IPs performing DNS lookups associated with common Tor proxies.",
    "Detects remote task creation via at.exe or API interacting with ATSVC namedpipe"
]

# Obtener los datos de MITRE ATT&CK
attack_data = get_mitre_attack_data(ENTERPRISE_ATTACK_URL)

# Mapeo de alertas a técnicas MITRE y guardado en CSV
filename = "alert_to_mitre_mapping.csv"
with open(filename, "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = ["Alert Description", "Technique ID", "Technique Name", "Technique Description"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    writer.writeheader()
    
    for alert in alerts:
        print(f"Procesando alerta: {alert}")
        matched_techniques = map_alert_to_techniques(alert, attack_data)
        
        for technique in matched_techniques:
            writer.writerow({
                "Alert Description": alert,
                "Technique ID": technique["id"],
                "Technique Name": technique["name"],
                "Technique Description": technique.get("description", "No description available")
            })

print(f"Resultados guardados en el archivo {filename}")