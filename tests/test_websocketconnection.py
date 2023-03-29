import json
import logging
import time
from unittest import TestCase
from unittest.mock import patch


from binance_f import SubscriptionClient
from binance_f.impl.utils.timeservice import get_current_timestamp
from tests.test_client import callback_agg, error_handler, request_client, test_api_key, test_secret_key, \
    NEW_TESTNET_WS_URL, callback_mark


class TestFBraWebSocket(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.modul = f"{cls.__class__.__name__}"
        cls.symbol = "btcusdt"
        cls.sub_client = SubscriptionClient(api_key=test_api_key, secret_key=test_secret_key,
                                            uri=NEW_TESTNET_WS_URL,
                                            check_conn_freq=1,
                                            connection_delay_failure=3)
        log_binance_future = logging.getLogger("binance-futures")
        log_binance_future.setLevel(level=logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        log_binance_future.addHandler(handler)

    def test_check_ws_connection(self):
        self.sub_client.subscribe_aggregate_trade_event(self.symbol, callback_agg, error_handler)
        ws_connection = self.sub_client.connections[0]
        time.sleep(3*60)

    def test_on_message(self):
        self.sub_client.subscribe_aggregate_trade_event(self.symbol, callback_agg, error_handler)
        ws_connection = self.sub_client.connections[0]
        time.sleep(5)
        # ws_connection.on_error(ws_connection, "fake binance error")
        # status error messages
        json_msg = '{"status":"fake status"}'
        ws_connection.on_message(ws_connection, json_msg)
        json_msg = '{"status":"fake status", "msg":"Invalid symbol."}'
        ws_connection.on_message(ws_connection, json_msg)
        json_msg = '{"status":"fake status", "msg":"Invalid symbol."}'
        ws_connection.on_message(ws_connection, json_msg)
        json_msg = '{"status":"fake status", "msg":"Invalid symbol.", "code":-1}'
        ws_connection.on_message(ws_connection, json_msg)

        # code error messages
        json_msg = '{"code":-1}'
        ws_connection.on_message(ws_connection, json_msg)
        json_msg = '{"code":-1121,"msg":"Invalid symbol."}'
        ws_connection.on_message(ws_connection, json_msg)
        json_msg = '{"code":-1003,"msg":"too_many_requests"}'
        ws_connection.on_message(ws_connection, json_msg)

        # result message
        json_msg = '{"id": "-1", "result": "fake result"}'
        ws_connection.on_message(ws_connection, json_msg)
        json_msg = '{"result": "fake result"}'
        ws_connection.on_message(ws_connection, json_msg)
        json_msg = '{"id": -1}'
        ws_connection.on_message(ws_connection, json_msg)

        # payload message
        json_msg = '{"e": -1}'
        ws_connection.on_message(ws_connection, json_msg)

        # random message
        json_msg = '{"msg": "hello msg"}'
        ws_connection.on_message(ws_connection, json_msg)

        time.sleep(60)
        ws_connection.close()

    def test_no_response_from_server(self):
        self.sub_client.subscribe_mark_price_event(self.symbol, callback_mark, error_handler)
        self.sub_client.subscribe_mark_price_event(self.symbol, callback_mark, error_handler)
        ws_connection = self.sub_client.connections[0]
        time.sleep(5)
        ws_connection.ws.close()
        ws_connection.last_receive_time = get_current_timestamp() - 120000
        time.sleep(1 * 60)

    def test_on_error(self):
        self.sub_client.subscribe_mark_price_event(self.symbol, callback_mark, error_handler)
        # self.sub_client.subscribe_mark_price_event(self.symbol, callback_mark, error_handler)
        ws_connection1 = self.sub_client.connections[0]
        # ws_connection2 = self.sub_client.connections[1]
        time.sleep(10)
        ws_connection1.on_error(ws_connection1.ws, json.loads('{"code":-1, '
                                                              '"msg":"true"}'))
        # ws_connection2.on_error("2 Ein Fehler ist aufgetreten.")
        time.sleep(2 * 60)

    def test_user_socket(self):
        key = request_client.start_user_data_stream()
        self.sub_client.subscribe_user_data_event(key, callback_agg, error_handler)
        time.sleep(3 * 60)
