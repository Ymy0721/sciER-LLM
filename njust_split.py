import json
import re

def load_json(file_path):
    # 读取 JSON 文件
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def split_text_into_sentences(text):
    # 使用负向前瞻和负向后顾来避免在特定缩写后分割，并确保只有在 .!? 后跟随空格时才分割
    # sentences = re.split(r'(?<!\bet al)(?<!\bet al )(?<!\bi\.e)(?<!\bi\.e )(?<!\be\.g)(?<!\be\.g )(?<!\betc)(?<!\betc )(?<!\bviz)(?<!\bviz )(?<=[.!?])\s+(?=[A-Z])', text)
    sentences = re.split(r'(?<=[.!?])\s+', text)

    return sentences

def split_text_and_entities(entry, sentence_count=10):
    # 分割文本和实体
    text = entry['data']['text']
    sentences = split_text_into_sentences(text)
    entities = entry['result']

    chunks = []
    current_chunk = []
    current_chunk_text = ""
    current_start_index = 0
    chunk_entities = []

    for i, sentence in enumerate(sentences):
        current_chunk.append(sentence)
        current_chunk_text += sentence + " "

        if (i + 1) % sentence_count == 0 or i == len(sentences) - 1:
            chunk_text = " ".join(current_chunk).strip()
            chunk_length = len(chunk_text)

            # 调整当前块的实体
            chunk_entities = [
                entity for entity in entities
                if current_start_index <= entity['value']['start'] < current_start_index + chunk_length
            ]

            for entity in chunk_entities:
                entity['value']['start'] -= current_start_index
                entity['value']['end'] -= current_start_index

            chunks.append({
                'id': f"{entry['id']}_chunk_{len(chunks) + 1}",
                'data': {'text': chunk_text},
                'result': chunk_entities
            })

            current_chunk = []
            current_chunk_text = ""
            current_start_index += chunk_length + 1  # +1 表示每个句子后添加的空格

    return chunks

def split_text_into_chunks(entry, sentence_count=10):
    # 分割文本为块
    text = entry['data']['text']
    sentences = split_text_into_sentences(text)

    chunks = []
    for i in range(0, len(sentences), sentence_count):
        chunk_sentences = sentences[i:i + sentence_count]
        chunk_text = ' '.join(chunk_sentences)
        chunks.append({
            "id": f"{entry['id']}_chunk_{len(chunks) + 1}",
            "data": {"text": chunk_text}
        })

    return chunks

def main():
    train_input_file = './data/raw/train/njust_train.json'
    train_output_file = './data/processed/train/njust_train.json'
    test_input_file = './data/raw/test/njust_test.json'
    test_output_file = './data/processed/test/njust_test.json'

    # 处理训练数据
    train_data = load_json(train_input_file)
    train_split_data = []

    for entry in train_data:
        train_split_data.extend(split_text_and_entities(entry))

    with open(train_output_file, 'w', encoding='utf-8') as file:
        json.dump(train_split_data, file, ensure_ascii=False, indent=4)

    # 处理测试数据
    test_data = load_json(test_input_file)
    test_split_data = []

    for entry in test_data:
        test_split_data.extend(split_text_into_chunks(entry))

    with open(test_output_file, 'w', encoding='utf-8') as file:
        json.dump(test_split_data, file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
