import requests
import json
import time
import time
import dexprice.modules.utilis.timedefine as timedefine
import dexprice.modules.mexc.mexc_queue as mexc_queue
import dexprice.modules.utilis.define as define


def biance_token_history_basic(ohlcv_data, symbol,flag="binance"):
    historydatas = []

    if flag == "mexc":
        ohlcv_data = ohlcv_data["data"]
        timelen = len(ohlcv_data.get('time'))

        if(timelen ==0):
            return []
        if(ohlcv_data):
            for i in range(timelen):
                timedata = ohlcv_data.get('time')[i]
                open = ohlcv_data.get('open')[i]
                high = ohlcv_data.get('high')[i]
                low = ohlcv_data.get('low')[i]
                close = ohlcv_data.get('close')[i]
                volume = ohlcv_data.get('vol')[i]
                amount = ohlcv_data.get('amount')[i]
                historydata =  define.OvhlFromCex(symbol,open,high,low,close,timedefine.timestamp_to_datetime(timedata),volume,amount)

                historydatas.append(historydata)
        return historydatas
    elif flag=='binance':
        if(not ohlcv_data):
            #here sometime the token is not in the cex,so it is ignored
            return []
        timelen =len(ohlcv_data)
        if (timelen == 0):
            return []
        for i in range(timelen):
            dataovhl = ohlcv_data[i]
            timedata = dataovhl[0] /1000
            open = dataovhl[1]
            high = dataovhl[2]
            low = dataovhl[3]
            close = dataovhl[4]
            volume =dataovhl[5]
            amount = dataovhl[7]
            historydata = define.OvhlFromCex(symbol, open, high, low, close, timedefine.timestamp_to_datetime(timedata),
                                             volume, amount)

            historydatas.append(historydata)
        return historydatas
