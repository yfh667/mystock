import dexprice.modules.utilis.define as define
import dexprice.modules.allmodules.geckpricehistory as geckpricehistory

import dexprice.modules.db.insert_db as insert_db

from dexprice.modules.utilis.define import FilterCriteria

import dexprice.modules.db.multidb as multidb

import time
import dexprice.modules.tg.tgbot as tgbot
# Define a function to try deleting the table with retry logic
import dexprice.modules.proxy.proxymultitheread as proxymultitheread

import os
import dexprice.modules.utilis.findroot as findroot
import dexprice.modules.allmodules.refreshmaindb as refreshmaindb
import dexprice.modules.cexdb.cexdb as cexdb

import dexprice.modules.mexc.getalltoken as getalltoken
import dexprice.modules.cexdb.cexdb as cexdb

import dexprice.modules.utilis.define as define
import os
import dexprice.modules.utilis.findroot as findroot


def pingwen(tokenhistorys: list[define.TokenPriceHistory]):
    #  print(tokenhistorys)
    open = tokenhistorys[0].open
    last = tokenhistorys[-1].close
    if(len(tokenhistorys)>5):
        if last > 0.8 * open:
            return True


def try_delete_table_with_retry(db, retries=3, delay=5):
    for attempt in range(retries):
        try:
            db.delete_table2()
            print("Table deleted successfully.")
            return True
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("Max retries reached. Could not delete table.")
                return False


if __name__ == "__main__":

    import dexprice.modules.allmodules.initialtoken as initialtoken

  #
  #   ## 我们将json的token读取到json
    current_dir = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = findroot.find_project_root(current_dir)
    DATA_FOLDER = os.path.join(PROJECT_ROOT, "Data")

    # filepath  = DATA_FOLDER+'/result.json'
    # initialtoken.initialtoken3(filepath)
    #
    #
    #
    # refreshmaindb.refreshmaindb()

    # 将我们要研究的token存入到today数据库内
    criteria_raw = FilterCriteria(
        liquidity_usd_min=10000,
        liquidity_usd_max=None,
        fdv_min=5000000,
        fdv_max=None,
        pair_age_min_hours=None,
        pair_age_max_hours=None,
        txn_buy=10,
        txn_sell=10,
        volume=10000
    )
    db_name = 'rawmeme'
    import dexprice.modules.allmodules.project as project
    from dexprice.modules.utilis.define import FilterCriteria

    project.setproject_cex(db_name, criteria_raw)
  #  refreshmaindb.refreshmaindb_cex(criteria_raw)

  #   # here we need get the tokenfrom mexc
    db_name = "cexmain" + '.db'  # 数据库文件名
    db_folder =DATA_FOLDER+'/cex'
    db = cexdb.CexSQLiteDatabase(db_folder, db_name)

    db.connect()

    symbol = getalltoken.getalltoken()
    tokens_cex = []
    for symbol in symbol:
        token_parts = symbol.split('_')
        name = token_parts[0]
        chaind = token_parts[1]
        token = define.CexTokenInfo(
            name=name,  # Token name (string)
            chainid=chaind,  # Chain ID (string)

        )
        tokens_cex.append(token)
    db.insert_Multidata(tokens_cex)
    db.close()

# here we need use the tokens_cex
    db_dex = insert_db.SQLiteDatabase(db_folder, 'rawmeme.db')

    db_dex.connect()
    tokendex = db_dex.readdbtoken()
    suoyin = {}  # 创建一个空字典
    for token in tokendex:
        suoyin[token.name] = token.tokenid  # 将name和id建立对应关系

    # 如果需要将所有的字典存入一个列表
    allname = []
    for token in tokendex:
        for cextoken in tokens_cex:
            if(token.name=='MLG'):
                print("here")
            if cextoken.name==token.name:
                allname.append(cextoken.name)
             #   print(cextoken.name)
    findid = []
    for name in allname:
        if name in suoyin:
            findid.append(suoyin[name])
    #print(findid)

    findtokens = []
    for id in findid:
        print(id)
        token = tokendex[id]
        findtokens.append(token)
    db_dex.close()

    db_mexc = insert_db.SQLiteDatabase(db_folder+'/memecex', 'mexc.db')
    db_mexc.connect()
    db_mexc.insert_multiple_tokeninfo2(findtokens)
    db_mexc.close()





