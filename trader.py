import websocket, json, pprint, numpy as np, talib as tb
from binance.client import Client
import binance.enums as b_enum
import config

SOCKET = "wss://stream.binance.com:9443/ws/ethusdt@kline_1m"
#RSI THreshsolds
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
TRADE_SYMBOL = 'ETHBUSD'
TRADE_QUANTITY = 0.005
global in_position
in_position = False;
closes = []

client = Client(config.API_KEY, config.API_SECRET, tld='en')

def on_open(ws):
    print("opened connection")

def on_close(ws):
    print("closed")

def on_message(ws, message):
    json_message = json.loads(message)
    #Prints json with candlestick data. Keeps printing until period is over. x=true in json object when final message is received for given candlestick
    pprint.pprint(json_message)

    candle = message['k']
    #check if closed candlestick and get close price
    closed = candle['x']
    close_p = candle['c']
    if closed:
        print("closed at {}".format(close_p))
        closes.append(float(close_p))

        if len(closes) < RSI_PERIOD:
            return

        closes_arr = np.array(closes)
        rsi = tb.get_rsi(closes_arr)
        print("All RSI calculated so far: {}".format(rsi))
        last_rsi = rsi[-1]
        print("Current rsi: {}".format(last_rsi))

        if last_rsi > RSI_OVERBOUGHT and in_position:
            print("Make Sell order")
            order_placed = make_order(TRADE_SYMBOL, TRADE_QUANTITY, b_enum.SIDE_SELL, b_enum.ORDER_TYPE_MARKET)
            in_position = False
        if last_rsi < RSI_OVERSOLD and in_position:
            print("Make buy order")
            order_placed = make_order(TRADE_SYMBOL, TRADE_QUANTITY, b_enum.SIDE_BUY, b_enum.ORDER_TYPE_MARKET)
            in_position = True
        
        

def make_order(symbol, quantity, side, order_type):
    try:
        print("Placing order")
        order = client.create_order(
            symbol=symbol,
            side=side,
            type=order_type,
            quantity=quantity
        )
        print(order)
    except Exception as e:
        e.print_exception
        return False

    return True
    

def main():
    ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
    ws.run_forever()

if __name__ == '__main__':
    main()

#https://www.youtube.com/watch?v=GdlFhF6gjKo
