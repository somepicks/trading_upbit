import time
import pyupbit
import pandas as pd
import numpy as np
import sqlite3
import os
import make_indicator
pd.set_option('display.max_columns',None) #모든 열을 보고자 할 때
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width',1500)
pd.set_option("display.unicode.east_asian_width", True)
pd.set_option('mode.chained_assignment',  None) # SettingWithCopyWarning 경고를 끈다
from pprint import pprint


# df = pyupbit.get_orderbook(ticker=["KRW-BTC", "KRW-XRP"])
# print(df)
# print(type(df[0]))
# df = pd.DataFrame(df[0])
# print(df)
# cur.executemany("INSERT INTO upbit(open, high,low,close,volume, value) VALUES(?,?,?,?,?,?)", df)
# con.commit()
if __name__ == '__main__':
    db_path = "D:/db_files"
    db_ohlcv = db_path + '/upbit.db'
    con = sqlite3.connect(db_ohlcv)
    cur = con.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cur.fetchall()  # fetchall 한번에 모든 로우 데이터 읽기 (종목코드 읽기)
    table_list = []
    if not tables:
        print('최초 저장...')
    else:
        table_list = np.concatenate(tables).tolist()  # 모든테이블을 리스트로변환 https://codechacha.com/ko/python-flatten-list/
        # [table_list.remove(x) for x in table_list if x == '잔고조회']  # 테이블 리스트에서 잔고조회 삭제
    # quit()
    sales_days = 1
    split = {'day': sales_days, 'minute240': sales_days * 6, 'minute60': sales_days * 24,
                 'minute30': sales_days * 48, 'minute15': sales_days * 96, 'minute10': sales_days * 144,
                 'minute5': sales_days * 288, 'minute3': sales_days * 480, 'minute1': sales_days * 1440}
    intervals = ['minute3']
    tickers = pyupbit.get_tickers(fiat="KRW") #전체 데이터 받을 경우
    # tickers = ['KRW-BTC'] #BTC 데이터만 받을 경우
    for i,ticker in enumerate(tickers):
        for interval in intervals:
            time.sleep(0.1)
            print(f'df생성 중... [{i+1}:{len(tickers)}] | {ticker} | {interval} | days= {sales_days}일 ',end='...')
            df = pyupbit.get_ohlcv(ticker=ticker,interval=interval,count=split[interval])
            df = df.drop([df.index[-1]]) #마지막 행은 현재 만들어지고 있는거기 때문에 제거
            symbol = str(ticker[4:])
            table = f'{symbol}-{interval}'
            print(table)
            con = sqlite3.connect(db_ohlcv)
            if table in table_list:
                print('yes')
                quit()

            # df = make_indicator.sma(df)
            # df = make_indicator.CCI(df)
            # df = make_indicator.CMO(df)
            # df = make_indicator.RSI(df)
            # df = make_indicator.df_add(df)
            # df = make_indicator.BBAND(df)
            # df = make_indicator.ATR(df)
            # df = make_indicator.heikin_ashi(df)
            # df['고저평균대비등락율'] = ((df['close'] / ((df['high'] + df['low']) / 2) - 1) * 100).round(2)
            df.index = df.index.strftime("%Y%m%d%H%M%S").astype(np.int64)
            print(' | DB저장 중...',end='')
            df.to_sql(table, con, if_exists='replace')
            con.commit()
            print('완료')
