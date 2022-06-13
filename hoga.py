# https://iamaman.tistory.com/2195
# https://gist.github.com/ssgkd/6e2de32431b2d7ea45a9d44a3909e49d#file-hogareturn-py
import pandas as pd
import pyupbit
import datetime
import sqlite3
def hogaUnitCalc(price,jang):
    hogaUnit = 1
    if price < 10:
        hogaUnit = 0.01
    elif price < 100:
        hogaUnit = 0.1
    elif price < 1000:
        hogaUnit = 1
    elif price < 10000:
        hogaUnit = 5
    elif price < 100000 and jang == "업비트":
        hogaUnit = 10
    elif price < 500000 and jang == "업비트":
        hogaUnit = 50
    elif price < 1000000 and jang == "업비트":
        hogaUnit = 100
    elif price < 2000000 and jang == "업비트":
        hogaUnit = 500
    elif price > 2000000 and jang == "업비트":
        hogaUnit = 1000
    elif price < 100000 and jang == "kospi":
        hogaUnit = 100
    elif price < 500000 and jang == "kospi":
        hogaUnit = 500
    elif price >= 500000 and jang == "kospi":
        hogaUnit = 1000
    elif price >= 50000 and jang == "kosdaq":
        hogaUnit = 100
    return hogaUnit

def hogaUnitCalc_per(hogaPrice, jang):
    minPrice = 1

    if hogaPrice < 10:
        minPrice = 10
    elif hogaPrice < 100:
        minPrice = 100
    elif hogaPrice < 1000:
        minPrice = 1000
    elif hogaPrice < 10000:
        minPrice = 10000
    elif hogaPrice < 100000:
        minPrice = 100000
    elif (hogaPrice < 500000):
        minPrice = 500000
    elif (hogaPrice < 1000000) & (jang == "업비트"):
        minPrice = 1000000
    elif (hogaPrice < 2000000) & (jang == "업비트"):
        minPrice = 2000000
    elif (hogaPrice > 2000000) & (jang == "업비트"):
        minPrice = 100000000
    elif (hogaPrice >= 500000) & (jang == "kospi"):
        minPrice = 500000
    elif (hogaPrice >= 50000) & (jang == "kosdaq"):
        minPrice = 50000

    return minPrice

def hogaPriceReturn(currentPrice, tic,jang): #틱으로 반환
    hogaPrice = currentPrice
    for _ in range(abs(tic)):
        if tic < 0:
            minusV = (hogaPrice - 1)
            hogaunit = hogaUnitCalc(minusV,jang)
            mot = minusV // hogaunit
            hogaPrice = mot * hogaunit
        elif tic > 0:
            hogaunit = hogaUnitCalc(hogaPrice,jang)
            hogaPrice = hogaPrice + hogaunit

    return hogaPrice


def hogaPriceReturn_per(currentPrice, per,jang): #퍼센트로 반환
    hogaPrice = currentPrice * ((per * 0.01) + 1)
    hogaUnit = hogaUnitCalc(hogaPrice,jang)
    minPrice = hogaUnitCalc_per(hogaPrice,jang)
    while True:
        minPrice = (minPrice - hogaUnit)
        if minPrice <= hogaPrice:
            return round(minPrice, 2)

if __name__ == '__main__':
    print(hogaPriceReturn_per(41772000,-2,'업비트'))
    df = pyupbit.get_ohlcv('KRW-XRP',interval='day',count=100)
    # df.loc[df['high']==df['open'],'ohga'] = hogaPriceReturn(1450,-1,'업비트')
    df.loc[df['high']==df['open'],'ohga'] = (df['close'].shift(1))*0.99
    print(df['close'][0])
    # con = sqlite3.connect('backtest.db')
    # cursor = con.cursor()
    # cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    # table = str(datetime.datetime.now())
    # table = table[0:16]
    # df.to_sql(table,con,if_exists='replace')
    # con.commit()
    # con.close()
    # print(type(hogaPriceReturn_per(15,-2,'업비트')))
    # hogaPriceReturn(기준가, 원하는 것과, 'kosdaq' or ‘kospi’)
    # ex) 코스닥, 현재가가 1만원인데 -2 호가의 가격, hogaPriceReturn(10000, -2, 'kosdaq')
