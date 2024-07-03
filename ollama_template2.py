# Author: Pablo Moreno
# Date: 2024-05-15
# Description: This script collects data from the Ollama API and saves it to a file.

import os
import re
import requests
import json
import argparse

# Template used for generating warning messages based on detected alerts
template = """
As a cybersecurity expert specializing in the interpretation of Intrusion Detection System (IDS) alerts, your goal is to provide a comprehensive, accurate, and easily understandable explanation of an IDS alert. Your analysis should utilize information from the MITRE ATT&CK framework and be structured in a way that non-technical stakeholders can comprehend.

**Alert Details:**
- **Description**: {alert_description}
- **Source IP**: {source_ip}
- **Destination IP**: {destination_ip}
- **Protocol**: {protocol}
- **Timestamp**: {timestamp}
- **Additional Details**: {additional_details}

**Instructions:**
Using the MITRE ATT&CK framework, address each of the following steps in a clearly separated manner:

1. **Interpret the Alert**: Provide a straightforward, non-technical explanation of what this alert signifies. Avoid technical jargon and focus on the essence of the alert.
   
2. **Identify Relevant MITRE ATT&CK Techniques**: For each MITRE ATT&CK technique and tactic related to this alert:
   - **Name the Technique**: Clearly state the MITRE ATT&CK technique or tactics related to this alert.
   - **Explain the Technique**: Briefly describe what this technique involves. Use citations from the MITRE ATT&CK database to enhance the explanation (e.g., "According to MITRE ATT&CK, Txxxx is...").
   - **Provide References**: Include specific URLs or identifiers from the MITRE ATT&CK database for further reading.

3. **Assess Potential Impact**: Describe, in simple terms, the possible effects on the system or network if this alert is not addressed. Consider the following aspects:
   - **Data Breach**: Risk of sensitive data being accessed or stolen.
   - **Service Disruption**: Potential for disruption of services or network operations.
   - **Financial Impact**: Possible financial consequences.
   - **Reputational Damage**: Risks to the organization's reputation.

4. **Recommend Mitigation Steps**: List clear and actionable steps that can be taken to mitigate the impact of this alert. Ensure these steps are understandable and feasible for implementation without requiring deep technical knowledge. Examples include:
   - **Immediate Actions**: Steps to take immediately to contain or mitigate the threat.
   - **Long-term Solutions**: Strategies to prevent similar alerts in the future.
   - **Best Practices**: General security best practices relevant to the alert.

**Note**: Your response should be concise, staying focused on the details provided in the alert and relevant MITRE ATT&CK information. Avoid introducing any speculative or unrelated information.

**Example Response Structure**:
1. **Interpret the Alert**:
   - "This alert indicates that a potentially malicious activity has been detected..."
2. **Identify Relevant MITRE ATT&CK Techniques**:
   - "Technique: Phishing (T1566)"
   - "Explanation: Phishing involves tricking users into providing sensitive information..."
   - "Reference: [MITRE ATT&CK T1566](https://attack.mitre.org/techniques/T1566/)"
3. **Assess Potential Impact**:
   - "If unaddressed, this could lead to unauthorized access to sensitive data, potentially causing..."
4. **Recommend Mitigation Steps**:
   - "Immediate Action: Block the IP address and investigate the source..."
   - "Long-term Solution: Implement email filtering to detect phishing attempts..."
   - "Best Practice: Educate employees on recognizing phishing emails..."

Ensure your response adheres to this format and covers each point thoroughly.
"""

