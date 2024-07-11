import os
import json
from collections import Counter
from glob import glob
import numpy as np
import matplotlib.pyplot as plt
from nltk.translate.bleu_score import SmoothingFunction, corpus_bleu
from rouge import Rouge
from nltk.translate.meteor_score import meteor_score
import nltk

nltk.download('wordnet')

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

# Function to create radar chart
def create_radar_chart(metrics, title):
    labels = list(metrics.keys())
    stats = list(metrics.values())

    # Number of variables
    num_vars = len(labels)

    # Compute angle of each axis
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()

    # Complete the loop
    stats += stats[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.fill(angles, stats, color='red', alpha=0.25)
    ax.plot(angles, stats, color='red', linewidth=2)

    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)

    plt.title(title, size=20, color='red', y=1.1)
    plt.savefig(f'{title}_radar.png')
    plt.close()

# Get all ground truth files
ground_truth_files = glob('got/*.txt')

all_alerts_metrics = {}

for ground_truth_path in ground_truth_files:
    # Load ground truth
    ground_truth = read_file(ground_truth_path)
    
    # Directory with generated responses
    base_name = os.path.basename(ground_truth_path)
    alert_name = os.path.splitext(base_name)[0]
    generated_responses_dir = f'outputs_cap_6/{alert_name}'  # Directory with LLM outputs
    
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
    
    # Calculate average metrics for the current alert
    avg_metrics = {
        'BLEU': np.mean([r['BLEU'] for r in results]),
        'ROUGE-1': np.mean([r['ROUGE-1'] for r in results]),
        'ROUGE-2': np.mean([r['ROUGE-2'] for r in results]),
        'ROUGE-L': np.mean([r['ROUGE-L'] for r in results]),
        'METEOR': np.mean([r['METEOR'] for r in results])
    }
    
    # Store average metrics for the current alert
    all_alerts_metrics[alert_name] = avg_metrics
    
    # Save results to a JSON file for each alert
    with open(f'{alert_name}_evaluation_results.json', 'w') as json_file:
        json.dump(results, json_file, indent=4)
    
# Create radar chart for all alerts
for alert_name, avg_metrics in all_alerts_metrics.items():
    create_radar_chart(avg_metrics, alert_name)

# Print the average metrics for all alerts
for alert_name, avg_metrics in all_alerts_metrics.items():
    print(f"Summary of Metrics for {alert_name}:")
    for metric, score in avg_metrics.items():
        print(f"  {metric}: {score:.4f}")
    print("\n" + "="*50 + "\n")
