import dexprice.modules.tg.tgbot as tgbot
import dexprice.modules.tg.mexctg as mexctg
import dexprice.modules.utilis.define as define

if __name__ == '__main__':
 #   tgbot.sendmessage("6rvir3c4H9cvMxtz38aG9TJPgH1sDUiGpUnupiHituVs",7890)
    chatid = "@jingou11"
    tokeninfo1 = define.CexTokenInfo(
        name = "BTC",
        chainid='USDT',
        creattime='11',
        )
    tokeninfo2 = define.CexTokenInfo(
        name="ETH",
        chainid='USDT',
        creattime='11',
    )
    tokeninfos = [tokeninfo1, tokeninfo2]
    mexctg.mexctg2(chatid, tokeninfos)
  #  tgbot.sendmessage_chatid("@jingou24","refresh token",7890)