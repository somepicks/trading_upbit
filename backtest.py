import pandas as pd
import sqlite3
import numpy as np
import datetime
import talib
import make_indicator
import hoga
pd.set_option('mode.chained_assignment',  None) # SettingWithCopyWarning 경고를 끈다
pd.set_option('display.max_columns',None) #모든 열을 보고자 할 때
pd.set_option('display.width',1500)
pd.set_option("display.unicode.east_asian_width", True)

def buy_stg(df):
    # df.loc[(df.rsi < 30) & (df.ma20 > df.ma60) & (df.low<df.band_lower),'매매신호'] = True
    # df['매매신호'] = True
    df.loc[df.index ,'매매신호'] = True
    df.loc[(df.hei_close < df.hei_open) & (df.매매신호==True) ,'매매신호'] = np.nan
    df.loc[((df.hmac_5 - df.hmac_10)<80000) & (df.매매신호==True) ,'매매신호'] = np.nan
    df.loc[((df.hma_gap_l)<1) & (df.매매신호==True) ,'매매신호'] = np.nan
    # df.loc[(df.hei_close < df.hei_open) & (df.매매신호==True) ,'매매신호'] = np.nan
    # df.loc[(df.rsi > 30) & (df.매매신호==True) ,'매매신호'] = np.nan

    df.loc[(df['매매신호'].shift(1)==True) , '매수가'] = df['open'].apply(buy_hoga_return)
    df['매수가'].fillna(method='ffill', inplace=True)  # nan값을 윗 값으로 채움

    # df.loc[(df['매매신호'].shift(1)==True) , '손절가'] = df['매수가'].apply(loss_hogaPriceReturn_per)
    return df
def sell_stg(df):
    # df['매수대비'] = (df['close']-df['매수가'])/df['매수가']*100

    # print(df)
    # quit()
    # df.loc[(df.close > df.band_upper) & (df.rsi > 70) ,'매매신호'] = False
    # df.loc[(df.cmo_20 < df.cmo_30) & (df.hmac_5 <= df.hmao_5) ,'매매신호'] = False
    df.loc[(df.hmac_5 <= df.hmao_10) ,'매매신호'] = False
    df.loc[(df.hmao_10 <= df.band_lower) ,'매매신호'] = False

    # df.loc[(df.close < df.band_middle),'매매신호'] = False
    # df.loc[(df['매매신호'].shift(1)==True),'매매신호'] = False
    df.loc[(df['매매신호'].shift(1)==False), '매도가'] = df['open'].apply(sell_hoga_return)
    return df
def losscut_stg(df):
    df.loc[df['기간수익률']<loss_per,'손절'] = True
    df.loc[df.index,'기간수익률'] = np.nan
    df.loc[df.index,'보유여부'] = np.nan
    df=buy_stg(df)
    df=sell_stg(df)
    df.loc[(df['매매신호'].shift(1) == True) & (df['low'] < df['매수가']) & (df['손절']!=True), '보유여부'] = True
    df.loc[(df['매매신호'].shift(1) == False) & (df['high'] > df['매도가']) | (df['손절']==True), '보유여부'] = False

    df['보유여부'].ffill(inplace=True) # NaN값을 윗 값으로 채움
    df['보유여부'].fillna(False, inplace=True) # NaN값을 False로 채움
    df.loc[(df['보유여부']==False) & (df['보유여부'].shift(1)==True)& (df['손절']==True),'매도체결가' ] = df['low']
    df.loc[df['보유여부']==True,'기간수익률'] = round((df['close']-df['매수체결가'])/df['매수체결가']*100,1)
    df.loc[df['보유여부'].shift(1)==False,'매도체결가' ] = np.nan
    df.loc[(df.보유여부==True),'손절가'] = df['매수체결가']-(df['매수체결가']*abs(loss_per)*0.01)
    return df
