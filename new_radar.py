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

# Save results to a JSON file
with open('evaluation_results.json', 'w') as json_file:
    json.dump(results, json_file, indent=4)

# Group results by LLM (assuming filenames contain the LLM name)
llm_metrics = {}
for result in results:
    llm_name = result['file'].split('_')[0]  # Adjust the split logic based on actual filenames
    if llm_name not in llm_metrics:
        llm_metrics[llm_name] = {'BLEU': [], 'ROUGE-1': [], 'ROUGE-2': [], 'ROUGE-L': [], 'METEOR': []}
    llm_metrics[llm_name]['BLEU'].append(result['BLEU'])
    llm_metrics[llm_name]['ROUGE-1'].append(result['ROUGE-1'])
    llm_metrics[llm_name]['ROUGE-2'].append(result['ROUGE-2'])
    llm_metrics[llm_name]['ROUGE-L'].append(result['ROUGE-L'])
    llm_metrics[llm_name]['METEOR'].append(result['METEOR'])

# Calculate average metrics for each LLM
average_metrics = {}
for llm, metrics in llm_metrics.items():
    average_metrics[llm] = {
        'BLEU': np.mean(metrics['BLEU']),
        'ROUGE-1': np.mean(metrics['ROUGE-1']),
        'ROUGE-2': np.mean(metrics['ROUGE-2']),
        'ROUGE-L': np.mean(metrics['ROUGE-L']),
        'METEOR': np.mean(metrics['METEOR'])
    }

# Plot radar chart
categories = ['BLEU', 'ROUGE-1', 'ROUGE-2', 'ROUGE-L', 'METEOR']
num_vars = len(categories)

angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
angles += angles[:1]

fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

for llm, metrics in average_metrics.items():
    values = list(metrics.values())
    values += values[:1]
    ax.plot(angles, values, label=llm)
    ax.fill(angles, values, alpha=0.25)

ax.set_theta_offset(np.pi / 2)
ax.set_theta_direction(-1)

ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories)

ax.set_ylim(0, 0.6)

plt.legend(loc='upper right', bbox_to_anchor=(1.1, 1.1))
plt.title('Average Metrics for Different LLMs')
plt.savefig('radar_chart_zoom.png')
plt.show()
