import threading
import websocket
import ssl
import logging

from binance_f.impl.time_out_lock import TimeoutLock
from binance_f.impl.utils.timeservice import get_current_timestamp
from binance_f.exception.binanceapiexception import BinanceApiException
from binance_f.impl.utils import *
from binance_f.model.constant import *

# Key: ws, Value: connection
websocket_connection_handler = dict()


def on_message(ws, message):
    websocket_connection = websocket_connection_handler[ws]
    websocket_connection.on_message(message)
    return


def on_error(ws, error):
    websocket_connection = websocket_connection_handler[ws]
    websocket_connection.on_error(error)


def on_close(ws, *args):
    websocket_connection = websocket_connection_handler[ws]
    websocket_connection.on_close()


def on_open(ws):
    websocket_connection = websocket_connection_handler[ws]
    websocket_connection.on_open(ws)


connection_id = 0


class ConnectionState:
    IDLE = 0
    CONNECTED = 1
    CLOSED_ON_ERROR = 2


def websocket_func(*args):
    connection_instance = args[0]
    connection_instance.ws = websocket.WebSocketApp(connection_instance.url,
                                                    on_message=on_message,
                                                    on_error=on_error,
                                                    on_close=on_close)
    global websocket_connection_handler
    websocket_connection_handler[connection_instance.ws] = connection_instance
    connection_instance.logger.info(connection_instance.name + ": Connecting...")
    connection_instance.ws.on_open = on_open
    connection_instance.ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
    connection_instance.logger.info(connection_instance.name + ": ws.run_forever loop down")
    if connection_instance.state == ConnectionState.CONNECTED:
        connection_instance.state = ConnectionState.IDLE


class WebsocketConnection:

    def __init__(self, api_key, secret_key, uri, watch_dog, request):
        self.__thread = None
        self.url = uri
        self.__api_key = api_key
        self.__secret_key = secret_key
        self.request = request
        self.__watch_dog = watch_dog
        self.delay_in_second = -1
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
                params = params[:cut_off]+"..."
        except (KeyError, TypeError):
            params = "params not set"
        return f"[Sub][{self.id}]{params}"

    def set_receive_limit_ms(self, receive_limit_ms):
        self.receive_limit_ms = receive_limit_ms

    def is_in_delay(self):
        with self.lock.cm_acquire():
            return self.delay_in_second != -1

    def set_to_reconnect_in_delay(self, delay_in_second):
        with self.lock.cm_acquire():
            if self.ws is not None:
                self.ws.close()
                self.ws = None
            self.delay_in_second = delay_in_second
            self.logger.warning(self.name + ": Reconnecting after " + str(self.delay_in_second) + " seconds later")

    def re_connect_in_delay(self):
        with self.lock.cm_acquire():
            if self.delay_in_second != 0:
                self.delay_in_second -= 1
                self.logger.warning(self.name + ": In delay connection: " + str(self.delay_in_second))
            else:
                self.connect()

    def connect(self):
        if self.state == ConnectionState.CONNECTED:
            self.logger.info(self.name + ": Already connected")
        else:
            self.delay_in_second = -1
            self.__thread = threading.Thread(target=websocket_func, args=[self])
            self.__thread.start()

    def send(self, data):
        self.ws.send(data)

    def close(self):
        with self.lock.cm_acquire():
            self.logger.info(self.name + ": Closing normally")
            self.ws.close()
            del websocket_connection_handler[self.ws]
            self.__watch_dog.on_connection_closed(self)

    def on_close(self):
        self.logger.info(self.name + ": on_close: Received on_close from server")

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

    def error_msg(self, error_message):
        error_message = self.name + ": " + str(error_message)
        if self.request.error_handler is not None:
            exception = BinanceApiException(BinanceApiException.SUBSCRIPTION_ERROR, error_message)
            self.request.error_handler(exception)
        self.logger.error(error_message)

    def on_error(self, error):
        with self.lock.cm_acquire():
            self.error_msg("on_error: " + str(error))
            if self.ws is not None:
                self.logger.error(self.name + ": Connection is closing due to error")
                self.ws.close()
                self.state = ConnectionState.CLOSED_ON_ERROR

    def on_message(self, message):
        self.last_receive_time = get_current_timestamp()
        json_wrapper = parse_json_from_string(message)

        if json_wrapper.contain_key("status") and json_wrapper.get_string("status") != "ok":
            error_code = json_wrapper.get_string_or_default("err-code", "Unknown error")
            error_msg = json_wrapper.get_string_or_default("err-msg", "Unknown error")
            self.error_msg(error_code + ": " + error_msg)
        elif json_wrapper.contain_key("err-code") and json_wrapper.get_int("err-code") != 0:
            error_code = json_wrapper.get_string_or_default("err-code", "Unknown error")
            error_msg = json_wrapper.get_string_or_default("err-msg", "Unknown error")
            self.error_msg(error_code + ": " + error_msg)
        elif json_wrapper.contain_key("result") and json_wrapper.contain_key("id"):
            self.__on_receive_response(json_wrapper)
        else:
            self.__on_receive_payload(json_wrapper)

    def __on_receive_response(self, json_wrapper):
        res = None
        try:
            res = json_wrapper.get_int("id")
        except Exception as e:
            self.error_msg("Failed to parse server's response: " + str(e))

        try:
            if self.request.update_callback is not None:
                self.request.update_callback(SubscribeMessageType.RESPONSE, res)
        except Exception as e:
            self.error_msg("Process error: " + str(e)
                           + " You should capture the exception in your error handler")

    def __on_receive_payload(self, json_wrapper):
        res = None
        try:
            if self.request.json_parser is not None:
                res = self.request.json_parser(json_wrapper)
        except Exception as e:
            self.error_msg("Failed to parse server's response: " + str(e))

        try:
            if self.request.update_callback is not None:
                self.request.update_callback(SubscribeMessageType.PAYLOAD, res)
        except Exception as e:
            self.error_msg("Process error: " + str(e) +
                           " You should capture the exception in your error handler")

        if self.request.auto_close:
            self.close()

    def __process_ping_on_trading_line(self, ping_ts):
        self.send("{\"op\":\"pong\",\"ts\":" + str(ping_ts) + "}")
        return

    def __process_ping_on_market_line(self, ping_ts):
        self.send("{\"pong\":" + str(ping_ts) + "}")
        return