def df_backtest(df,ticker):
    df = df[['open', 'high', 'low', 'close', 'ma20', 'ma60', 'rsi','band_upper','band_lower','band_middle','val_rsi','hei_open','hei_close','고저평균대비등락율','hmac_5','hmac_10','hmao_5','hmao_10','cmo_20','cmo_30','hma_gap_l','hma_gap_h']]
    df = buy_stg(df)
    df = sell_stg(df)
    df.loc[(df['매매신호'].shift(1) == True) & (df['low'] < df['매수가']), '보유여부'] = True
    df.loc[(df['매매신호'].shift(1) == False) & (df['high'] > df['매도가']), '보유여부'] = False
    df['보유여부'].ffill(inplace=True) # NaN값을 윗 값으로 채움
    df['보유여부'].fillna(False, inplace=True) # NaN값을 False로 채움
    df.loc[(df['보유여부']==True) & (df['보유여부'].shift(1)==False),'매수체결가' ]= df['매수가']
    df.loc[(df['보유여부']==False) & (df['보유여부'].shift(1)==True),'매도체결가' ]= df['매도가']
    if df.loc[df.index[-1],'보유여부'] == True: #공정한 백테를 위해 마지막에 일괄 정리
        df.loc[df.index[-1],'매도체결가'] = df.loc[df.index[-1],'close']
        df.loc[df.index[-1],'보유여부'] = False
    df['매수체결가'].fillna(method='ffill', inplace=True)  # nan값을 윗 값으로 채움
    # df.loc[df['보유여부']==False,'매수체결가'] = np.nan
    # df['보유수익률'] = df.loc[df['보유여부'] == True, '일간수익률']
    # df['보유수익률'].fillna(1, inplace=True)
    df.loc[df['보유여부']==True,'기간수익률'] = round((df['close']-df['매수체결가'])/df['매수체결가']*100,1)

    df = losscut_stg(df)
    # df.loc[df['기간수익률']<loss_per,'매도체결가'] = df['high']
    df.loc[(df['매도체결가']>0) & (df['보유여부']==False),'수익률'] = round(((df['매도체결가']-df['매수체결가'])/df['매수체결가'].shift(1)*100)-0.1,1)
    df.loc[(df['매도체결가']>0) & (df['보유여부']==False),'수익금'] = round(((df['매도체결가']/df['매수체결가'].shift(1)-0.001)*bet)-bet)
    df.loc[(df['매도체결가']>0) & (df['보유여부']==False),'수수료'] = round(0.001*bet)
    df['단순보유수익률'] = round((df['close'] - df.iloc[0, 0])/df.iloc[0, 0]*100,1)
    # df[['수익률', '단순보유수익률']].plot(figsize=(8, 4))
    df['종목명']=str(ticker[:ticker.find('-')])
    # df['index_2']=df.index
    # df.loc[(df.보유여부==True) & (df.보유여부.shift(1)==False & (df.매매신호.shift(1) == True) ),'매수시간']=df['index_2'] #앞의 조건을 만족하면 '매수시간'컬럼에 'index_2'값 입력
    # df.loc[(df.보유여부==False) & (df.보유여부.shift(1) == True),'매도시간']=df['index_2']
    df.loc[(df.보유여부==True) & (df.보유여부.shift(1)==False & (df.매매신호.shift(1) == True) ),'매수시간']=pd.Series(df.index,index=df.index) #앞의 조건을 만족하면 '매수시간'컬럼에 'index_2'값 입력
    df.loc[(df.보유여부==False) & (df.보유여부.shift(1) == True),'매도시간']=pd.Series(df.index,index=df.index)
    # print(df)
    df['매수시간'].fillna(method='ffill', inplace=True)  # nan값을 윗 값으로 채움
    df['매수시간'] = df['매수시간'].fillna(0) #nan값을 다른값으로 대체 후 타입변환 가능
    df['매도시간'] = df['매도시간'].fillna(0)
    # print(pd.Series(df.index,index=df.index).index[-1])
    df.loc[df.index[-1],'매도시간'] = pd.Series(df.index,index=df.index).index[-1] #마지막에 일괄 매도이기 때문에 매도시간 마지막행을 인덱스마지막행으로 변경
    df['매수시간'] = df['매수시간'].astype(np.int64)
    df['매도시간'] = df['매도시간'].astype(np.int64)
    make_detail_db(df,ticker)

    # index_x = df[(df['매수시간'].isnull()) & (df['매도시간'].isnull())].index
    # index_x = df[df['매도시간'].isnull()].index # 매도시간이 비어있는 행을(매수시간행)을 반환
    # df.fillna(method='ffill',inplace=True) #nan값을 윗 값으로 채움
    # df.drop(index_x,inplace=True) # 매수시간 행 삭제

    #- 데이터프레임.fillna(method='ffill'): 평균으로 채움
    #- 데이터프레임.fillna(method='ffill'): 바로 앞 데이터로 채움
    #- 데이터프레임.fillna(method='bfill'): 바로 뒤 데이터로 채움
    #- 데이터프레임.fillna(특정_값): 특정 값으로 채움

    index_x = df[df['매도체결가'].isnull()].index #매도체결가가 null인 행 찾아서 지우기
    df.drop(index_x,inplace=True)
    # index_x = df[(df['매도시간'].isnull()) & (df['보유여부']==False)].index
    df=df[['종목명','매수시간','매도시간','매수체결가','매도체결가','손절','손절가','수익률','수익금','수수료']]
    if df.empty:
        pass
    ror = round(df['수익률'].mean(),1)
    rop = df['수익금'].sum()
    print(f' - 수익률: {ror}, 수익금: {rop}')
    return df