# Predefined list of alerts to handle
ARTICLE_ALERTS_v1 = [
    "MALWARE-CNC Harakit botnet traffic",
    "SERVER-WEBAPP NetGear router default password login attempt admin/password",
    "SURICATA MQTT unassigned message type (0 or >15)",
    "SURICATA HTTP Response abnormal chunked for transfer-encoding",
    "Mirai Botnet TR-069 Worm - Generic Architecture",
    "Linux.IotReaper",
    "Identifies IPs performing DNS lookups associated with common Tor proxies.",
    "Detects remote task creation via at.exe or API interacting with ATSVC namedpipe"
]
ARTICLE_ALERTS = [
    {"alert_description": "MALWARE-CNC Harakit botnet traffic", "source_ip": "192.168.1.10", "destination_ip": "10.0.0.5", "protocol": "TCP", "timestamp": "2024-07-01T12:34:56Z", "additional_details": "Detected by IDS rule 1234"},
    {"alert_description": "SERVER-WEBAPP NetGear router default password login attempt admin/password", "source_ip": "172.16.0.2", "destination_ip": "192.168.0.1", "protocol": "HTTP", "timestamp": "2024-07-01T13:45:00Z", "additional_details": "Failed login attempt"},
    {"alert_description": "SURICATA MQTT unassigned message type (0 or >15)", "source_ip": "203.0.113.5", "destination_ip": "192.168.2.20", "protocol": "MQTT", "timestamp": "2024-07-01T14:22:33Z", "additional_details": "Unexpected message type"},
    {"alert_description": "SURICATA HTTP Response abnormal chunked for transfer-encoding", "source_ip": "198.51.100.3", "destination_ip": "192.168.3.30", "protocol": "HTTP", "timestamp": "2024-07-01T15:01:45Z", "additional_details": "Anomaly detected in HTTP response"},
    {"alert_description": "Mirai Botnet TR-069 Worm - Generic Architecture", "source_ip": "198.18.0.1", "destination_ip": "10.0.1.2", "protocol": "TCP", "timestamp": "2024-07-01T16:10:50Z", "additional_details": "Known Mirai botnet behavior"},
    {"alert_description": "Linux.IotReaper", "source_ip": "203.0.113.11", "destination_ip": "10.1.1.5", "protocol": "TCP", "timestamp": "2024-07-01T17:30:10Z", "additional_details": "Detected activity associated with IoT Reaper"},
    {"alert_description": "Identifies IPs performing DNS lookups associated with common Tor proxies.", "source_ip": "198.51.100.23", "destination_ip": "192.168.0.40", "protocol": "DNS", "timestamp": "2024-07-01T18:45:30Z", "additional_details": "Potential Tor network use detected"},
    {"alert_description": "Detects remote task creation via at.exe or API interacting with ATSVC namedpipe", "source_ip": "192.0.2.4", "destination_ip": "10.2.2.10", "protocol": "RPC", "timestamp": "2024-07-01T19:20:15Z", "additional_details": "Remote task creation detected"}
]

def generar_respuesta(alerta):
    return template.format(
        alert_description=alerta["alert_description"],
        source_ip=alerta["source_ip"],
        destination_ip=alerta["destination_ip"],
        protocol=alerta["protocol"],
        timestamp=alerta["timestamp"],
        additional_details=alerta["additional_details"]
    )

