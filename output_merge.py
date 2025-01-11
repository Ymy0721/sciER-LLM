import os
import json

folder_path = './submit/result'
output_file = './submit/灵犀解语.json'

merged_data = []

# 遍历文件夹中的所有 JSON 文件并合并数据
for filename in os.listdir(folder_path):
    if filename.endswith('.json'):
        file_path = os.path.join(folder_path, filename)
        with open(file_path, 'r', encoding='utf-8') as infile:
            data = json.load(infile)
            if isinstance(data, list):
                merged_data.extend(data)
            else:
                merged_data.append(data)

# 将合并后的数据保存到新文件
with open(output_file, 'w', encoding='utf-8') as outfile:
    json.dump(merged_data, outfile, ensure_ascii=False, indent=4)