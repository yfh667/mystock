

# retrice from the dexscreen
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

class TokenInfo:
    def __init__(self, chainid:str,address: str,name: str, price_usd: float, liquidity_usd: float, fdv: float, timestamp: str,creattime: str ,pair_address: str, txn_buy: Optional[str] = None,
                 txn_sell: Optional[str] = None, volume: Optional[float] = None):
        self.address = address
        self.name = name
        self.price_usd = price_usd
        self.liquidity_usd = liquidity_usd
        self.fdv = fdv
        self.timestamp = timestamp
        self.creattime = creattime
        self.pair_address = pair_address
        self.chainid = chainid
        self.txn_buy = txn_buy
        self.txn_sell = txn_sell
        self.volume = volume


    def __repr__(self):
        return f"TokenInfo(chainid = {self.chainid}, address={self.address}, name={self.name}, price_usd={self.price_usd}, liquidity_usd={self.liquidity_usd}, fdv={self.fdv}, timestamp={self.timestamp}, pair_address={self.pair_address}, creattime={self.creattime})"
# modules/utilis/constants.py


class CexTokenInfo:
    def __init__(self,  name:  str ,chainid: str,creattime :str ):
        self.chainid = chainid
        self.name = name
        self.creattime = creattime

    def __repr__(self):
        return f"CexTokenInfo(chanid={self.chainid}, name={self.name} ,creattime={self.creattime}) )"
    def __eq__(self, other):
        if isinstance(other, CexTokenInfo):
            return self.chainid == other.chainid and self.name.strip() == other.name.strip() and self.creattime.strip() == other.creattime.strip()
        return False
# modules/utilis/constants.py
## historical --
class TokenPriceHistory:
    def __init__(self, tokenid: float, open: float, high: float, low: float, close: str,time: str ,volume: float):
        self.tokenid = tokenid

        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.time = time
        self.volume = volume

    def __repr__(self):
        return f"TokenPriceHistory(tokenid={self.tokenid},  open={self.open}, high={self.high}, low={self.low}, close={self.close}, time={self.time}, volume={self.volume})"
# modules/utilis/constants.py

## historical --
class CexTokenPriceHistory:
    def __init__(self, tokenid: float, open: float, high: float, low: float, close: str,time: str ,volume: float,amount:float):
        self.tokenid = tokenid

        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.time = time
        self.volume = volume
        self.amount = amount


    def __repr__(self):
        return f"CexTokenPriceHistory(tokenid={self.tokenid},  open={self.open}, high={self.high}, low={self.low}, close={self.close}, time={self.time}, volume={self.volume},amount={self.amount})"
# modules/utilis/constants.py

class OvhlFromDex:
    def __init__(self,  pairaddress: str, open: float, high: float, low: float, close: str,time: str ,volume: float):
        self.pairaddress = pairaddress

        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.time = time
        self.volume = volume

    def __repr__(self):
        return f"OvhlFromDex(pairaddress={self.pairaddress},  open={self.open}, high={self.high}, low={self.low}, close={self.close}, time={self.time}, volume={self.volume})"
# modules/utilis/constants.py

## raw tiem sequence data

class OvhlFromCex:
    def __init__(self,   name : str, open: float, high: float, low: float, close: str,time: str ,volume: float,amount:float):
        self.name = name
#voulume : token amount: usdt
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.time = time
        self.volume = volume
        self.amount = amount

    def __repr__(self):
        return f"OvhlFromCex(name={self.name},  open={self.open}, high={self.high}, low={self.low}, close={self.close}, time={self.time}, volume={self.volume},amount={self.amount})"
# modules/utilis/constants.py

class OvhlRawPrice:
    def __init__(self, tokenid: float, price: float, time: str):
        self.tokenid = tokenid
        self.price = price
        self.time = time

    def __repr__(self):
        return f"OvhlRawPrice(tokenid={self.tokenid}, price={self.price}, time={self.time})"


## read from the table
class Tokendb:
    def __init__(self, tokenid: float, chainid: str,name: str,address:str,pair_address: str,creattime: str ):
        self.tokenid = tokenid
        self.chainid = chainid
        self.pair_address = pair_address
        self.creattime = creattime
        self.address = address

        self.name = name



    def __repr__(self):
            return f"Tokendb(tokenid={self.tokenid}, chainid={self.chainid},  name={self.name}, address={self.address},pair_address={self.pair_address}, creattime={self.creattime})"
# modules/utilis/constants.py



class Config:
    DEXS = 0
    GECK = 1
    DEXCA =2
    # 可以在这里添加更多的常量或配置项

    def __init__(self):
        pass

@dataclass
class FilterCriteria:
    liquidity_usd_min: Optional[float] = None
    liquidity_usd_max: Optional[float] = None
    fdv_min: Optional[float] = None
    fdv_max: Optional[float] = None
    pair_age_min_hours: Optional[float] = None
    pair_age_max_hours: Optional[float] = None
    txn_buy: Optional[float] = None
    txn_sell: Optional[float] = None
    volume: Optional[float] = None


