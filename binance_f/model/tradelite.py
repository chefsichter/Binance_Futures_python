class TradeLite:
    def __init__(self):
        self.eventType = ""        # Event Type ("TRADE_LITE")
        self.eventTime = 0         # Event Time
        self.transactionTime = 0   # Transaction Time
        self.symbol = ""           # Symbol (e.g., "BTCUSDT")
        self.originalQuantity = 0.0  # Original Quantity
        self.originalPrice = 0.0   # Original Price
        self.isMakerSide = None    # Is this trade the maker side?
        self.clientOrderId = ""    # Client Order Id
        self.side = ""             # Side (e.g., "BUY" or "SELL")
        self.lastFilledPrice = 0.0 # Last Filled Price
        self.lastFilledQuantity = 0.0  # Order Last Filled Quantity
        self.tradeId = None        # Trade Id
        self.orderId = None        # Order Id
        self.orderStatus = "FILLED"  # Order Status

    @staticmethod
    def json_parse(json_data):
        result = TradeLite()
        result.eventType = json_data.get_string("e")
        result.eventTime = json_data.get_int("E")
        result.transactionTime = json_data.get_int("T")
        result.symbol = json_data.get_string("s")
        result.originalQuantity = json_data.get_float("q")
        result.originalPrice = json_data.get_float("p")
        result.isMakerSide = json_data.get_boolean("m")
        result.clientOrderId = json_data.get_string("c")
        result.side = json_data.get_string("S")
        result.lastFilledPrice = json_data.get_float("L")
        result.lastFilledQuantity = json_data.get_float("l")
        result.tradeId = json_data.get_int("t")
        result.orderId = json_data.get_int("i")
        return result
