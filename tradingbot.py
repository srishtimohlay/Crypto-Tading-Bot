import talib, numpy
import websocket, json, pprint
from binance.client import Client
from binance.enums import *
import config

socket="wss://stream.binance.com:9443/ws/ethusdt@kline_1m"   #binance API to connect to the binance servers and get the data in the form of streams.

rsi_period=14
rsi_overbought=70
rsi_oversold=30
trade_symbol='ETHUSD'
trade_quantity=0.06

in_line = False

client= Client(config.API_KEY, config.API_SECRET, tld='us')

def order(side, quantity,  symbol,  order_type=ORDER_TYPE_MARKET):
  try:
    print("Sending Order")
    order=client.create_order(symbol=symbol, side=side,type=ORDER_TYPE_MARKET, quantity=quantity)
    print(order)
    return True
  except Exception as e:
      return False
  return True


closeseries=[] #to track the series of closes
def on_open(ws): #opened connection
    print("Connection opened")

def on_close(ws):  #closed connection 
    print("Connection closed")

def on_message(ws, message):  #message received
   
    print("Message Received")
    python_message=json.loads(message)   #data parsing of json data strings to python format
    pprint.pprint(python_message)

    candle=python_message['k']
    iscandleclosed = candle['x']  
    close=candle['c']


    if (iscandleclosed): #if the value is true i.e. it is the very last end of the candlestick
        
        print("Candle closed at {}".format(close))

        closeseries.append(float(close))  #appending closes to the list
        print("closes")
        print(closeseries)

        if len(closeseries)> rsi_period: #no of closes should be greater than rsi_period to calculate RSI
            numpy_closes= numpy.array(closeseries)  #converting to numpy array of closes
            rsi=talib.RSI(numpy_closes, rsi_period) #calling RI funtion(part of talib) 
            print("All RSIs calculated so far") # RSI function calculates series of RSIs values. For ex. On the 15th close we'll get 1 RSI value and so on...
            print(rsi)
            last_rsi=rsi[-1] #getting the last rsi from the series of RSIs
            print("Current RSI is {}".format(last_rsi))

            if last_rsi>rsi_overbought:

                if in_line:
                    print("SELL IT!!")
                    order_succeeded=  order(SIDE_SELL, trade_quantity,  trade_symbol) #binance sell
                    if order_succeeded:
                        in_line= False
                else:
                    print("It's overbought but you don't own any")  
            
            if last_rsi<rsi_oversold:

                if in_line:
                    print("It's oversold, but you already bought it once")
                else:
                    print("BUY IT!!")
                    order_succeeded=  order(SIDE_BUY, trade_quantity,  trade_symbol) #binance buy
                    if order_succeeded:
                        in_line= True

            

ws=websocket.WebSocketApp(socket, on_open=on_open , on_close= on_close , on_message= on_message) #connecting websocket pytho client

ws.run_forever()




