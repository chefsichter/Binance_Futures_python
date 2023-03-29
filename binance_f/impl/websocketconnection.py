import threading
import time

import websocket
import ssl
import logging

from binance_f.impl.time_out_lock import TimeoutLock
from binance_f.impl.utils.timeservice import get_current_timestamp
from binance_f.exception.binanceapiexception import BinanceApiException
from binance_f.impl.utils import *
from binance_f.model.constant import *

connection_id = 0


class ConnectionState:
    IDLE = 0
    CONNECTING = 1
    CONNECTED = 2
    CLOSED_ON_ERROR = 3
    IN_DELAY = 4


class WebsocketConnection:

    def __init__(self, api_key, secret_key, uri, watch_dog, request):
        self.__thread = None
        self.url = uri
        self.__api_key = api_key
        self.__secret_key = secret_key
        self.request = request
        self.__watch_dog = watch_dog
        self.delay_in_second = watch_dog.connection_delay_failure
        self.ws = None
        self.receive_limit_ms = self.__watch_dog.receive_limit_ms
        self.last_receive_time = 0
        self.logger = logging.getLogger("binance-futures")
        self.state = ConnectionState.IDLE
        global connection_id
        connection_id += 1
        self.id = connection_id
        self.name = self.get_name()
        self.lock = TimeoutLock(logger=self.logger, modul=self.name, debug=True)

    def get_name(self):
        cut_off = 20
        try:
            params = self.request.channel['params'][0]
            if len(params) > cut_off:
                params = params[:cut_off] + "..."
        except (KeyError, TypeError):
            params = "params not set"
        return f"[Sub][{self.id}]{params}"

    def set_receive_limit_ms(self, receive_limit_ms):
        self.receive_limit_ms = receive_limit_ms

    def send(self, data):
        self.ws.send(data)

    def on_open(self, ws):
        with self.lock.cm_acquire():
            self.logger.info(self.name + ": on_open: Connected to server")
            self.ws = ws
            self.last_receive_time = get_current_timestamp()
            self.state = ConnectionState.CONNECTED
            self.__watch_dog.on_connection_created(self)
            if self.request.subscription_handler is not None:
                self.request.subscription_handler(self)
            return

    def __on_receive_response(self, json_wrapper):
        res = None
        try:
            res = json_wrapper.get_int("id")
        except Exception as e:
            self._error_msg(f"{SubscribeMessageType.RESPONSE.upper()}->Failed to parse server's response: " +
                            str(e), error_binance=json_wrapper.json_object)

        try:
            if self.request.update_callback is not None:
                self.request.update_callback(SubscribeMessageType.RESPONSE, res)
        except Exception as e:
            self._error_msg(f"{SubscribeMessageType.RESPONSE.upper()}->Process error: " + str(e)
                            + " You should capture the exception in your error handler",
                            error_binance=json_wrapper.json_object)

    def __on_receive_payload(self, json_wrapper):
        res = None
        try:
            if self.request.json_parser is not None:
                res = self.request.json_parser(json_wrapper)
        except Exception as e:
            self._error_msg(f"{SubscribeMessageType.PAYLOAD.upper()}->Failed to parse server's response: "
                            + str(e), error_binance=json_wrapper.json_object)

        try:
            if self.request.update_callback is not None:
                self.request.update_callback(SubscribeMessageType.PAYLOAD, res)
        except Exception as e:
            self._error_msg(f"{SubscribeMessageType.PAYLOAD.upper()}->Process error: " + str(e) +
                            " You should capture the exception in your error handler",
                            error_binance=json_wrapper.json_object)

        if self.request.auto_close:
            self.close()

    def on_message(self, ws, message):
        with self.lock.cm_acquire(debug=False):
            self.last_receive_time = get_current_timestamp()
            json_wrapper = parse_json_from_string(message)

            if json_wrapper.contain_key("status") and json_wrapper.get_string("status") != "ok":
                error_code = json_wrapper.get_string_or_default("code", "Unknown error")
                error_msg = json_wrapper.get_string_or_default("msg", "Unknown error")
                self._error_msg(error_code + ": " + error_msg, error_binance=json_wrapper.json_object)
            elif json_wrapper.contain_key("code") and json_wrapper.get_int("code") != 0:
                error_code = json_wrapper.get_string_or_default("code", "Unknown error")
                error_msg = json_wrapper.get_string_or_default("msg", "Unknown error")
                self._error_msg(error_code + ": " + error_msg, error_binance=json_wrapper.json_object)
            elif json_wrapper.contain_key("result") and json_wrapper.contain_key("id"):
                self.logger.info(self.name + ": on_message: " + message)
                self.__on_receive_response(json_wrapper)
            else:
                self.__on_receive_payload(json_wrapper)

    def _error_msg(self, error_message, error_binance=None):
        error_message = self.name + ": " + str(error_message)
        if self.request.error_handler is not None:
            exception = BinanceApiException(BinanceApiException.SUBSCRIPTION_ERROR,
                                            error_message,
                                            error_binance=error_binance)
            self.request.error_handler(exception)
        self.logger.error(error_message)
        if error_binance:
            self.logger.warning(f"Binance: {error_binance}")

    def on_error(self, ws, error):
        with self.lock.cm_acquire():
            self.state = ConnectionState.CLOSED_ON_ERROR
            try:
                error_binance = parse_json_from_string(error).json_object
            except json.decoder.JSONDecodeError:
                error_binance = error
            self._error_msg("on_error: " + str(error), error_binance=error_binance)
            if self.ws is not None:
                self.logger.error(self.name + ": Connection is closing due to error")
                self.ws.close()

    def set_to_reconnect_in_delay(self, delay_in_second):
        self._close_websocket()
        self.state = ConnectionState.IN_DELAY
        self.delay_in_second = delay_in_second
        self.logger.warning(self.name + ": Reconnecting after " + str(self.delay_in_second) + " seconds later")

    def _start_new_websocket(self):
        self.ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
        self.logger.info(self.name + ": Websocket loop down")

    def connect(self):
        if self.state == ConnectionState.CONNECTING:
            self.logger.info(self.name + ": Already connecting...")
        elif self.state == ConnectionState.CONNECTED:
            self.logger.info(self.name + ": Already connected")
        else:
            self.state = ConnectionState.CONNECTING
            self.logger.info(self.name + ": Connecting...")
            self.last_receive_time = get_current_timestamp()
            self.ws = websocket.WebSocketApp(self.url,
                                             on_message=self.on_message,
                                             on_error=self.on_error,
                                             on_close=self.on_close)
            self.ws.on_open = self.on_open
            self.__thread = threading.Thread(target=self._start_new_websocket)  # self.ws
            self.__thread.start()

    def re_connect_in_delay(self):
        if self.delay_in_second != 0:
            self.delay_in_second -= 1
            self.logger.warning(self.name + ": In delay connection: " + str(self.delay_in_second))
        else:
            self.connect()

    def on_close(self, ws, close_status_code, close_msg):
        with self.lock.cm_acquire():
            self.logger.info(self.name + f": on_close: close_status_code: '{close_status_code}', "
                                         f"close_msg: '{close_msg}'")

    def _close_websocket(self):
        if self.ws is not None:
            self.ws.close()
            self.ws = None

    def close(self):
        with self.lock.cm_acquire():
            self.logger.info(self.name + ": Closing normally")
            self._close_websocket()
            self.__watch_dog.on_connection_closed(self)

    def __process_ping_on_trading_line(self, ping_ts):
        self.send("{\"op\":\"pong\",\"ts\":" + str(ping_ts) + "}")
        return

    def __process_ping_on_market_line(self, ping_ts):
        self.send("{\"pong\":" + str(ping_ts) + "}")
        return
