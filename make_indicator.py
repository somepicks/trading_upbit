import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd
pd.set_option('display.max_columns',None) #모든 열을 보고자 할 때
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width',1500)
pd.set_option("display.unicode.east_asian_width", True)
pd.set_option('mode.chained_assignment',  None) # SettingWithCopyWarning 경고를 끈다
import numpy as np
import pyupbit # pyupbit모듈 불러오기
import talib
pd.set_option('mode.chained_assignment',  None) # SettingWithCopyWarning 경고를 끈다
import sqlite3
# system_path = 'C:/Users/vosan/PycharmProjects/pythonProject/digital_currency/trading_upbit/back_test/db/'

def renko1(df):
    # https://pypi.org/project/mplfinance/
    # https://github.com/matplotlib/mplfinance/issues/63
    def make_renko(df):
        retdata = {}
        #차트 나왔다가 꺼지게
        mpf.plot(df,figratio=(10,6),type='renko',mav=(3,6,9,12,20,40),volume=True,tight_layout=True,return_calculated_values=retdata, block=False, returnfig=True)
        # print(axlist)
        # plt.pause(1)
        plt.close()

        # 차트 그림으로 저장
        # mpf.plot(df,figratio=(10,6),type='renko',mav=(3,6,9),volume=True,tight_layout=True,return_calculated_values=retdata,
        #          block=False, returnfig=True,savefig=filename+'.jpg')
        df = pd.DataFrame(retdata)
        # print(df)
        # quit()
        renko_3=(list(retdata.get('mav3'))[-1])
        renko_6=(list(retdata.get('mav6'))[-1])
        renko_9=(list(retdata.get('mav9'))[-1])
        renko_12=(list(retdata.get('mav12'))[-1])
        renko_20=(list(retdata.get('mav20'))[-1])
        renko_40=(list(retdata.get('mav40'))[-1])
        renko_bricks=(list(retdata.get('renko_bricks'))[-1])

        return renko_3,renko_6,renko_9,renko_12,renko_20,renko_40,renko_bricks
    # print(df)
    loop = 100
    for i in range(len(df.index)-loop+1):
        f_index=i+loop
        df_renko=df.iloc[i:f_index]
        renko_3,renko_6,renko_9,renko_12,renko_20,renko_40,renko_bricks = make_renko(df_renko)
        end_index = df_renko.index[-1]
        df.loc[end_index,'renko1_3'] = renko_3
        df.loc[end_index,'renko1_6'] = renko_6
        df.loc[end_index,'renko1_9'] = renko_9
        df.loc[end_index,'renko1_12'] = renko_12
        df.loc[end_index,'renko1_20'] = renko_20
        df.loc[end_index,'renko1_40'] = renko_40
        df.loc[end_index,'renko1_bricks'] = renko_bricks
        # df.loc[end_index,'renko_+-'] = [df['renko_bricks'].shift(-2)<df['renko_bricks'].shift(-1) == '1']
    # print(df)
    # quit()
    return df
def renko2(df):
    # https://pypi.org/project/mplfinance/
    # https://github.com/matplotlib/mplfinance/issues/63
    def make_renko(df):
        df['렌코_고'] = (df['close']-df['high'].shift(1))/df['high'].shift(1)
        df['렌코_저'] = (df['close']-df['low'].shift(1))/ df['low'].shift(1)
        brick_size = df['close'].mean()
        ratio = abs((df['렌코_고'].mean()+df['렌코_저'].mean())/2)
        retdata = {}
        #https://towardsdatascience.com/mplfinance-matplolibs-relatively-unknown-library-for-plotting-financial-data-62c1c23177fd
        # mpf.plot(df,figratio=(10,6),type='candle',mav=(3,6,9),volume=True,tight_layout=True,savefig='back_renko_origin.png')
        mpf.plot(df, type="renko", mav=(3,6,9,12,20,40,60),volume=True,renko_params=dict(brick_size=brick_size*ratio),return_calculated_values=retdata, block=False, returnfig=True)
        # mpf.plot(df,figratio=(10,6),type='renko',mav=(3,6,9,12,20,40),volume=True,tight_layout=True,return_calculated_values=retdata, block=False, returnfig=True)

        plt.cla()
        plt.clf()
        plt.pause(0)
        plt.close()

        # 차트 그림으로 저장
        # mpf.plot(df,figratio=(10,6),type='renko',mav=(3,6,9),volume=True,tight_layout=True,return_calculated_values=retdata,
        #          block=False, returnfig=True,savefig=filename+'.jpg')
        df = pd.DataFrame(retdata)
        # print(df)
        # quit()
        renko_3=(list(retdata.get('mav3'))[-1])
        renko_6=(list(retdata.get('mav6'))[-1])
        renko_9=(list(retdata.get('mav9'))[-1])
        renko_12=(list(retdata.get('mav12'))[-1])
        renko_20=(list(retdata.get('mav20'))[-1])
        renko_40=(list(retdata.get('mav40'))[-1])
        renko_60=(list(retdata.get('mav60'))[-1])
        renko_bricks=(list(retdata.get('renko_bricks'))[-1])

        return renko_3,renko_6,renko_9,renko_12,renko_20,renko_40,renko_60,renko_bricks

    # print(df)
    loop = 100
    for i in range(len(df.index)-loop+1):
        f_index=i+loop
        df_renko=df.iloc[i:f_index]
        renko_3,renko_6,renko_9,renko_12,renko_20,renko_40,renko_60,renko_bricks = make_renko(df_renko)
        end_index = df_renko.index[-1]
        df.loc[end_index,'renko2_3'] = renko_3
        df.loc[end_index,'renko2_6'] = renko_6
        df.loc[end_index,'renko2_9'] = renko_9
        df.loc[end_index,'renko2_12'] = renko_12
        df.loc[end_index,'renko2_20'] = renko_20
        df.loc[end_index,'renko2_40'] = renko_40
        df.loc[end_index,'renko2_60'] = renko_60
        df.loc[end_index,'renko2_bricks'] = renko_bricks
        # df.loc[end_index,'renko_+-'] = [df['renko_bricks'].shift(-2)<df['renko_bricks'].shift(-1) == '1']
    # print(df)
    # quit()
    return df
