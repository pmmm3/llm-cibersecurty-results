import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from tqdm import tqdm
import re

def load_model(model_name):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name,
                                                 local_files_only=True,
                                                 device_map=device,
                                                 torch_dtype=torch.float16)
    return tokenizer, model

def generate_text(model, tokenizer, user_input):
    inputs = tokenizer(user_input, return_tensors="pt").to(model.device)
    generated_ids = model.generate(**inputs, do_sample=True, top_p=0.84, top_k=100, max_length=2000)
    return tokenizer.batch_decode(generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]

models = {
#    "1": "Mistral-7B-v0.1",
#    "2": "Llama-2-7b-chat-hf",
#    "3": "phi-2",
#    "4": "gemma-7b",
    "5": "Meta-Llama-3-8B",
}

template = """The Intrusion Detection System in a home network has detected an
intrusion and sent out the alert {alert}. Your job is to inform
Pablo  about the alert in a warning message. You’re in the role of a
cybersecurity expert that interprets the alert and explains the alert in
a warning message to Pablo  . Your goal is to inform Jon about the
intrusion in a way he understands and motivate the user to take steps
to stop the intrusion. Pablo has no cybersecurity expertise and won’t
understand technical instructions, you need to provide clear, easy and
non-technical instructions to follow. Don’t use technical terms like ”twofactor-authentication”, ”Intrusion Detection System”, ”intrusion” or ”unassigned message”, use simple non-technical terms instead. Don’t use
the term ”Intrusion Detection System”. Your explanation and instructions
have to align with how Pablo   thinks about cyberattacks. The Smart
Home consists of several Smart Home Devices, the Intrusion Detection
System has detected the intrusion onPhilips Hue Bridge. The warning message
has to follow this order: Explain the intrusion, explain the potential
consequences for the user if he won’t comply with the warning message
and give instructions on how to stop the intrusion in an itemized list. """

def generate_prompt(alert):
    return template.format(alert=alert)

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

while True:
    print("\n\nBienvenido al laboratorio de pruebas. Seleccione un modo para comenzar o 'salir' para terminar.")
    print("1. Generar salida en fichero de todas las alertas en todos los modelos.")
    print("2. Conversar")
    print("3. Salir")
    choice = input("\nIngrese el número correspondiente al modo que desea usar: ")

    if choice == "3" or choice.lower() == "salir":
        break

    if choice == "1":
        # Generar salida en ficheros para cada modelo y alerta
        for model_key, model_name in models.items():
            print(f"Cargando modelo {model_name}...")
            tokenizer, model = load_model(model_name)
            for alert in tqdm(alerts, desc=f"Modelo {model_name}"):
                print(f"Generando salida para alerta: {alert}")
                prompt = generate_prompt(alert)
                try:
                    result = generate_text(model, tokenizer, prompt)
                    safe_model_name = re.sub(r'[^\w\s]', '', model_name)
                    safe_alert = re.sub(r'[^\w\s]', '', alert)
                    filename = f"{safe_model_name}_{safe_alert}.txt"
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write(result)
                except Exception as e:
                    print(f"Error al generar salida para alerta {alert}: {e}")
                    continue
                
            # Liberar recursos del modelo actual antes de cargar el siguiente
            del model
            torch.cuda.empty_cache()
        print("Salida generada en ficheros.")
        break

    

    if choice == "2" or choice.lower() == "conversar":
        while True:
            print("\nSeleccione un modelo:")
            for model in models:
                print(f"{model}: {models[model]}")
            print("salir: Volver atrás")
            choice_model = input("\nIngrese el número correspondiente al modelo que desea usar: ")
            if choice_model.lower() == "salir":
                break

            if choice_model not in models:
                print("\nModelo no válido. Intente de nuevo.")
                continue
            
            user_input = input("\nIngrese el texto con el que desea comenzar la conversación: ")
            model_name = models[choice_model]
            tokenizer, model = load_model(model_name)
            print("Generando texto...\n\n")
            print(generate_text(model, tokenizer, user_input))
            break




