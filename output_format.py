import json

def load_jsonl(file_path):
    # 读取 JSONL 文件
    with open(file_path, 'r', encoding='utf-8') as file:
        return [json.loads(line) for line in file]

def load_json(file_path):
    # 读取 JSON 文件
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def find_entities_and_relations(output):
    # 提取实体和关系
    entities = output.get("Entities", {})
    relations = output.get("Relations", {})
    return entities, relations

def create_result_entry(text_id, entities, relations, text, dataset_name):
    # 创建结果条目
    result = []
    entity_map = {}
    for idx, (entity_text, label) in enumerate(entities.items()):
        start = text.find(entity_text)
        # 如果找不到实体，则跳过
        if start == -1:
            print(f"Entity '{entity_text}' not found in text with id: {text_id}")
            continue
        end = start + len(entity_text) - 1 if dataset_name == 'njust' else start + len(entity_text)  # 修改 end 为索引减一
        entity_id = f"{text_id}:E{idx}"
        entity_map[entity_text] = entity_id
        result.append({
            "value": {
                "start": start,
                "end": end,
                "text": entity_text,
                "labels": [label]
            },
            "id": entity_id
        })

    if relations:
        for relation, relation_label in relations.items():
            try:
                # 提取头实体和尾实体
                if ',' in relation:
                    from_entity, to_entity = relation[1:-1].split(',', 1)
                elif '/' in relation:
                    from_entity, to_entity = relation[1:-1].split('/', 1)
                else:
                    raise ValueError(f"Invalid relation format: {relation}")

                # 实体名称必须在实体id映射中
                if relation_label != "NaN" and from_entity in entity_map and to_entity in entity_map:
                    result.append({
                        "from_id": entity_map[from_entity],
                        "to_id": entity_map[to_entity],
                        "type": "relation",
                        "labels": [relation_label]
                    })
            except ValueError:
                print(f"Skipping invalid relation format: {relation}")

    return {
        "id": text_id,
        "result": result,
        "data": {
            "text": text
        }
    }

def process_dataset(dataset_name):
    # 处理数据集
    if dataset_name == 'njust':
        jsonl_file = f'./data/inference/output/{dataset_name}_inf_output_merged.jsonl'
    else:
        jsonl_file = f'./data/inference/output/{dataset_name}_inf_output.jsonl'
    json_file = f'./data/raw/test/{dataset_name}_test.json'
    output_file = f'./submit/result/{dataset_name}_result.json'

    jsonl_data = load_jsonl(jsonl_file)
    json_data = load_json(json_file)

    result_data = []
    for json_entry in json_data:
        json_text = json_entry['data']['text']
        json_id = json_entry['id']
        matched = False
        for jsonl_entry in jsonl_data:
            jsonl_text = jsonl_entry['input']
            if jsonl_text.strip()[-20:] == json_text.strip()[-20:]:
                try:
                    entities, relations = find_entities_and_relations(json.loads(jsonl_entry['target']))
                    result_entry = create_result_entry(json_id, entities, relations, json_text, dataset_name)
                    result_data.append(result_entry)
                    matched = True
                    break
                except json.JSONDecodeError as e:
                    print(f"Skipping entry due to JSON decode error: {e}")
        if not matched:
            print(f"Skipping entry with id: {json_id} due to no matching text")

    output = {
        "dataset": dataset_name,
        "result_data": result_data
    }

    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(output, file, ensure_ascii=False, indent=4)

def main():
    # 主函数，处理所有数据集
    datasets = ['istic', 'las', 'whu', 'njust']

    for dataset_name in datasets:
        process_dataset(dataset_name)

if __name__ == "__main__":
    main()