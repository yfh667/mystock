import json
import  re
import os



def gettokenca(files):
    token = []
    lines = []
    with open(files, 'r') as file:
        for line in file:
            lines.append(lines)
            if (len(line) > 120):
                base_url_position = line.find("https://dexscreener.com/")
                if base_url_position != -1:
                    base_url_position = line.find("https://dexscreener.com/")
                    start_pos = line.find("/", base_url_position + len("https://dexscreener.com/"))
                    chiand = line[base_url_position + 24:start_pos]
                    question_mark_position = line.find('?')
                    address = line[start_pos + 1:question_mark_position]
                    token.append({
                        'chain': chiand,
                        'ca': address
                    })

    return token
def process_all_json_files2(directory):
    """遍历目录中的所有 JSON 文件，提取信息并汇总结果"""
    all_results = []
    # 列出目录中的所有文件
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            file_path = os.path.join(directory, filename)
                        # 提取所需的信息
            results = gettokenca(file_path)
            all_results.extend(results)
    return all_results

def gettokenCAaddress(files,chainid):
    token = []
    lines = []
    with open(files, 'r', encoding='utf-8') as file:
        for line in file:
            # 尝试解析当前行的 JSON 数据
            line = line.strip()  # 去除行首行尾的空白符
            if '"type": "code"' in line:
                  #  data = json.loads(line)
                    next_line = file.readline().strip()
                    # 使用正则表达式提取 "text" 字段的值
                    match = re.search(r'"text":\s*"([^"]+)"', next_line)

                    if match:
                        text_value = match.group(1)
                        token.append({
                            'chain': chainid,
                            'ca': text_value
                        })
                        #token.append(text_value)
                       # print("提取的 text 值:", text_value)
                    else:
                        pass
                        #print("未找到匹配的 text 值")
    return token

def gettokenCAaddress_linshi(files):
    token = []
    lines = []
    with open(files, 'r', encoding='utf-8') as file:
        for line in file:
            # 尝试解析当前行的 JSON 数据
            line = line.strip()  # 去除行首行尾的空白符
            if '"type": "code"' in line:
                #  data = json.loads(line)
                next_line = file.readline().strip()
                # 使用正则表达式提取 "text" 字段的值
                match = re.search(r'"text":\s*"([^"]+)"', next_line)

                if match:
                    text_value = match.group(1)
                    token.append( text_value  )

                    # token.append(text_value)
                # print("提取的 text 值:", text_value)
                else:
                    pass
                    # print("未找到匹配的 text 值")

    return token