def renko_sma(df):
    df['renko1_3평균'] = df['renko1_3'].rolling(window=avgtime).mean().round(3)
    df['renko1_6평균'] = df['renko1_6'].rolling(window=avgtime).mean().round(3)
    df['renko1_9평균'] = df['renko1_9'].rolling(window=avgtime).mean().round(3)
    df['renko1_12평균'] = df['renko1_12'].rolling(window=avgtime).mean().round(3)
    df['renko1_20평균'] = df['renko1_20'].rolling(window=avgtime).mean().round(3)
    df['renko1_40평균'] = df['renko1_40'].rolling(window=avgtime).mean().round(3)
    df['renko1_bricks'] = df['renko1_bricks'].rolling(window=avgtime).mean().round(3)
    return df
def heikin_ashi(df):
    heikin_ashi_df = pd.DataFrame(index=df.index.values, columns=['open', 'high', 'low', 'close'])
    heikin_ashi_df['close'] = (df['open'] + df['high'] + df['low'] + df['close']) / 4
    for i in range(len(df)):
        if i == 0:
            heikin_ashi_df.iat[0, 0] = df['open'].iloc[0]
        else:
            heikin_ashi_df.iat[i, 0] = (heikin_ashi_df.iat[i - 1, 0] + heikin_ashi_df.iat[i - 1, 3]) / 2
    heikin_ashi_df['high'] = heikin_ashi_df.loc[:, ['open', 'close']].join(df['high']).max(axis=1)
    heikin_ashi_df['low'] = heikin_ashi_df.loc[:, ['open', 'close']].join(df['low']).min(axis=1)
    heikin_ashi_df.rename(columns={'open':'hei_open','high':'hei_high','low':'hei_low','close':'hei_close'},inplace=True)
    heikin_ashi_df['hmao_5'] = heikin_ashi_df['hei_open'].rolling(window=5).mean().round(3)
    heikin_ashi_df['hmao_10'] = heikin_ashi_df['hei_open'].rolling(window=10).mean().round(3)
    heikin_ashi_df['hmao_20'] = heikin_ashi_df['hei_open'].rolling(window=20).mean().round(3)
    heikin_ashi_df['hmao_30'] = heikin_ashi_df['hei_open'].rolling(window=30).mean().round(3)
    heikin_ashi_df['hmac_5'] = heikin_ashi_df['hei_close'].rolling(window=5).mean().round(3)
    heikin_ashi_df['hmac_10'] = heikin_ashi_df['hei_close'].rolling(window=10).mean().round(3)
    heikin_ashi_df['hmac_20'] = heikin_ashi_df['hei_close'].rolling(window=20).mean().round(3)
    heikin_ashi_df['hmac_30'] = heikin_ashi_df['hei_close'].rolling(window=30).mean().round(3)
    df = pd.concat([df, heikin_ashi_df], axis=1)
    return df

