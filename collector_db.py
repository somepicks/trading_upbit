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
    db_path = "D:/db_files/"
    db_ohlcv = db_path + 'upbit_ohlcv.db'
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
    duration_days = 20
    split = {'day': duration_days, 'minute240': duration_days * 6, 'minute60': duration_days * 24,
                 'minute30': duration_days * 48, 'minute15': duration_days * 96, 'minute10': duration_days * 144,
                 'minute5': duration_days * 288, 'minute3': duration_days * 480, 'minute1': duration_days * 1440}
    intervals = ['minute3']
    tickers = pyupbit.get_tickers(fiat="KRW") #전체 데이터 받을 경우
    # tickers = ['KRW-BTC'] #BTC 데이터만 받을 경우
    for i,ticker in enumerate(tickers):
        for interval in intervals:
            time.sleep(0.1)
            print(f'[{i+1}:{len(tickers)}] | {ticker} | {interval} | days= {duration_days}일 df생성 중...',end='')
            df = pyupbit.get_ohlcv(ticker=ticker,interval=interval,count=split[interval])
            df = df.drop([df.index[-1]]) #마지막 행은 현재 만들어지고 있는거기 때문에 제거
            df.index = df.index.strftime("%Y%m%d%H%M%S").astype(np.int64)
            # df.index.names = ['date']  # 인덱스명 'date'로 재 정의
            symbol = str(ticker[4:])
            table = f'{symbol}-{interval}'
            con = sqlite3.connect(db_ohlcv)
            if table in table_list:
                df_db = pd.read_sql(f"SELECT * FROM'{table}'", con).set_index('index')
                df = df[df.index > df_db.index[-1]]
            print('columns 추가 중...',end='')
            df=make_indicator.ALL(df)
            df.to_sql(table, con, if_exists='append')
            con.commit()
            print('완료')
    con.close()
