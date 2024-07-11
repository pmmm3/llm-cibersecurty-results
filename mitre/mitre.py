import csv
import io
import re
from stix2 import TAXIICollectionSource, MemorySource, Filter
from taxii2client.v20 import Collection
import tqdm

# Lista de alertas predefinidas
ARTICLE_ALERTS = [
    "MALWARE-CNC Harakit botnet traffic",
    "SERVER-WEBAPP NetGear router default password login attempt admin/password",
    "SURICATA MQTT unassigned message type (0 or >15)",
    "SURICATA HTTP Response abnormal chunked for transfer-encoding",
    "Mirai Botnet TR-069 Worm - Generic Architecture",
    "Linux.IotReaper",
    "Identifies IPs performing DNS lookups associated with common Tor proxies.",
    "Detects remote task creation via at.exe or API interacting with ATSVC namedpipe"
]

# Dominio de ATT&CK por defecto
DEFAULT_DOMAIN = "enterprise_attack"

def build_taxii_source(collection_name):
    """Downloads latest Enterprise or Mobile ATT&CK content from MITRE TAXII Server."""
    collection_map = {
        "enterprise_attack": "95ecc380-afe9-11e4-9b6c-751b66dd541e",
        "mobile_attack": "2f669986-b40b-4423-b720-4396ca6a462b"
    }
    collection_url = "https://cti-taxii.mitre.org/stix/collections/" + collection_map[collection_name] + "/"
    collection = Collection(collection_url)
    taxii_ds = TAXIICollectionSource(collection)

    # Create an in-memory source (to prevent multiple web requests)
    return MemorySource(stix_data=taxii_ds.query())

def get_all_techniques(src, source_name):
    """Filters data source by attack-pattern which extracts all ATT&CK Techniques"""
    filters = [
        Filter("type", "=", "attack-pattern"),
        Filter("external_references.source_name", "=", source_name),
    ]

    results = src.query(filters)
    return remove_deprecated(results)

def remove_deprecated(stix_objects):
    """Will remove any revoked or deprecated objects from queries made to the data source"""
    return list(
        filter(
            lambda x: x.get("x_mitre_deprecated", False) is False and x.get("revoked", False) is False,
            stix_objects
        )
    )

def grab_external_id(stix_object, source_name):
    """Grab external id from STIX2 object"""
    for external_reference in stix_object.get("external_references", []):
        if external_reference.get("source_name") == source_name:
            return external_reference["external_id"]

def escape_chars(a_string):
    """Some characters create problems when written to file"""
    return a_string.translate(str.maketrans({
        "\n": r"\\n",
    }))

def find_techniques_related_to_alerts(ds, alerts, source_name):
    """Find techniques related to given alerts"""
    all_techniques = get_all_techniques(ds, source_name)
    related_techniques_by_alert = {}

    for alert in alerts:
        alert_pattern = re.compile(re.escape(alert), re.IGNORECASE)
        related_techniques = []

        for technique in all_techniques:
            if alert_pattern.search(technique.name) or (technique.description and alert_pattern.search(technique.description)):
                related_techniques.append({
                    "TID": grab_external_id(technique, source_name),
                    "Technique Name": technique.name,
                    "Description": escape_chars(technique.description or "")
                })

        related_techniques_by_alert[alert] = related_techniques

    return related_techniques_by_alert

def main():
    # Load data source
    data_source = build_taxii_source(DEFAULT_DOMAIN)
    source_name = "mitre-attack"  # Asumimos que siempre es enterprise_attack

    # Utilizamos las alertas predefinidas
    alerts = ARTICLE_ALERTS

    # Find related techniques
    related_techniques_by_alert = find_techniques_related_to_alerts(data_source, alerts, source_name)

    # Output filename
    filename = "related_techniques_by_alert.csv"
    fieldnames = ["Alert", "TID", "Technique Name", "Description"]

    # Write results to CSV
    with io.open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for alert, techniques in related_techniques_by_alert.items():
            for technique in techniques:
                writer.writerow({
                    "Alert": alert,
                    "TID": technique["TID"],
                    "Technique Name": technique["Technique Name"],
                    "Description": technique["Description"]
                })

    print(f"Related techniques have been saved to {filename}")

if __name__ == "__main__":
    main()
