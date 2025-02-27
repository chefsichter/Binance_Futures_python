import json
from binance_f.impl.utils.timeservice import get_current_timestamp
from binance_f.model import DepthStep


def aggregate_trade_channel(symbol):
    channel = dict()
    channel["params"] = list()
    channel["params"].append(symbol + "@aggTrade")
    channel["id"] = get_current_timestamp()
    channel["method"] = "SUBSCRIBE"
    return channel

def mark_price_channel(symbol):
    channel = dict()
    channel["params"] = list()
    channel["params"].append(symbol + "@markPrice")
    channel["id"] = get_current_timestamp()
    channel["method"] = "SUBSCRIBE"
    return channel

def continuous_kline_channel(pair, contract_type, interval):
    channel = dict()
    channel["params"] = list()
    channel["params"].append(pair + '_' + contract_type + "@continuousKline_" + interval)
    channel["id"] = get_current_timestamp()
    channel["method"] = "SUBSCRIBE"
    return channel

def kline_channel(symbol, interval):
    channel = dict()
    channel["params"] = list()
    channel["params"].append(symbol + "@kline_" + interval)
    channel["id"] = get_current_timestamp()
    channel["method"] = "SUBSCRIBE"
    return channel

def trade_channel(symbol):
    channel = dict()
    channel["params"] = list()
    channel["params"].append(symbol + "@trade")
    channel["id"] = get_current_timestamp()
    channel["method"] = "SUBSCRIBE"
    return channel

def symbol_miniticker_channel(symbol):
    channel = dict()
    channel["params"] = list()
    channel["params"].append(symbol + "@miniTicker")
    channel["id"] = get_current_timestamp()
    channel["method"] = "SUBSCRIBE"
    return channel

def all_miniticker_channel():
    channel = dict()
    channel["params"] = list()
    channel["params"].append("!miniTicker@arr")
    channel["id"] = get_current_timestamp()
    channel["method"] = "SUBSCRIBE"
    return channel

def symbol_ticker_channel(symbol):
    channel = dict()
    channel["params"] = list()
    channel["params"].append(symbol + "@ticker")
    channel["id"] = get_current_timestamp()
    channel["method"] = "SUBSCRIBE"
    return channel

def all_ticker_channel():
    channel = dict()
    channel["params"] = list()
    channel["params"].append("!ticker@arr")
    channel["id"] = get_current_timestamp()
    channel["method"] = "SUBSCRIBE"
    return channel

def symbol_bookticker_channel(symbol):
    channel = dict()
    channel["params"] = list()
    channel["params"].append(symbol + "@bookTicker")
    channel["id"] = get_current_timestamp()
    channel["method"] = "SUBSCRIBE"
    return channel

def all_bookticker_channel():
    channel = dict()
    channel["params"] = list()
    channel["params"].append("!bookTicker")
    channel["id"] = get_current_timestamp()
    channel["method"] = "SUBSCRIBE"
    return channel

def symbol_liquidation_channel(symbol):
    channel = dict()
    channel["params"] = list()
    channel["params"].append(symbol + "@forceOrder")
    channel["id"] = get_current_timestamp()
    channel["method"] = "SUBSCRIBE"
    return channel

def all_liquidation_channel():
    channel = dict()
    channel["params"] = list()
    channel["params"].append("!forceOrder@arr")
    channel["id"] = get_current_timestamp()
    channel["method"] = "SUBSCRIBE"
    return channel

def book_depth_channel(symbol, limit, update_time):
    channel = dict()
    channel["params"] = list()
    channel["params"].append(symbol + "@depth" + str(limit) + str(update_time))
    channel["id"] = get_current_timestamp()
    channel["method"] = "SUBSCRIBE"
    return channel

def diff_depth_channel(symbol, update_time):
    channel = dict()
    channel["params"] = list()
    channel["params"].append(symbol + "@depth" + update_time)
    channel["id"] = get_current_timestamp()
    channel["method"] = "SUBSCRIBE"
    return channel
    
def user_data_channel(listenKey):
    channel = dict()
    channel["params"] = list()
    channel["params"].append(listenKey)
    channel["id"] = get_current_timestamp()
    channel["method"] = "SUBSCRIBE"
    return channel

def all_mark_price_channel():
    channel = dict()
    channel["params"] = list()
    channel["params"].append("!markPrice@arr")
    channel["id"] = get_current_timestamp()
    channel["method"] = "SUBSCRIBE"
    return channel

def blvt_info_channel(symbol):
    channel = dict()
    channel["params"] = list()
    channel["params"].append(symbol + "@compositeIndex")
    channel["id"] = get_current_timestamp()
    channel["method"] = "SUBSCRIBE"
    return channel

def blvt_nav_kline_channel(symbol, interval):
    channel = dict()
    channel["params"] = list()
    channel["params"].append(symbol + "@kline_" + interval)
    channel["id"] = get_current_timestamp()
    channel["method"] = "SUBSCRIBE"
    return channel

def composite_index_channel(symbol):
    channel = dict()
    channel["params"] = list()
    channel["params"].append(symbol + "@compositeIndex")
    channel["id"] = get_current_timestamp()
    channel["method"] = "SUBSCRIBE"
    return channel
