import math
import os
import json
from typing import Counter
import numpy as np
import matplotlib.pyplot as plt
from nltk.translate.bleu_score import SmoothingFunction, corpus_bleu
from rouge import Rouge
from nltk.translate.meteor_score import meteor_score
import nltk
nltk.download('wordnet')
from sklearn.metrics import accuracy_score

# Helper function to read text files
def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read().strip()

# Function to calculate BLEU score
def calculate_bleu(reference, candidate):
    reference_tokens = reference.split()
    candidate_tokens = candidate.split()

    ref_count = Counter(reference_tokens)
    cand_count = Counter(candidate_tokens)

    # Count matching tokens
    match_count = sum((min(ref_count[token], cand_count[token]) for token in cand_count))

    # Calculate precision
    precision = match_count / len(candidate_tokens) if len(candidate_tokens) > 0 else 0

    # Brevity penalty
    bp = 1 if len(candidate_tokens) > len(reference_tokens) else math.exp(1 - len(reference_tokens) / len(candidate_tokens))

    # BLEU-1 score
    bleu_score = bp * precision
    return bleu_score

# Function to calculate ROUGE scores
def calculate_rouge(reference, candidate):
    rouge = Rouge()
    scores = rouge.get_scores(candidate, reference, avg=True)
    return scores

# Function to calculate METEOR score
def calculate_meteor(reference, candidate):
    reference_tokens = reference.split()
    candidate_tokens = candidate.split()
    return meteor_score([reference_tokens], candidate_tokens)

# Function to evaluate all metrics
def evaluate_metrics(reference, candidate):
    bleu = calculate_bleu(reference, candidate)
    rouge = calculate_rouge(reference, candidate)
    meteor = calculate_meteor(reference, candidate)
    return {
        'BLEU': bleu,
        'ROUGE-1': rouge['rouge-1']['f'],
        'ROUGE-2': rouge['rouge-2']['f'],
        'ROUGE-L': rouge['rouge-l']['f'],
        'METEOR': meteor
    }

# Load ground truth
ground_truth_path = 'got/Detects_remote_task_creation_via_at.exe_or_API_interacting_with_ATSVC_namedpipe.txt'  # Actual path to GoT file
ground_truth = read_file(ground_truth_path)

# Directory with generated responses
generated_responses_dir = 'outputs_cap_6/Detects_remote_task_creation_via_at.exe_or_API_interacting_with_ATSVC_namedpipe'  # Directory with LLM outputs

# Collecting all results
results = []
for file_name in os.listdir(generated_responses_dir):
    if not file_name.endswith('.txt'):
      continue
    file_path = os.path.join(generated_responses_dir, file_name)
    candidate = read_file(file_path)
    metrics = evaluate_metrics(ground_truth, candidate)
    metrics['file'] = file_name
    results.append(metrics)

# average_metrics = {}
# for result in results:
#     model_name = result['file']
#     if model_name not in average_metrics:
#         average_metrics[model_name] = {
#             'BLEU': [],
#             'ROUGE-1': [],
#             'ROUGE-2': [],
#             'ROUGE-L': [],
#             'METEOR': []
#         }
#     average_metrics[model_name]['BLEU'].append(result['BLEU'])
#     average_metrics[model_name]['ROUGE-1'].append(result['ROUGE-1'])
#     average_metrics[model_name]['ROUGE-2'].append(result['ROUGE-2'])
#     average_metrics[model_name]['ROUGE-L'].append(result['ROUGE-L'])
#     average_metrics[model_name]['METEOR'].append(result['METEOR'])

def calculate_average_metrics(results):
  average_metrics = {}
  for result in results:
    model_name = result['file']
    # Check if model exists. If not, create a dictionary with all metrics initialized to empty lists.
    average_metrics.setdefault(model_name, {'BLEU': [], 'ROUGE-1': [], 'ROUGE-2': [], 'ROUGE-L': [], 'METEOR': []})
    # Update each metric list with the corresponding value from the result.
    for metric, value in result.items():
      if metric in average_metrics[model_name]:  # Ensure metric is valid (optional)
        average_metrics[model_name][metric].append(value)

  # Now, all models in average_metrics should have the same number of metrics (5).
  return average_metrics

average_metrics = calculate_average_metrics(results)

for model_name, metrics in average_metrics.items():
    metrics['BLEU'] = np.mean(metrics['BLEU'])
    metrics['ROUGE-1'] = np.mean(metrics['ROUGE-1'])
    metrics['ROUGE-2'] = np.mean(metrics['ROUGE-2'])
    metrics['ROUGE-L'] = np.mean(metrics['ROUGE-L'])
    metrics['METEOR'] = np.mean(metrics['METEOR'])

def create_radar_chart(model_name, metrics, save_path):
    labels = list(metrics.keys())
    values = list(metrics.values())

    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]
    print(model_name, labels, angles)
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    ax.plot(angles[:-1], values, color='blue', linewidth=2)
    ax.fill(angles[:-1], values, color='blue', alpha=0.25)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)

    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_ylim(0, 0.6)

    ax.set_title(f'Metrics for Model: {model_name}')
    ax.grid(True)

    plt.savefig(save_path)
    plt.close()

for model_name, metrics in average_metrics.items():
    save_path = f"{model_name}_radar_chart_closed.png"
    create_radar_chart(model_name, metrics, save_path)


