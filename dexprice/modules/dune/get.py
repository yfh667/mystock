import requests



url = f"https://api.dune.com/api/v1/query/{QUERY_ID}/results"

# 设置分页请求的参数
limit = 1000  # 每页获取的行数
offset = 5     # 起始偏移量，第一页从 0 开始
pages_to_fetch = 1  # 只获取第一页的数据，想要获取更多页可以增加此值

headers = {"X-Dune-Api-Key": API_KEY}

all_data = []  # 用来存储所有请求的结果

for page in range(pages_to_fetch):
    # 请求的参数
    params = {
        "limit": limit,
        "offset": offset
    }

    # 发送 GET 请求
    response = requests.get(url, headers=headers, params=params)

    # 检查请求是否成功
    response.raise_for_status()

    # 获取返回的 JSON 数据
    data = response.json()

    # 获取当前页的结果
    rows = data.get('result', {}).get('rows', [])
    all_data.extend(rows)

    print(f"已获取第 {page+1} 页，共 {len(rows)} 行")

    # 更新 offset，以便获取下一页的数据
    offset += limit

# 打印第一页的数据或总数据行数
print(f"总共获取 {len(all_data)} 行数据")
# 如果只需要查看第一页，可以打印 all_data[:1000]（第一页的前1000行）
print(all_data[:1000])