def make_back_db(df):
    ror = df['수익률'].mean()
    plus=df[df['수익률'] > 0]
    minus=df[df['수익률'] < 0]
    benefit = df['수익금'].sum()
    df['수익금합계']=df['수익금'].cumsum()
    df['interval']=interval
    df['매수시간'] = df['매수시간'].astype(str)
    df['매도시간'] = df['매도시간'].astype(str)
    df['매수체결가'] = df['매수체결가'].astype(str)
    df['매도체결가'] = df['매도체결가'].astype(str)
    df['수익률'] = df['수익률'].astype(str)
    df.rename(columns={'매수체결가': '매수가'}, inplace=True)
    df.rename(columns={'매도체결가': '매도가'}, inplace=True)

    print(df)
    df['매수시간_dt'] = pd.to_datetime(df['매수시간'], format='%Y%m%d%H%M%S') #int형을 datetime으로 변환
    df['매도시간_dt'] = pd.to_datetime(df['매도시간'], format='%Y%m%d%H%M%S') #int형을 datetime으로 변환
    df['보유시간']=df['매도시간_dt']-df['매수시간_dt']
    had_time = df['보유시간'].mean()
    df['매수시간_dt']=df['매수시간_dt'].astype(str)
    df['매도시간_dt']=df['매도시간_dt'].astype(str)
    df['보유시간']=df['보유시간'].astype(str)
    # df = df[df.duplicated(subset=['매수시간', '매도시간'], keep=False)]
    con = sqlite3.connect(back_file)
    dt_now = str(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
    table = 'coins_vj_'+ dt_now
    df.to_sql(table, con, if_exists='replace')
    # group = df.groupby(df.index)
    # print(group.size().max())

    plus_per = len(plus)/len(df.index)*100
    result = {'interval':interval,'거래횟수': len(df.index),'평균수익률': round(ror,2),'익절': len(plus),
              '손절': len(minus), '승률': round(plus_per,1),'수익금합계': benefit,'평균보유기간': str(had_time)[:15],
              '배팅금액': bet,'수익률합계': 0, '최대낙폭률': 0,'필요자금': 0, '일평균거래횟수': 0,
              '최대보유종목수': 0,'매수전략':'기술적 매수','매도전략':'예술적 매도'}
    df_result = pd.DataFrame(result, index=[dt_now])
    df_result.to_sql('coins_vj', con, if_exists='append')
    con.commit()
    con.close()
    return df_result
def make_detail_db(df,ticker):
    con = sqlite3.connect(back_detail_file)
    df.to_sql(ticker, con, if_exists='replace')
    con.commit()
    con.close()
def get_ticker_list(cur,interval):
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    table_list = cur.fetchall()  # fetchall 한번에 모든 로우 데이터 읽기 (종목코드 읽기)
    if not table_list:
        print('* DB 테이블이 비어있음 - 확인 필요 *')
        quit()
    table_list = np.concatenate(table_list).tolist()  # 모든테이블을 리스트로변환 https://codechacha.com/ko/python-flatten-list/
    # print(table_list)
    exist_list =[]

    # for ticker in table_list:
    #     position=ticker.find('-')+1
    #     if str(ticker[position:]) == interval:
    #         exist_list.append(ticker)
    [exist_list.append(x) for x in table_list if str(x[x.find('-')+1:]) == interval] #for문을 컴프리헨션으로

    return exist_list
def df_add(df):
    df['val_rsi'] = round(talib.RSI(df['value'], timeperiod=14), 1)
    df['고저평균대비등락율'] = (df['close'] / ((df['high'] + df['low']) / 2) - 1) * 100
    df['고저평균대비등락율'] = df['고저평균대비등락율'].round(2)
    df['hmao_5'] = df['hei_open'].rolling(window=5).mean().round(3)
    df['hmao_10'] = df['hei_open'].rolling(window=10).mean().round(3)
    df['hmac_5'] = df['hei_close'].rolling(window=5).mean().round(3)
    df['hmac_10'] = df['hei_close'].rolling(window=10).mean().round(3)
    df['cmo_5'] = df['cmo'].rolling(window=5).mean().round(3)
    df['cmo_20'] = df['cmo'].rolling(window=20).mean().round(3)
    df['cmo_30'] = df['cmo'].rolling(window=30).mean().round(3)
    df['cmo_60'] = df['cmo'].rolling(window=60).mean().round(3)
    df['hma']=df['hmac_5']-df['hmac_10']
    df['hma최고']=df['hma'].rolling(window=5).max()
    df['hma최저']=df['hma'].rolling(window=5).min()
    df['hma_gap_l'] = df['hma']-df['hma최저']
    df['hma_gap_h'] = df['hma최고']-df['hma']
    # df=make_indicator.heikin_ashi(df)
    return df
def hogaUnitCalc(price):
    hogaUnit = 1
    if price < 10:
        hogaUnit = 0.01
    elif price < 100:
        hogaUnit = 0.1
    elif price < 1000:
        hogaUnit = 1
    elif price < 10000:
        hogaUnit = 5
    elif price < 100000:
        hogaUnit = 10
    elif price < 500000:
        hogaUnit = 50
    elif price < 1000000:
        hogaUnit = 100
    elif price < 2000000:
        hogaUnit = 500
    elif price > 2000000:
        hogaUnit = 1000
    return hogaUnit
def buy_hoga_return(currentPrice): #틱으로 반환
    hogaPrice = currentPrice
    for _ in range(abs(buy_hoga)):
        if buy_hoga < 0:
            minusV = (hogaPrice - 1)
            hogaunit = hogaUnitCalc(minusV)
            mot = minusV // hogaunit
            hogaPrice = mot * hogaunit
        elif buy_hoga > 0:
            hogaunit = hogaUnitCalc(hogaPrice)
            hogaPrice = hogaPrice + hogaunit
    return hogaPrice
def sell_hoga_return(currentPrice): #틱으로 반환
    hogaPrice = currentPrice
    for _ in range(abs(sell_hoga)):
        if sell_hoga < 0:
            minusV = (hogaPrice - 1)
            hogaunit = hogaUnitCalc(minusV)
            mot = minusV // hogaunit
            hogaPrice = mot * hogaunit
        elif sell_hoga > 0:
            hogaunit = hogaUnitCalc(hogaPrice)
            hogaPrice = hogaPrice + hogaunit
    return hogaPrice
def hogaUnitCalc_per(hogaPrice):
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
    elif (hogaPrice < 1000000) :
        minPrice = 1000000
    elif (hogaPrice < 2000000) :
        minPrice = 2000000
    elif (hogaPrice > 2000000) :
        minPrice = 100000000
    elif (hogaPrice >= 500000):
        minPrice = 500000
    elif (hogaPrice >= 50000) :
        minPrice = 50000
    return minPrice
def loss_hogaPriceReturn_per(currentPrice): #퍼센트로 반환
    hogaPrice = currentPrice * ((loss_per * 0.01) + 1)
    hogaUnit = hogaUnitCalc(hogaPrice)
    minPrice = hogaUnitCalc_per(hogaPrice)
    while True:
        minPrice = (minPrice - hogaUnit)
        if minPrice <= hogaPrice:
            return round(minPrice, 2)

if __name__ == '__main__':
    db_path = "D:/db_files"
    ohlcv_db = db_path + '/upbit.db'
    back_file = db_path + '/upbit_backtest.db'
    back_detail_file = db_path + '/upbit_backtest_detail.db'
    coin_con = sqlite3.connect(ohlcv_db)
    cur = coin_con.cursor()

    interval = 'minute3'
    bet = 10000
    optimization = True
    if optimization == True:
        buy_hoga = -2
        sell_hoga = 3
        loss_per = -1
        sell_per = 0.7
    else:
        buy_hoga = -2
        sell_hoga = 3
        loss_per = -1
        sell_per = 0.7
    # tickers = get_ticker_list(cur,interval)
    tickers =['BTC-'+interval]
    # tickers =['AVAX-'+interval,'ALGO-'+interval,'GLM-'+interval,'SRM-'+interval,'TON-'+interval,'BAT-'+interval]
    df_amount = pd.DataFrame()
    for ticker in tickers:
        df = pd.read_sql(f"SELECT * FROM '{ticker}'", coin_con).set_index('index')
        # df = df.iloc[2490:2520]
        print(ticker,end='')
        df = df_add(df)
        df = df_backtest(df,ticker)
        df_amount = pd.concat([df,df_amount],axis=0)
    coin_con.commit()
    coin_con.close()
    df_result = make_back_db(df_amount)
    print(df_result)
    # make_back_db(df)
