import json
import os

def load_prompts(file_path):
    # 读取提示词 JSON 文件
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

prompts = load_prompts('./dataset_prompts.json')

def convert_data(data, instruction):
    # 转换数据格式
    entities = {}
    relations = {}
    for item in data["result"]:
        if "value" in item:
            entity_text = item["value"]["text"]
            entity_label = item["value"]["labels"][0]
            entities[item["id"]] = {entity_text: entity_label}
        elif "from_id" in item and "to_id" in item:
            from_entity_id = item["from_id"]
            to_entity_id = item["to_id"]
            relation_label = item["labels"][0]
            if from_entity_id in entities and to_entity_id in entities:
                from_entity_text = list(entities[from_entity_id].keys())[0]
                to_entity_text = list(entities[to_entity_id].keys())[0]
                relations[(from_entity_text, to_entity_text)] = relation_label

    new_entities_dict = {entity_text: entity_label for entity_item in entities.values() for entity_text, entity_label in entity_item.items()}

    new_relations_dict = {}
    if relations:
        new_relations_dict = {f"<{e1},{e2}>": relations[(e1, e2)] for e1 in new_entities_dict for e2 in new_entities_dict if e1 != e2 and (e1, e2) in relations}

    output = {
        "instruction": instruction,
        "input": data["data"]["text"],
        "output": json.dumps({
            "Entities": new_entities_dict,
            "Relations": new_relations_dict
        }, ensure_ascii=False) if relations else json.dumps({
            "Entities": new_entities_dict
        }, ensure_ascii=False)
    }
    return output

for dataset, instruction in prompts.items():
    input_file = f'./data/processed/train/{dataset}_train.json'
    output_file = f'./data/alpaca/{dataset}_train_alpaca.json'

    # 创建输出文件夹
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # 读取原始 JSON 文件
    with open(input_file, 'r', encoding='utf-8') as f:
        original_data = json.load(f)

    # 转换每个数据并保存到新文件
    converted_data_list = [convert_data(data_item, instruction) for data_item in original_data]

    # 将转换后的数据保存到新的 JSON 文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(converted_data_list, f, indent=4, ensure_ascii=False)