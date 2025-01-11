import json
import os
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MaxNLocator

def count_text_length(text):
    # 计算文本长度
    def is_chinese(char):
        return '\u4e00' <= char <= '\u9fff'

    if any(is_chinese(char) for char in text):
        return len(text)
    else:
        return len(text.split())

def analyze_text_lengths(input_file, output_json, output_image):
    # 分析文本长度
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    text_lengths = [count_text_length(item['data']['text']) for item in data]
    total_documents = len(text_lengths)
    average_length = float(np.mean(text_lengths))
    min_length = int(np.min(text_lengths))
    first_quartile = float(np.percentile(text_lengths, 25))
    median_length = float(np.median(text_lengths))
    third_quartile = float(np.percentile(text_lengths, 75))
    max_length = int(np.max(text_lengths))

    output_data = {
        'total_documents': total_documents,
        'average_length': average_length,
        'min_length': min_length,
        'first_quartile': first_quartile,
        'median_length': median_length,
        'third_quartile': third_quartile,
        'max_length': max_length,
        'text_lengths': text_lengths
    }
    os.makedirs(os.path.dirname(output_json), exist_ok=True)
    with open(output_json, 'w', encoding='utf-8') as file:
        json.dump(output_data, file, ensure_ascii=False, indent=4)

    plt.figure(figsize=(12, 8))
    plt.hist(text_lengths, bins=20, edgecolor='black', color='skyblue')
    plt.title('Document Length Distribution', fontsize=16)
    plt.xlabel('Length', fontsize=14)
    plt.ylabel('Frequency', fontsize=14)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    os.makedirs(os.path.dirname(output_image), exist_ok=True)
    plt.savefig(output_image)
    plt.close()

def extract_label_counts(input_file, output_file):
    # 提取标签计数
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    entity_counts = {}
    relation_counts = {}

    for item in data:
        if 'result' not in item:
            continue
        for result in item['result']:
            if 'value' in result and 'labels' in result['value']:
                for label in result['value']['labels']:
                    if label in entity_counts:
                        entity_counts[label] += 1
                    else:
                        entity_counts[label] = 1

            if 'type' in result and result['type'] == 'relation' and 'labels' in result:
                for label in result['labels']:
                    if label in relation_counts:
                        relation_counts[label] += 1
                    else:
                        relation_counts[label] = 1

    output_data = {
        'entity_counts': entity_counts,
        'relation_counts': relation_counts
    }

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(output_data, file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    datasets = ['istic', 'las', 'njust', 'whu']
    data_types = ['train', 'test']

    os.makedirs('./stat', exist_ok=True)

    for dataset in datasets:
        for data_type in data_types:
            input_file = f'./data/raw/{data_type}/{dataset}_{data_type}.json'
            output_dir = f'./stat/{dataset}'
            os.makedirs(output_dir, exist_ok=True)

            output_json = f'{output_dir}/{dataset}_{data_type}_length_stats.json'
            output_image = f'{output_dir}/{dataset}_{data_type}_length_distribution.png'
            analyze_text_lengths(input_file, output_json, output_image)

            if data_type == 'train':
                output_label_counts = f'{output_dir}/{dataset}_{data_type}_label_counts.json'
                extract_label_counts(input_file, output_label_counts)