def df_add(df):
    avgtime = 30
    df['고저평균대비등락율'] = (df['close'] / ((df['high'] + df['low']) / 2) - 1) * 100
    df['고저평균대비등락율'] = df['고저평균대비등락율'].round(2)

    df['최고등락'] = (df['high']-df['low'])/df['low']*100
    df['최고등락평균'] = df['최고등락'].rolling(window=60).mean().round(3)
    df['등락'] = (df['close']-df['open'])/df['open']*100
    df['등락평균'] = df['등락'].rolling(window=60).mean().round(3)

    df['거래대금차'] = df['value'] - df['value'].shift(1)
    df['거래대금차'].iloc[0] = 0  # 초반 튀는값 잡기위해

    df['거래대금차평균'] = df['거래대금차'].rolling(window=avgtime).mean().round(3)

    df['직전거래대금차'] = df['거래대금차'].shift(1)
    df['거래대금변동'] = (df['직전거래대금차'] - df['거래대금차'])

    df['거래대금변동절대'] = abs(df['직전거래대금차'] - df['거래대금차'])
    df['거래대금변동평균'] = df['거래대금변동절대'].rolling(window=avgtime).mean().round(3)

    df['거래대금평균최고'] = df['거래대금차평균'].rolling(window=avgtime).max()
    df['거래대금평균최고'] = df['거래대금평균최고'].round(3)
    df['거래대금평균최고마지'] = df['거래대금평균최고']*0.9
    df['초대금평균차초대금평균최고'] = abs(df['거래대금차평균'] - df['거래대금평균최고'])

    df['거래대금평균60'] = df['거래대금차'].rolling(window=60).mean()
    df['거래대금평균60'] = df['거래대금평균60'].round(3)

    df['거래대금평균120'] = df['거래대금차'].rolling(window=120).mean()
    df['거래대금평균120'] = df['거래대금평균120'].round(3)

    df['거래대금각도'] = np.arctan((df['value']-df['value'].shift(1))/1000) * 180 / np.pi

    df['봉거래대금'] = df['close'] * df['volume']

    df['봉거래대금평균'] = df['봉거래대금'].rolling(window=avgtime).mean().round(3)
    df['봉거래대금평균최고'] = df['봉거래대금평균'].rolling(window=avgtime).max().round(3)
    df['rsi_gap'] = df['rsi'] - df['rsi'].shift(1)

    return df
def change_price(df):
    df['최고등락'] = (df['high']-df['low'])/df['low']*100
    df['등락'] = (df['close']-df['open'])/df['open']*100
    return df
def sma(df):
    df['ma5'] = round(talib.MA(df['close'], timeperiod=5),1)
    df['ma20'] = round(talib.MA(df['close'], timeperiod=20),1)
    df['ma60'] = round(talib.MA(df['close'], timeperiod=60),1)
    df['ma90'] = round(talib.MA(df['close'], timeperiod=90),1)
    df['ma300'] = round(talib.MA(df['close'], timeperiod=300),1)
    df['ma60마지'] = round(df['ma60']*0.98,1)
    df['ma300마지'] = round(df['ma300']*0.98,1)
    return df

def CCI(df):
    df['cci'] = talib.CCI(df['high'],df['low'],df['close'], timeperiod=14)
    return df

def CMO(df):
    df['cmo'] = talib.CMO(df['close'], timeperiod=14)
    return df

def RSI(df):
    df['rsi'] = round(talib.RSI(df['close'],timeperiod=14),1)
    df['rsi_upper'] = 70
    df['rsi_lower'] = 30
    df['val_rsi'] = round(talib.RSI(df['value'], timeperiod=14), 1)


    return df

def BBAND(df):
    df['band_upper'],df['band_middle'],df['band_lower'] = talib.BBANDS(df['close'],20,2)
    return df

def ATR(df):
    df['atr'] = talib.ATR(df['high'],df['low'],df['close'], timeperiod=14)
    return df

def ALL(df):
    df = sma(df)
    df = CCI(df)
    df = CMO(df)
    df = RSI(df)
    df = df_add(df)
    df = BBAND(df)
    df = ATR(df)
    df = heikin_ashi(df)
    df = df_add(df)
    df = change_price(df)
    return df

def compare(df):
    pass

if __name__ == '__main__':
    db_path = 'D:/db_files/'
    db_ohlcv = db_path + 'upbit.db'
    con = sqlite3.connect(db_ohlcv)
    cur = con.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    table_list = cur.fetchall()  # fetchall 한번에 모든 로우 데이터 읽기 (종목코드 읽기)
    if not table_list:
        print('* DB 테이블이 비어있음 - 확인 필요 *')
        quit()
    table_list = np.concatenate(table_list).tolist()  # 모든테이블을 리스트로변환 https://codechacha.com/ko/python-flatten-list/
    print(table_list)
    for ticker in table_list:
        print(f'{ticker} 변환중...')
        df = pd.read_sql(f"SELECT * FROM '{ticker}'", con).set_index('index')
        list_columns_exist=df.columns.tolist()
        df = df_add(df)
        df = sma(df)
        df = CCI(df)
        df = CMO(df)
        df = RSI(df)
        df = df_add(df)
        df = BBAND(df)
        df = ATR(df)
        df = heikin_ashi(df)
        df = change_price(df)
        list_columns_new = df.columns.tolist()
        print(list_columns_exist)
        print(list_columns_new)
        list_columns = list(set(list_columns_new) - set(list_columns_exist))  # 새로받은 인덱스랑 기존인덱스 비교
        if list_columns:
            print(list_columns)
            print(df[list_columns])
            cur.execute(f"ALTER TABLE '{ticker}' ADD COLUM {list_columns} ")

        quit()
        df.to_sql(ticker, con, if_exists='replace')
    con.commit()
    con.close()