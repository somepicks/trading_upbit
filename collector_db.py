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
    duration_days = 60
    split = {'day': duration_days, 'minute240': duration_days * 6, 'minute60': duration_days * 24,
                 'minute30': duration_days * 48, 'minute15': duration_days * 96, 'minute10': duration_days * 144,
                 'minute5': duration_days * 288, 'minute3': duration_days * 480, 'minute1': duration_days * 1440}
    intervals = ['minute3']
    tickers = pyupbit.get_tickers(fiat="KRW") #전체 데이터 받을 경우
    # tickers = ['KRW-BTC'] #BTC 데이터만 받을 경우
    for i,ticker in enumerate(tickers):
        for interval in intervals:
            time.sleep(0.1)
            print(f'df생성 중... [{i+1}:{len(tickers)}] | {ticker} | {interval} | days= {duration_days}일 ',end='...')
            df = pyupbit.get_ohlcv(ticker=ticker,interval=interval,count=split[interval])
            df = df.drop([df.index[-1]]) #마지막 행은 현재 만들어지고 있는거기 때문에 제거
            df.index = df.index.strftime("%Y%m%d%H%M%S").astype(np.int64)
            symbol = str(ticker[4:])
            table = f'{symbol}-{interval}'
            con = sqlite3.connect(db_ohlcv)
            if table in table_list:
                df_db = pd.read_sql(f"SELECT * FROM'{table}'", con).set_index('index')
                df = df[df.index > df_db.index[-1]]
            # df = make_indicator.sma(df)
            # df = make_indicator.CCI(df)
            # df = make_indicator.CMO(df)
            # df = make_indicator.RSI(df)
            # df = make_indicator.df_add(df)
            # df = make_indicator.BBAND(df)
            # df = make_indicator.ATR(df)
            # df = make_indicator.heikin_ashi(df)
            # df['고저평균대비등락율'] = ((df['close'] / ((df['high'] + df['low']) / 2) - 1) * 100).round(2)
            print(' | DB저장 중...',end='')
            df.to_sql(table, con, if_exists='append')
            con.commit()
            print('완료')
color_r1 = (255,0,0)
color_r2 = (255,216,216)
color_r3 = (255,167,167)
color_r4 = (241,95,95)
color_r5 = (204,61,61)
color_r6 = (152,0,0)
color_r7 = (103,0,0)

color_o1 = (255,94,0)
color_o2 = (250,224,212)
color_o3 = (255,193,158)
color_o4 = (242,150,97)
color_o5 = (204,114,61)
color_o6 = (153,56,0)
color_o7 = (102,37,0)

color_m1 = (255,187,0)
color_m2 = (250,236,197)
color_m3 = (255,224,140)
color_m4 = (242,203,97)
color_m5 = (204,166,61)
color_m6 = (153,112,0)
color_m7 = (102,75,0)

color_y1 = (255,228,0)
color_y2 = (250,244,192)
color_y3 = (250,237,125)
color_y4 = (229,216,92)
color_y5 = (196,183,59)
color_y6 = (153,138,0)
color_y7 = (102,92,0)

color_yg1 = (171,242,0)
color_yg2 = (228,247,186)
color_yg3 = (206,242,121)
color_yg4 = (188,229,92)
color_yg5 = (159,201,60)
color_yg6 = (107,153,0)
color_yg7 = (71,102,0)

color_g1 = (29,219,22)
color_g2 = (206,251,201)
color_g3 = (183,240,177)
color_g4 = (134,229,127)
color_g5 = (71,200,62)
color_g6 = (47,157,39)
color_g7 = (34,116,28)

color_c1 = (0,216,255)
color_c2 = (212,244,250)
color_c3 = (178,235,244)
color_c4 = (92,209,229)
color_c5 = (61,183,204)
color_c6 = (0,130,153)
color_c7 = (0,87,102)

color_yb1 = (0,84,255)
color_yb2 = (217,229,255)
color_yb3 = (178,204,255)
color_yb4 = (103,153,255)
color_yb5 = (67,116,217)
color_yb6 = (0,51,153)
color_yb7 = (0,34,102)