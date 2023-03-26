import json
import logging
import time
from unittest import TestCase

from tests.test_client import sub_client, callback, error_handler, request_client


class TestFBraWebSocket(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.modul = f"{cls.__class__.__name__}"
        cls.symbol = "btcusdt"
        log_binance_future = logging.getLogger("binance-futures")
        log_binance_future.setLevel(level=logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        log_binance_future.addHandler(handler)

    def test_check_ws_connection(self):
        sub_client.subscribe_aggregate_trade_event(self.symbol, callback, error_handler)
        ws_connection = sub_client.connections[0]
        time.sleep(5)
        ws_connection.on_error("fake binance error")
        json_msg = '{"id": "1"}'
        ws_connection.on_message(json_msg)
        json_msg = '{"msg": "hello msg"}'
        ws_connection.on_message(json_msg)
        json_msg = '{"status": "err"}'
        ws_connection.on_message(json_msg)
        json_msg = '{"err-code": "-5055", "err-msg": "fake msg"}'
        ws_connection.on_message(json_msg)
        time.sleep(60)
        ws_connection.close()
        time.sleep(15 * 60)

    def test_user_socket(self):
        key = request_client.start_user_data_stream()
        sub_client.subscribe_user_data_event(key, callback, error_handler)
        time.sleep(15 * 60)
