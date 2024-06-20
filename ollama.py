# Author: Pablo Moreno
# Date: 2024-05-15
# Description: This script collects data from the Ollama API and saves it to a file.

import os
import re
import requests
import json
import argparse

# Template used for generating warning messages based on detected alerts
template = """The Intrusion Detection System in a home network has detected an
intrusion and sent out the alert {alert}. Your job is to inform
Pablo about the alert in a warning message. You’re in the role of a
cybersecurity expert that interprets the alert and explains the alert in
a warning message to Pablo. Your goal is to inform Pablo about the
intrusion in a way he understands and motivate the user to take steps
to stop the intrusion. Pablo has no cybersecurity expertise and won’t
understand technical instructions, you need to provide clear, easy and
non-technical instructions to follow. Don’t use technical terms like "two-factor-authentication", "Intrusion Detection System", "intrusion" or "unassigned message", use simple non-technical terms instead. Don’t use
the term "Intrusion Detection System". Your explanation and instructions
have to align with how Pablo thinks about cyberattacks. The Smart
Home consists of several Smart Home Devices, the Intrusion Detection
System has detected the intrusion on the Philips Hue Bridge. The warning message
has to follow this order: Explain the intrusion, explain the potential
consequences for the user if he won’t comply with the warning message,
and give instructions on how to stop the intrusion in an itemized list."""

# Predefined list of alerts to handle
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

def generate_prompt(alert):
    """
    Generates a formatted warning message based on the provided alert.

    Parameters:
    alert (str): The alert message to incorporate into the warning template.

    Returns:
    str: The formatted warning message.
    """
    return template.format(alert=alert)

def set_args():
    """
    Configures and parses command-line arguments for the script.

    Returns:
    argparse.Namespace: The parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Ollama API client")
    parser.add_argument("--url", dest="ollama_url", help="Ollama API URL", default="http://localhost:11434", type=str)
    parser.add_argument("--models", nargs='+', help="List of models", type=str, dest="models")
    parser.add_argument("--alerts", nargs='+', help="Alert IDs", type=str, default=ARTICLE_ALERTS, dest="alerts")
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
    if not os.path.exists("outputs"):
        print("Creating 'outputs' directory...")
        os.makedirs("outputs")

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
        prompt = generate_prompt(alert)

        for model_name in models:
            try:
                print(f"Generating output for alert '{alert}' with model '{model_name}'...")
                result = call_ollama_api(args.ollama_url, model_name, prompt)
                print(f"Finished generating output for alert '{alert}' with model '{model_name}' in {result['total_duration']} nanoseconds.")

                # Sanitize alert and model names for file usage
                safe_model_name = model_name.replace(" ", "_")
                safe_alert = sanitize_alert_name(alert)
                output_dir = f"outputs/{safe_alert}"
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
