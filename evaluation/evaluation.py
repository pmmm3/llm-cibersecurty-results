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
from glob import glob

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

# Get all ground truth files
ground_truth_files = glob('got/*.txt')

# Initialize overall results
overall_results = []

for ground_truth_path in ground_truth_files:
    # Load ground truth
    ground_truth = read_file(ground_truth_path)
    
    # Directory with generated responses
    base_name = os.path.basename(ground_truth_path)
    generated_responses_dir = f'outputs_cap_6/{os.path.splitext(base_name)[0]}'  # Directory with LLM outputs
    
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
    
    # Save results to a JSON file for each alert
    alert_name = os.path.splitext(base_name)[0]
    with open(f'{alert_name}_evaluation_results.json', 'w') as json_file:
        json.dump(results, json_file, indent=4)
    
    # Extract scores for plotting
    files = [r['file'] for r in results]
    bleu_scores = [r['BLEU'] for r in results]
    rouge1_scores = [r['ROUGE-1'] for r in results]
    rouge2_scores = [r['ROUGE-2'] for r in results]
    rougeL_scores = [r['ROUGE-L'] for r in results]
    meteor_scores = [r['METEOR'] for r in results]

    fixed_width = 10
    fixed_height = 15

    # Create the subplots
    fig, ax = plt.subplots(3, 1, figsize=(fixed_width, fixed_height))
    bar_width = 0.7 
    # Plot BLEU Scores
    ax[0].bar(files, bleu_scores, color='b', width=bar_width)
    ax[0].set_title(f'BLEU Scores for {alert_name}')
    ax[0].set_ylabel('Score')
    ax[0].set_xticklabels(files, rotation=45, ha='right')

    # Plot ROUGE-1 Scores
    ax[1].bar(files, rouge1_scores, color='g', width=bar_width)
    ax[1].set_title(f'ROUGE-1 Scores for {alert_name}')
    ax[1].set_ylabel('Score')
    ax[1].set_xticklabels(files, rotation=45, ha='right')

    # Plot METEOR Scores
    ax[2].bar(files, meteor_scores, color='r', width=bar_width)
    ax[2].set_title(f'METEOR Scores for {alert_name}')
    ax[2].set_ylabel('Score')
    ax[2].set_xticklabels(files, rotation=45, ha='right')

    # Adjust the layout to reduce space between the plots
    plt.subplots_adjust(hspace=0.4)  # Change the hspace to a smaller value to reduce vertical space

    plt.tight_layout()
    plt.savefig(f'{alert_name}_evaluation_results.png')

    # Interpretation of results
    print(f'Results for {alert_name}:')
    for idx, file in enumerate(files):
        print(f"File: {file}")
        print(f"  BLEU Score: {bleu_scores[idx]:.4f}")
        print(f"  ROUGE-1 Score: {rouge1_scores[idx]:.4f}")
        print(f"  METEOR Score: {meteor_scores[idx]:.4f}")
        print("\n")
    
    # Additional insights based on the metrics
    average_bleu = np.mean(bleu_scores)
    average_rouge1 = np.mean(rouge1_scores)
    average_meteor = np.mean(meteor_scores)

    print(f"Summary of Metrics for {alert_name}:")
    print(f"  Average BLEU Score: {average_bleu:.4f}")
    print(f"  Average ROUGE-1 Score: {average_rouge1:.4f}")
    print(f"  Average METEOR Score: {average_meteor:.4f}")
    print("\n" + "="*50 + "\n")
