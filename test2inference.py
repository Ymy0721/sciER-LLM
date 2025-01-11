import json
import os

def load_prompts(file_path):
    # 读取提示词 JSON 文件
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

prompts = load_prompts('./dataset_prompts.json')

def convert_data(data, instruction):
    # 转换数据格式
    output = {
        "instruction": instruction,
        "input": data["data"]["text"],
        "output": ""
    }
    return output

for dataset, instruction in prompts.items():
    input_file = f'./data/processed/test/{dataset}_test.json'
    output_file = f'./data/inference/input/{dataset}_test_inf.jsonl'

    # 创建输出文件夹
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # 读取原始 JSON 文件
    with open(input_file, 'r', encoding='utf-8') as f:
        original_data = json.load(f)

    # 转换每个数据并保存到新文件
    with open(output_file, 'w', encoding='utf-8') as f:
        for idx, data_item in enumerate(original_data):
            converted_data = convert_data(data_item, instruction)
            json.dump({
                "id": str(data_item["id"]),
                "input": converted_data["instruction"] + "\n" + converted_data["input"],
                "target": converted_data["output"]
            }, f, ensure_ascii=False)
            f.write("\n")