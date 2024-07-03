from openai import OpenAI
import os
import json



# Define las alertas de prueba
alertas = [
    {"alert_description": "MALWARE-CNC Harakit botnet traffic", "source_ip": "192.168.1.10", "destination_ip": "10.0.0.5", "protocol": "TCP", "timestamp": "2024-07-01T12:34:56Z", "additional_details": "Detected by IDS rule 1234"},
    {"alert_description": "SERVER-WEBAPP NetGear router default password login attempt admin/password", "source_ip": "172.16.0.2", "destination_ip": "192.168.0.1", "protocol": "HTTP", "timestamp": "2024-07-01T13:45:00Z", "additional_details": "Failed login attempt"},
    {"alert_description": "SURICATA MQTT unassigned message type (0 or >15)", "source_ip": "203.0.113.5", "destination_ip": "192.168.2.20", "protocol": "MQTT", "timestamp": "2024-07-01T14:22:33Z", "additional_details": "Unexpected message type"},
    {"alert_description": "SURICATA HTTP Response abnormal chunked for transfer-encoding", "source_ip": "198.51.100.3", "destination_ip": "192.168.3.30", "protocol": "HTTP", "timestamp": "2024-07-01T15:01:45Z", "additional_details": "Anomaly detected in HTTP response"},
    {"alert_description": "Mirai Botnet TR-069 Worm - Generic Architecture", "source_ip": "198.18.0.1", "destination_ip": "10.0.1.2", "protocol": "TCP", "timestamp": "2024-07-01T16:10:50Z", "additional_details": "Known Mirai botnet behavior"},
    {"alert_description": "Linux.IotReaper", "source_ip": "203.0.113.11", "destination_ip": "10.1.1.5", "protocol": "TCP", "timestamp": "2024-07-01T17:30:10Z", "additional_details": "Detected activity associated with IoT Reaper"},
    {"alert_description": "Identifies IPs performing DNS lookups associated with common Tor proxies.", "source_ip": "198.51.100.23", "destination_ip": "192.168.0.40", "protocol": "DNS", "timestamp": "2024-07-01T18:45:30Z", "additional_details": "Potential Tor network use detected"},
    {"alert_description": "Detects remote task creation via at.exe or API interacting with ATSVC namedpipe", "source_ip": "192.0.2.4", "destination_ip": "10.2.2.10", "protocol": "RPC", "timestamp": "2024-07-01T19:20:15Z", "additional_details": "Remote task creation detected"}
]

# Crear directorio "got" si no existe
output_dir = "got"
os.makedirs(output_dir, exist_ok=True)

# Función para generar el ground truth usando la API de OpenAI
def generar_respuesta(alerta):
    return prompt_template.format(
        alert_description=alerta["alert_description"],
        source_ip=alerta["source_ip"],
        destination_ip=alerta["destination_ip"],
        protocol=alerta["protocol"],
        timestamp=alerta["timestamp"],
        additional_details=alerta["additional_details"]
    )
    

# Generar y almacenar el ground truth para cada alerta
for alerta in alertas:
    respuesta = generar_respuesta(alerta)
    # Nombre del archivo basado en la descripción de la alerta, sanitizado
    file_name = f"{alerta['alert_description'].replace(' ', '_').replace('/', '_').replace('>', 'greater_').replace('(', '').replace(')', '')}.txt"
    file_path = os.path.join(output_dir, file_name)
    
    # Guardar la respuesta en un archivo JSON separado
    with open(file_path, 'w') as f:
        f.write(respuesta)

# Mostrar un resumen de los archivos generados
for file in os.listdir(output_dir):
    print(f"Archivo generado: {file}")