def set_args():
    """
    Configures and parses command-line arguments for the script.

    Returns:
    argparse.Namespace: The parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Ollama API client")
    parser.add_argument("--url", dest="ollama_url", help="Ollama API URL", default="http://localhost:11434", type=str)
    parser.add_argument("--models", nargs='+', help="List of models", type=str, dest="models")
    parser.add_argument("--alerts", nargs='+', help="Alert IDs", default=ARTICLE_ALERTS, dest="alerts")
    return parser.parse_args()

def sanitize_alert_name(alert):
    """
    Cleans and sanitizes the alert name to be used as a valid file name.

    Parameters:
    alert (str): The alert name to sanitize.

    Returns:
    str: The sanitized alert name suitable for file names.
    """
    # Remove characters that are not allowed in file names and replace spaces with underscores
    cleaned_alert = re.sub(r'[^A-Za-z0-9\-_. ]+', '', alert)
    cleaned_alert = cleaned_alert.replace(' ', '_')
    return cleaned_alert

def banner():
    """
    Prints an ASCII art banner.
    """
    print("""                                                                                                          
                 .!JJ!.              .7YY7.                 
                :B@@@@B~            ^#@@@@B:                
               .B@#^^B@&:          :#@G::#@G                
               7@@?  !@@Y:!J5PP5J!:Y@@~  ?@@!               
               Y@@~  .&@@@@#GPPG#@@@@#.  ~@@J               
               7@@Y!7?@@B?^      :?B@&?7!Y@@?               
              .5@@@@&#G7            ?B#&@@@@5.              
             ?&@#J~:.                 .:^7P&@#7             
            Y@@J.                          :Y@@J            
           ~@@5              ..              5@@^           
           ?@@?    ?P5^ :?5GGGGGG5?: ^GBY.   7@@!           
           ~@@B.  :G##JJ&G?~::::~?G&J~B&B:  .B@&:           
            5@@P.   . ?@J   ~##~   J@? .   .G@@?            
            !@@@^     7@P.   ~!.  .P@7     :#@&:            
            G@&~       !G#5?!~~!?5#G!       ^&@P            
           :@@5          ^7J5PP5J7^          5@@^           
           ^@@Y                              5@@^           
            B@&^                            :&@B.           
            !@@#^                          :B@&~            
            .#@@^                          ^@@B             
            7@@J                            ?@@?            
            B@@^                            :&@#            
            7PB.                            .BG7            
              .                              .                                                                               
    """)

def get_ollama_models(ollama_url):
    """
    Fetches a list of unique model names from the Ollama API.

    Parameters:
    ollama_url (str): The base URL of the Ollama API.

    Returns:
    list: A list of unique model names available on the Ollama API.
    """
    try:
        response = requests.get(f"{ollama_url}/api/tags")
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx and 5xx)
    except requests.RequestException as e:
        print(f"Error getting local models: {e}")
        return []

    try:
        models = response.json().get("models", [])
    except ValueError:
        print("Error decoding JSON response")
        return []

    model_names = set()
    for model in models:
        name = model.get("name", "")
        base_name = name.split(':')[0] if ':' in name else name
        model_names.add(base_name)
    
    return list(model_names)

def call_ollama_api(ollama_url, model_name, prompt):
    """
    Calls the Ollama API to generate text using a specified model and prompt.

    Parameters:
    ollama_url (str): The base URL of the Ollama API.
    model_name (str): The name of the model to use.
    prompt (str): The prompt to use for text generation.

    Returns:
    dict: A dictionary containing the generated text and performance metrics.
        - "response" (str): The generated text response.
        - "total_duration" (int): The total duration of the text generation process in nanoseconds.
        - "load_duration" (int): The duration to load the model in nanoseconds.
        - "prompt_eval_count" (int): The number of evaluations performed on the prompt.
        - "eval_duration" (int): The total duration of all evaluations in nanoseconds.

    Raises:
    requests.RequestException: If an error occurs while making the API request.
    ValueError: If there is an error decoding the JSON response.
    """
    try:
        response = requests.post(f"{ollama_url}/api/generate", json={"model": model_name, "prompt": prompt, "stream": False})
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx and 5xx)
    except requests.RequestException as e:
        raise requests.RequestException(f"Error calling Ollama API: {e}")

    try:
        json_response = response.json()
        important_params = {
            "response": json_response.get("response", ""),
            "total_duration": json_response.get("total_duration", 0),
            "load_duration": json_response.get("load_duration", 0),
            "prompt_eval_count": json_response.get("prompt_eval_count", 0),
            "eval_duration": json_response.get("eval_duration", 0)
        }
        return important_params
    except ValueError as e:
        raise ValueError("Error decoding JSON response") from e

def main():
    """
    Main execution function that processes alerts using specified models and saves the results.
    """
    banner()
    args = set_args()

    # Create 'outputs' directory if it doesn't exist
    if not os.path.exists("outputs_cap_6"):
        print("Creating 'outputs' directory...")
        os.makedirs("outputs_cap_6")

    # Fetch available models from the Ollama API
    ollama_models = get_ollama_models(args.ollama_url)

    # Filter user-specified models to those available; use all available models if none specified
    models = [model for model in args.models if model in ollama_models] if args.models else ollama_models

    if not models:
        print("No models available")
        return

    print("Available models:", models)

    # Handle the alerts, ensuring it's treated as a list
    alerts = args.alerts if isinstance(args.alerts, list) else [args.alerts]

    for alert in alerts:
        prompt = generar_respuesta(alert)
        alert = alert["alert_description"]
        for model_name in models:
            try:
                print(f"Generating output for alert '{alert}' with model '{model_name}'...")
                result = call_ollama_api(args.ollama_url, model_name, prompt)
                print(f"Finished generating output for alert '{alert}' with model '{model_name}' in {result['total_duration']} nanoseconds.")

                # Sanitize alert and model names for file usage
                safe_model_name = model_name.replace(" ", "_")
                safe_alert = sanitize_alert_name(alert)
                output_dir = f"outputs_cap_6/{safe_alert}"
                filename = f"{output_dir}/{safe_model_name}.txt"

                # Ensure the directory exists
                os.makedirs(output_dir, exist_ok=True)

                # Write the generated response to a file
                with open(filename, "w", encoding="utf-8") as f:
                    text = result["response"] if result["response"] else "No response generated"
                    f.write(text)
                    print(f"Output saved to {filename}")

                # Write the performance stats to a separate file
                stats = (f"Total duration: {result['total_duration']} ns\n"
                         f"Load duration: {result['load_duration']} ns\n"
                         f"Prompt evaluation count: {result['prompt_eval_count']}\n"
                         f"Evaluation duration: {result['eval_duration']} ns")
                with open(f"{filename}.stats", "w", encoding="utf-8") as f:
                    f.write(stats)
                    print(f"Stats saved to {filename}.stats")
            except Exception as e:
                print(f"Error generating output for alert '{alert}' with model '{model_name}': {e}")
                continue

if __name__ == "__main__":
    main()
