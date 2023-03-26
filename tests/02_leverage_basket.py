from build.lib.binance_f.base.printobject import PrintMix
from test_client import request_client

result = request_client.get_leverage_bracket(symbol="BTCUSDT")
PrintMix.print_data(result)