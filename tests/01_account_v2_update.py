from test_client import request_client

symbol = 'BTCUSDT'
acc_v2 = request_client.get_position_v2()

print(acc_v2)
