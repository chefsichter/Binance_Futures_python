import time
from binance_f.impl.websocketrequest import WebsocketRequest
from binance_f.impl.utils.channels import *
from binance_f.impl.utils.channelparser import ChannelParser
from binance_f.impl.utils.timeservice import *
from binance_f.impl.utils.inputchecker import *
from binance_f.model import *
# For develop
from binance_f.base.printobject import *


class WebsocketRequestImpl(object):

    def __init__(self, api_key):
        self.__api_key = api_key

    @staticmethod
    def create_request_object(channel,
                              event_object,
                              callback,
                              error_handler,
                              parser=None):
        request = WebsocketRequest()
        request.channel = channel

        def subscription_handler(connection):
            connection.send(json.dumps(channel))
            time.sleep(0.01)

        request.subscription_handler = subscription_handler

        def json_parse(json_wrapper):
            result = event_object.json_parse(json_wrapper)
            return result

        if parser:
            request.json_parser = parser
        else:
            request.json_parser = json_parse

        request.update_callback = callback
        request.error_handler = error_handler
        return request

    def subscribe_aggregate_trade_event(self, symbol, callback, error_handler=None):
        check_should_not_none(symbol, "symbol")
        check_should_not_none(callback, "callback")

        return self.create_request_object(aggregate_trade_channel(symbol), AggregateTradeEvent, callback, error_handler)

    def subscribe_mark_price_event(self, symbol, callback, error_handler=None):
        check_should_not_none(symbol, "symbol")
        check_should_not_none(callback, "callback")

        return self.create_request_object(mark_price_channel(symbol), MarkPriceEvent, callback, error_handler)

    def subscribe_continuous_candlestick_event(self, pair, contract_type, interval, callback, error_handler=None):
        check_should_not_none(pair, "pair")
        check_should_not_none(contract_type, "contract_type")
        check_should_not_none(interval, "interval")
        check_should_not_none(callback, "callback")

        return self.create_request_object(continuous_kline_channel(pair, contract_type, interval),
                                          ContinuousCandlestickEvent, callback, error_handler)

    def subscribe_candlestick_event(self, symbol, interval, callback, error_handler=None):
        check_should_not_none(symbol, "symbol")
        check_should_not_none(interval, "interval")
        check_should_not_none(callback, "callback")

        return self.create_request_object(kline_channel(symbol, interval), CandlestickEvent, callback, error_handler)

    def subscribe_symbol_miniticker_event(self, symbol, callback, error_handler=None):
        check_should_not_none(symbol, "symbol")
        check_should_not_none(callback, "callback")

        return self.create_request_object(symbol_miniticker_channel(symbol), SymbolMiniTickerEvent,
                                          callback, error_handler)

    def subscribe_all_miniticker_event(self, callback, error_handler=None):
        check_should_not_none(callback, "callback")

        def json_parse(json_wrapper):
            result = list()
            data_list = json_wrapper.convert_2_array()
            for item in data_list.get_items():
                element = SymbolMiniTickerEvent.json_parse(item)
            result.append(element)
            return result

        return self.create_request_object(all_miniticker_channel(), SymbolMiniTickerEvent, callback,
                                          error_handler, parser=json_parse)

    def subscribe_symbol_ticker_event(self, symbol, callback, error_handler=None):
        check_should_not_none(symbol, "symbol")
        check_should_not_none(callback, "callback")

        return self.create_request_object(symbol_ticker_channel(symbol), SymbolTickerEvent, callback, error_handler)

    def subscribe_all_ticker_event(self, callback, error_handler=None):
        check_should_not_none(callback, "callback")

        def json_parse(json_wrapper):
            result = list()
            data_list = json_wrapper.convert_2_array()
            for item in data_list.get_items():
                ticker_event_obj = SymbolTickerEvent.json_parse(item)
            result.append(ticker_event_obj)
            return result

        return self.create_request_object(all_ticker_channel(), SymbolTickerEvent, callback,
                                          error_handler, parser=json_parse)

    def subscribe_symbol_bookticker_event(self, symbol, callback, error_handler=None):
        check_should_not_none(symbol, "symbol")
        check_should_not_none(callback, "callback")

        return self.create_request_object(symbol_bookticker_channel(symbol), SymbolBookTickerEvent, callback, error_handler)

    def subscribe_all_bookticker_event(self, callback, error_handler=None):
        check_should_not_none(callback, "callback")

        return self.create_request_object(all_bookticker_channel(), SymbolBookTickerEvent, callback, error_handler)

    def subscribe_symbol_liquidation_event(self, symbol, callback, error_handler=None):
        check_should_not_none(symbol, "symbol")
        check_should_not_none(callback, "callback")

        return self.create_request_object(symbol_liquidation_channel(symbol), LiquidationOrderEvent,
                                          callback, error_handler)

    def subscribe_all_liquidation_event(self, callback, error_handler=None):
        check_should_not_none(callback, "callback")

        return self.create_request_object(all_liquidation_channel(), LiquidationOrderEvent, callback, error_handler)

    def subscribe_book_depth_event(self, symbol, limit, update_time, callback, error_handler=None):
        check_should_not_none(symbol, "symbol")
        check_should_not_none(limit, "limit")
        check_should_not_none(callback, "callback")

        return self.create_request_object(book_depth_channel(symbol, limit, update_time), OrderBookEvent,
                                          callback, error_handler)

    def subscribe_diff_depth_event(self, symbol, update_time, callback, error_handler=None):
        check_should_not_none(symbol, "symbol")
        check_should_not_none(callback, "callback")

        return self.create_request_object(diff_depth_channel(symbol, update_time), DiffDepthEvent,
                                          callback, error_handler)

    def subscribe_user_data_event(self, listenKey, callback, error_handler=None):
        check_should_not_none(listenKey, "listenKey")
        check_should_not_none(callback, "callback")

        def json_parse(json_wrapper):
            print("event type: ", json_wrapper.get_string("e"))
            print(json_wrapper)
            if json_wrapper.get_string("e") == "ACCOUNT_UPDATE":
                result = AccountUpdate.json_parse(json_wrapper)
            elif json_wrapper.get_string("e") == "ORDER_TRADE_UPDATE":
                result = OrderUpdate.json_parse(json_wrapper)
            elif json_wrapper.get_string("e") == "listenKeyExpired":
                result = ListenKeyExpired.json_parse(json_wrapper)
            return result

        return self.create_request_object(user_data_channel(listenKey), object, callback,
                                          error_handler, parser=json_parse)

    def subscribe_all_mark_price_event(self, callback, error_handler=None):
        check_should_not_none(callback, "callback")

        def json_parse(json_wrapper):
            result = list()
            data_list = json_wrapper.convert_2_array()
            for item in data_list.get_items():
                element = MarkPriceEvent.json_parse(item)
            result.append(element)
            return result

        return self.create_request_object(all_mark_price_channel(), object, callback,
                                          error_handler, parser=json_parse)

    def subscribe_blvt_info_event(self, symbol, callback, error_handler=None):
        check_should_not_none(symbol, "symbol")
        check_should_not_none(callback, "callback")

        return self.create_request_object(blvt_info_channel(symbol), BLVTInfoEvent, callback, error_handler)

    def subscribe_blvt_nav_candlestick_event(self, symbol, interval, callback, error_handler=None):
        check_should_not_none(symbol, "symbol")
        check_should_not_none(interval, "interval")
        check_should_not_none(callback, "callback")

        return self.create_request_object(blvt_nav_kline_channel(symbol, interval), BLVTNAVCandlestickEvent,
                                          callback, error_handler)

    def subscribe_composite_index_event(self, symbol, callback, error_handler=None):
        check_should_not_none(symbol, "symbol")
        check_should_not_none(callback, "callback")

        return self.create_request_object(composite_index_channel(symbol), CompositeIndexEvent, callback, error_handler)
