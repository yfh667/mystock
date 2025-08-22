# 示例使用

import sys
import os




import dexprice.modules.db.readjson as readjson
import dexprice.modules.utilis.findroot as findroot

if __name__ == "__main__":
    # 读取 JSON 文件
    #file_path = '/home/yfh/Desktop/linshi/result.json'  # 将路径替换为你的 JSON 文件路径
    # file_path = '/home/yfh/Desktop/beifen/test/output_1.json'  # 将路径替换为你的 JSON 文件路径
    #
    # json_data = read_json_file(file_path)
    #
    # # 从 JSON 数据中提取所有链和合约地址
    # results = extract_chain_and_ca(json_data)
    # directory ='/home/yfh/Desktop/linshi'
    # results =  readjson.process_all_json_files2(directory)
    # print(results)



    ## 我们将json的token读取到json
    current_dir = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = findroot.find_project_root(current_dir)
    DATA_FOLDER = os.path.join(PROJECT_ROOT, "Data")
    filepath  = DATA_FOLDER+'/result.json'


    chaind = 'solana'
    results =  readjson.gettokenCAaddress(filepath,chaind)
    #results =  readjson.gettokenca(file)
    print(results)
   #  for result in results:
   #      print(f"Chain: {result['chain']}, CA: {result['ca']}")
   # # print(len(results))
    # # 假设 results 是你的初始数据
    # filtered_results = [result for result in results if result['chain'].lower() == 'solana']
    #
    # # 输出过滤后的结果
    # # for result in filtered_results:
    # #     print(f"Chain: {result['chain']}, CA: {result['ca']}")
    # CA_addresses = [result['ca'] for result in filtered_results]
    # print(CA_addresses)
