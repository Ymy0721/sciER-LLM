import json
import re

def load_json(file_path):
    # 读取 JSON 文件
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def load_jsonl(file_path):
    # 读取 JSONL 文件
    with open(file_path, 'r', encoding='utf-8') as file:
        return [json.loads(line) for line in file]

def merge_chunks(split_data, output_data):
    # 创建一个字典用于快速查找 output_data 中的条目
    output_dict = {}
    for item in output_data:
        key = item['input'][-20:]
        if key not in output_dict:
            output_dict[key] = []
        output_dict[key].append(item)

    merged_data = []
    current_id_prefix = None
    merged_text = ""
    merged_target = {"Entities": {}}

    for item in split_data:
        text = item['data']['text']
        key = text[-20:]
        id_prefix = re.match(r'(.+)_chunk_\d+', item['id']).group(1)

        if id_prefix != current_id_prefix:
            if current_id_prefix is not None:
                merged_data.append({
                    "input": merged_text.strip(),
                    "target": json.dumps(merged_target) if merged_target["Entities"] else "{}"
                })
            current_id_prefix = id_prefix
            merged_text = text + " "
            merged_target = {"Entities": {}}
        else:
            merged_text += text + " "

        if key in output_dict:
            for output_item in output_dict[key]:
                if output_item['target'] and output_item['target'].startswith('{'):
                    try:
                        entities = json.loads(output_item['target'])
                        # 添加校验字段，防止审查机制返回错误结果
                        if "Entities" in entities:
                            merged_target["Entities"].update(entities["Entities"])
                    except json.JSONDecodeError as e:
                        print(f"Skipping entry due to JSON decode error: {e}")

    if current_id_prefix is not None:
        merged_data.append({
            "input": merged_text.strip(),
            "target": json.dumps(merged_target) if merged_target["Entities"] else "{}"
        })

    return merged_data

def main():
    split_data = load_json('./data/processed/test/njust_test.json')
    output_data = load_jsonl('./data/inference/output/njust_inf_output.jsonl')

    merged_data = merge_chunks(split_data, output_data)

    with open('./data/inference/output/njust_inf_output_merged.jsonl', 'w', encoding='utf-8') as f:
        for item in merged_data:
            f.write(json.dumps(item) + '\n')

if __name__ == "__main__":
    main()