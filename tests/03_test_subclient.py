import logging
import time

from binance_f import SubscriptionClient
from binance_f.model import SubscribeMessageType
from build.lib.binance_f.base.printobject import PrintBasic
from test_client import sub_client, callback_agg, error_handler

log_binance_future = logging.getLogger("binance-futures")
log_binance_future.setLevel(level=logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
log_binance_future.addHandler(handler)


# sub_client.subscribe_mark_price_event(symbol="BTCUSDT", callback=callback, error_handler=error)
sub_client.subscribe_aggregate_trade_event(symbol="btcusdt", callback=callback_agg, error_handler=error_handler)
sub_client.subscribe_aggregate_trade_event(symbol="btcusdt", callback=callback_agg, error_handler=error_handler)
# fbra_web = FBraWebSocket(request_client)
# fbra_web.start_aggregate_trade_stream(symbol="BTCUSDT", callback=callback)
time.sleep(180)
