# 示例使用

import sys
import os




import dexprice.modules.db.readjson as readjson
import dexprice.modules.utilis.findroot as findroot

if __name__ == "__main__":
    # 读取 JSON 文件



    ## 我们将json的token读取到json
    current_dir = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = findroot.find_project_root(current_dir)
    DATA_FOLDER = os.path.join(PROJECT_ROOT, "Data")
    filepath  = DATA_FOLDER+'/result.json'


    chaind = 'solana'
    results =  readjson.gettokenCAaddress(filepath,chaind)
    #results =  readjson.gettokenca(file)
    print(results)

   # print(len(results))
    # 假设 results 是你的初始数据
    filtered_results = [result for result in results if result['chain'].lower() == 'solana']

    # 输出过滤后的结果
    # for result in filtered_results:
    #     print(f"Chain: {result['chain']}, CA: {result['ca']}")
    CA_addresses = [result['ca'] for result in filtered_results]


    print(CA_addresses)
