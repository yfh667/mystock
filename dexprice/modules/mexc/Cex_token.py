import dexprice.modules.utilis.define as define

def Token(tokenname,flag):
    #flag = 1: contract
   # other  spot
   if (flag ==1):
       name = tokenname+'_USDT'
       token = define.CexTokenInfo(
           name=name,  # Token name (string)
           chainid="USDT",  # Chain ID (string)
           creattime=''

       )

       return token
   else:
       name = tokenname + 'USDT'
       token = define.CexTokenInfo(
           name=name,  # Token name (string)
           chainid="USDT",  # Chain ID (string)
           creattime=''

       )
       return token
# t= Token('STREAM',0)
# print(t)