import time
import datetime
import pandas as pd
pd.set_option('display.max_columns',None)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width',1200)
pd.set_option("display.unicode.east_asian_width", True)
import pyupbit
# coin4 = order_upbit_book.Order_Book("KRW-BTC", "60", -1.5, 2.4, 100000)
# coin5 = order_upbit_book.Order_Book("KRW-BTC", "60", -2.3, 3.3, 200000)
# coin6 = order_upbit_book.Order_Book("KRW-BTC", "60", -3, 4.9, 400000)
import talib as ta
import numpy as np
import sqlite3
import hoga
import os

def run():
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    table_list = cur.fetchall()  # fetchall 한번에 모든 로우 데이터 읽기 (종목코드 읽기)
    if not table_list:
        print('* DB 테이블이 비어있음 - 확인 필요 *')
        quit()
    table_list = np.concatenate(table_list).tolist()  # 모든테이블을 리스트로변환 https://codechacha.com/ko/python-flatten-list/
    [table_list.remove(x) for x in table_list if x == '잔고조회']  # 테이블 리스트에서 잔고조회 삭제
    tickers = pyupbit.get_tickers(fiat='KRW')
    tickers = [str(x[4:]) for x in tickers]
    # tickers = ['KRW-BTC']
    if table_list != tickers: #신규상장이 있을경우
        update_tickers(table_list,tickers,con,cur)

    for i,ticker in enumerate(tickers):
        time.sleep(0.1)
        df = pd.read_sql(f"SELECT * FROM '{ticker}'", con).set_index('index')

        #서버점검 시 대책마련

        df_add = pyupbit.get_ohlcv('KRW-'+ticker, interval=interval, count=5)
        df_add.index = df_add.index.strftime("%Y%m%d%H%M%S").astype(np.int64)
        df_add = df_add.drop([df_add.index[-1]]) #마지막 행은 현재 만들어지고 있는거기 때문에 제거
        # if df.index[-1] == df_add.index[-1]: #인덱스가 중복되어 저장되는 경우가 발생해서
        #     print('df결합')
        df_sum = pd.concat([df,df_add])
        # print(df_sum.tail(10))
        duplicateRowsDF = df_sum[df_sum.index.duplicated()] #중복되는인덱스의 df 추출
        if len(duplicateRowsDF) ==len(df_add.index): #인덱스가 전부 중복일 경우 continue
            continue
        elif not df_sum.index.is_unique: #인덱스가 고유하지 않을 경우(중복이 있을 경우)
            df_add.drop(duplicateRowsDF.index,inplace=True) #중복되는 행의 인덱스 반환 후 삭제
        # df = df.loc[~df.index.duplicated(keep='last')] #인덱스가 중복인 행은 마지맊꺼 살리고 제거
        df_add = make_df(ticker,df,df_add)
        df_add['now'] = int(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
        # print(ticker)
        df_add.to_sql(ticker, con, if_exists='append')

    df_eval = evaluated()
    df_eval.to_sql('잔고조회', con, if_exists='append')
    con.commit()
    # cur.close()
    con.close()
def stg(df):
    # print(stg)
    df['ma20'] = round(ta.MA(df['close'], timeperiod=20))
    df['ma60'] = round(ta.MA(df['close'], timeperiod=60))
    df['rsi'] = round(ta.RSI(df['close'], timeperiod=14))
    df['고저평균대비등락율'] = (df['close'] / ((df['high'] + df['low']) / 2) - 1) * 100
    df['고저평균대비등락율'] = df['고저평균대비등락율'].round(2)
    df.loc[(df.rsi < 30) & (df.고저평균대비등락율 < 0.2), '매매신호'] = True  # 매수 신호
    df.loc[(df.수익률>0),'매매신호'] = False  # 매도 신호
    df.loc[(df.rsi > 120) & (df.ma20 < df.ma60), '손절신호'] = True  # 손절 신호
    return df
def make_df(ticker,df,df_add):
    add_lenth = len(df_add)
    for i in range (add_lenth):
        df = pd.concat([df,df_add.iloc[[i]]],axis=0)
        df = stg(df)
        if df.loc[df.index[-2],'보유여부'] == False :   # 0==False #보유 하고 있지 않을 때
            print(f'{ticker} - (인덱스 생성 {i+1} of {add_lenth})',end=' | ')
            df=buy(ticker,df)
        elif df.loc[df.index[-2],'보유여부'] == True: # 보유 하고 있을 때
            print(f'{ticker} - (인덱스 생성 {i+1} of {add_lenth})', end=' | ')
            df=sell(ticker,df)
        else:
            print(f'{ticker} - (인덱스 생성 {i+1} of {add_lenth})')
    # print(df)
    df_add = df[-add_lenth:] #입력받은 df_add만 계산 후 다시 반환
    return df_add
def sell(ticker,df):
    sell_signal = df.loc[df.index[-1],'매매신호']
    loss_cut_signal = df.loc[df.index[-1],'손절신호']
    uuid=df.loc[df.index[-2], 'uuid']
    if loss_cut_signal == True: #시장가 매도
        pass
    elif sell_signal == False : #매도신호
        if uuid=='empty': #처음 매도신호 발생
            print(f'{datetime.datetime.now().strftime("%H:%M:%S")} - 매도신호 발생')
            df.loc[df.index[-1],'보유여부'] = df.loc[df.index[-2],'보유여부']
            df.loc[df.index[-1], '매수가'] = df.loc[df.index[-2], '매수가']
            df.loc[df.index[-1], '매수수량'] = df.loc[df.index[-2], '매수수량']
            df.loc[df.index[-1], '매수금액'] = df.loc[df.index[-2], '매수금액']
            df.loc[df.index[-1], '수수료'] = df.loc[df.index[-2], '수수료']
            sell_uuid, sell_price = order_sell(ticker,df,sell_hoga) #매도주문  uuid 생성
            df.loc[df.index[-1],'uuid'] = sell_uuid
            df.loc[df.index[-1],'매도가'] = sell_price
            df = ror(df)
        elif uuid != 'empty' and str == type(uuid):  #기존 매도신호가 있었는데 또 매도신호 들어올 때
            df = check_sell(df,uuid)
            uuid = df.loc[df.index[-1], 'uuid']  # 체크 후 다시한번 uuid로 체결되었는지 확인
            if uuid != 'empty'and str == type(uuid):  # 기존 매수신호가 있었을 때
                print(f'{datetime.datetime.now().strftime("%H:%M:%S")} - 매도취소(추가 매도신호) | ', upbit.cancel_order(uuid)) #매도 취소
                df.loc[df.index[-1], 'uuid'] = 'empty'
                sell_uuid, sell_price = order_sell(ticker, df, sell_hoga)  # 다시 매도주문  uuid 생성
                df.loc[df.index[-1],'uuid'] = sell_uuid
                df.loc[df.index[-1],'매도가'] = sell_price
                df = ror(df)
    elif np.isnan(sell_signal): # 매도신호 없음
        if uuid=='empty': # 기존에 매도신호 없었음
            print(f'{datetime.datetime.now().strftime("%H:%M:%S")} - 보유유지')
            df.loc[df.index[-1],'보유여부'] = df.loc[df.index[-2],'보유여부']
            df.loc[df.index[-1],'매수가'] = df.loc[df.index[-2],'매수가']
            df.loc[df.index[-1], '매수수량'] = df.loc[df.index[-2], '매수수량']
            df.loc[df.index[-1], '매수금액'] = df.loc[df.index[-2], '매수금액']
            df.loc[df.index[-1], '수수료'] = df.loc[df.index[-2], '수수료']
            df.loc[df.index[-1],'uuid'] = df.loc[df.index[-2],'uuid']
            df = ror(df)
        elif uuid != 'empty'and str == type(uuid):  #기존 매도신호가 있었을 때
            df=check_sell(df,uuid)
            df=ror(df)
    elif sell_signal == True: #매도 취소
        if uuid != 'empty'and str == type(uuid):  # 기존 매도신호가 있었을 때
            print(f'{datetime.datetime.now().strftime("%H:%M:%S")} - 매도취소(매수신호) | ',upbit.cancel_order(uuid))
            df.loc[df.index[-1], 'uuid'] = 'empty'
    return df
def check_sell(df,uuid):
    my_order = upbit.get_order(ticker_or_uuid=uuid)
    if my_order['side'] == 'ask':  # 매도 체크
        if my_order['state'] == 'wait':  # 미 체결 시
            print(f'{datetime.datetime.now().strftime("%H:%M:%S")} - 매도 미체결', my_order)
            df.loc[df.index[-1], '보유여부'] = df.loc[df.index[-2], '보유여부']
            df.loc[df.index[-1], '매수가'] = df.loc[df.index[-2], '매수가']
            df.loc[df.index[-1], '매수수량'] = df.loc[df.index[-2], '매수수량']
            df.loc[df.index[-1], '매수금액'] = df.loc[df.index[-2], '매수금액']
            df.loc[df.index[-1], '수수료'] = df.loc[df.index[-2], '수수료']
            df = ror(df)
            df.loc[df.index[-1], 'uuid'] = df.loc[df.index[-2],'uuid']
        elif my_order['state'] == 'done':  # 매도 체결
            print(f'{datetime.datetime.now().strftime("%H:%M:%S")} - 매도체결 | ', my_order)
            df.loc[df.index[-1], '보유여부'] = False
            df.loc[df.index[-1], '매수가'] = df.loc[df.index[-2], '매수가']
            df.loc[df.index[-1], '매수수량'] = df.loc[df.index[-2], '매수수량']
            df.loc[df.index[-1], '매수금액'] = df.loc[df.index[-2], '매수금액']
            df.loc[df.index[-1], '수수료'] = float(my_order['paid_fee'])
            df.loc[df.index[-1], '매도가'] = df.loc[df.index[-2], '매도가']
            df.loc[df.index[-1], '매도금액'] = float(my_order['trades'][0]['funds'])
            df.loc[df.index[-1], '수익금'] = (df.loc[df.index[-1], '매도금액']) - (df.loc[df.index[-1], '매수금액'])
            df.loc[df.index[-1], '매도시간'] = df.index[-2]
            df.loc[df.index[-1], 'uuid'] = 'empty'
        elif my_order['state'] == 'cancle':  # 매도 취소 시
            print(f'{datetime.datetime.now().strftime("%H:%M:%S")} - 매도취소(state == cancle)')
            df.loc[df.index[-1], '보유여부'] = df.loc[df.index[-2], '보유여부']
            df.loc[df.index[-1], '매수가'] = df.loc[df.index[-2], '매수가']
            df.loc[df.index[-1], '매수수량'] = df.loc[df.index[-2], '매수수량']
            df.loc[df.index[-1], '매수금액'] = df.loc[df.index[-2], '매수금액']
            df.loc[df.index[-1], '수수료'] = df.loc[df.index[-2], '수수료']
    return df
def buy(ticker,df):
    buy_signal = df.loc[df.index[-1],'매매신호']
    uuid=df.loc[df.index[-2], 'uuid']
    if buy_signal==True: # 매수신호
        if uuid=='empty': #처음 매수신호 발생
            print(f'{datetime.datetime.now().strftime("%H:%M:%S")} - 매수신호 발생')
            df.loc[df.index[-1],'수수료'] = bet * commission
            uuid,buy_price,vol = order_buy(ticker,buy_hoga)
            df.loc[df.index[-1],'매수가'] = buy_price
            df.loc[df.index[-1],'매수수량'] = vol
            df.loc[df.index[-1],'매수금액'] = (buy_price * vol) + (bet * commission)
            df.loc[df.index[-1],'uuid'] = uuid
            df.loc[df.index[-1], '보유여부'] = False
        elif uuid != 'empty'and str == type(uuid):  #기존 매수신호가 있었을 때
            df = check_buy(ticker,df,uuid)

    elif np.isnan(buy_signal): # 매수신호 없음
        if uuid == 'empty':  # 매수 안함
            df.loc[df.index[-1], '보유여부'] = False
            df.loc[df.index[-1], 'uuid'] = uuid
            print(f'{datetime.datetime.now().strftime("%H:%M:%S")} - 매수신호 없음')
        elif uuid != 'empty'and str == type(uuid): #기존 매수신호가 있었을 때
            df = check_buy(ticker,df,uuid)

    elif buy_signal == False: # 매도신호
        if uuid != 'empty'and str == type(uuid):  # 기존 매수신호가 있었을 때
            df = check_buy(ticker,df,uuid)
            uuid = df.loc[df.index[-1], 'uuid'] #체크 후 다시한번 uuid로 체결되었는지 확인
            if uuid != 'empty'and str == type(uuid):  # 미 체결 시
                print(f'{datetime.datetime.now().strftime("%H:%M:%S")} - 매수취소(매도신호)', upbit.cancel_order(uuid))
                df.loc[df.index[-1], 'uuid'] = 'empty'
    return df
def check_buy(ticker,df,uuid):
    my_order = upbit.get_order(ticker_or_uuid=uuid)
    # print(my_order)
    if my_order['side'] == 'bid':  # 매수 체크
        if my_order['state'] == 'wait':  # 미 체결 시
            df.loc[df.index[-1], '보유여부'] = False
            df.loc[df.index[-1], '매매신호'] = df.loc[df.index[-2], '매매신호'] + 1
            signal_num =df.loc[df.index[-1], '매매신호']
            print(f'{datetime.datetime.now().strftime("%H:%M:%S")} - 매수 미체결 {signal_num}회 동안 매수하지 못 함 |')
            df.loc[df.index[-1], '매수가'] = df.loc[df.index[-2], '매수가']
            df.loc[df.index[-1], '매수수량'] = df.loc[df.index[-2], '매수수량']
            df.loc[df.index[-1], '매수금액'] = df.loc[df.index[-2], '매수금액']
            df.loc[df.index[-1], '수수료'] = df.loc[df.index[-2], '수수료']
            df.loc[df.index[-1], 'uuid'] = uuid
            if df.loc[df.index[-1], '매매신호'] == buy_limit:  # 매수가 buy_limit횟수만큼 안될 시 매수 취소
                print(f'{ticker} - 매수취소 {buy_limit}회 동안 매수하지 못 함 |',
                      upbit.cancel_order(df.loc[df.index[-1], 'uuid']))
                df.loc[df.index[-1], 'uuid'] = 'empty'
        elif my_order['state'] == 'done':  # 매수 체결 시
            print(f'{datetime.datetime.now().strftime("%H:%M:%S")} - 매수체결 | ', my_order)
            df.loc[df.index[-1], '보유여부'] = True
            df.loc[df.index[-1], '매수가'] = df.loc[df.index[-2], '매수가']
            df.loc[df.index[-1], '매수수량'] = df.loc[df.index[-2], '매수수량']
            df.loc[df.index[-1], '매수금액'] = df.loc[df.index[-2], '매수금액']
            df.loc[df.index[-1], '수수료'] = df.loc[df.index[-2], '수수료']
            df = ror(df)
            df.loc[df.index[-1], '매수시간'] = df.index[-2]
            df.loc[df.index[-1], 'uuid'] = 'empty'
            pass
        elif my_order['state'] == 'cancle':  # 매수 취소 시
            print(f'{datetime.datetime.now().strftime("%H:%M:%S")} - 매수 취소(state == cancle) | ', my_order)
            df.loc[df.index[-1], '보유여부'] = False
            df.loc[df.index[-1], 'uuid'] = 'empty'
            pass
    return df
def order_sell(ticker,df,tick):
    stock = df.loc[df.index[-1], '매수수량']
    close = pyupbit.get_current_price('KRW-'+ticker)
    sell_price = hoga.hogaPriceReturn(close,tick,'업비트')
    order_sell=upbit.sell_limit_order('KRW-'+ticker, sell_price, stock)  # 500원에 리플20개 매도
    uuid = order_sell['uuid']
    print(f'{datetime.datetime.now().strftime("%H:%M:%S")} - 매도주문',uuid)
    return uuid,sell_price

def order_buy(ticker,tick):
    close = pyupbit.get_current_price('KRW-'+ticker)
    buy_price = hoga.hogaPriceReturn(close,tick,'업비트')
    vol = round(bet*(1-commission)/buy_price,8)
    order_buy=upbit.buy_limit_order('KRW-'+ticker, buy_price, vol)  # 500원에 리플20개 매수
    uuid = order_buy['uuid']
    print(f'{datetime.datetime.now().strftime("%H:%M:%S")} - 매수주문',uuid)
    return uuid,buy_price,vol
def ror(df):
    close = df.loc[df.index[-1], 'close']
    price = df.loc[df.index[-1], '매수가']
    volume = df.loc[df.index[-1], '매수수량']
    paid_fee = df.loc[df.index[-1], '수수료']
    sell_fee = close * volume * commission
    df.loc[df.index[-1], '수익률'] = round((close - price) / price, 3) * 100 - 0.05
    df.loc[df.index[-1], '수익금'] = round((close * volume) - (price * volume) - paid_fee - sell_fee)
    df.loc[df.index[-1], '단순보유수익률'] = round((close - (df.loc[df.index[0], 'close'])) / price, 3) * 100 - 0.05
    return df
def evaluated():
    # print('잔고확인')
    balances = upbit.get_balances()
    for i, bal in enumerate(balances):
        time.sleep(0.2)
        if bal.get('avg_buy_price') == '0':  # 거래되지않는 화폐 건너뛰기
            del balances[i]
    value = 0
    for i, bal in enumerate(balances):
        time.sleep(0.2)
        ticker = bal.get('currency')
        unit = bal.get('unit_currency')
        stock = float(bal.get('balance'))
        # print(unit+'-'+ticker)
        if bal.get('avg_buy_price') == '0':  # 거래되지않는 화폐 건너뛰기
            continue
        current = pyupbit.get_current_price(unit + '-' + ticker)
        # print(type(current))
        # print(type(stock))
        value = current * stock + value
    date = int(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
    cash = round(upbit.get_balance(ticker="KRW"))
    bought = round(upbit.get_amount('ALL'))
    # evalue = evaluated()
    wallet = {'총보유자산':0,'보유현금':0,'매수금액':0,'총평가자산':0,'평가손익':0,'수익률':0 }
    wallet['총보유자산'] = round(cash+value)
    wallet['보유현금'] = cash
    wallet['매수금액'] = bought
    wallet['총평가자산'] = round(value)
    wallet['평가손익'] = round(bought-value)
    wallet['수익률'] = round((value/bought)*100,1)
    df = pd.DataFrame(wallet,index=[date])
    return df
def init_db():
    if not os.path.isfile(db_path):#실행 중 에러가 났을 경우 다시 시작 했을 때 기존 주문데이터를 갖고오기 위해
        #잔고조회
        con = sqlite3.connect(db_path)
        df = evaluated()
        df.to_sql('잔고조회',con,if_exists='replace')
        print('초기db생성 중...')
        tickers = pyupbit.get_tickers(fiat='KRW')
        # tickers = ['KRW-BTC']
        # if True:
        #     ticker = 'KRW-BTC'
        for ticker in tickers:
            df = pyupbit.get_ohlcv(ticker, interval=interval, count=100)
            df.index = df.index.strftime("%Y%m%d%H%M%S").astype(np.int64)
            df['now'] = int(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
            df['ma20'] = round(ta.MA(df['close'], timeperiod=20))
            df['ma60'] = round(ta.MA(df['close'], timeperiod=60))
            df['rsi'] = round(ta.RSI(df['close'], timeperiod=14))
            df['매매신호'] = int(0)
            df['손절신호'] = int(0)
            df['보유여부'] = int(0)
            df['매수가'] = float(0)
            df['매도가'] = float(0)
            df['매수수량'] = float(0)
            df['매수금액'] = float(0)
            df['매도금액'] = float(0)
            df['수익률'] = float(0)
            df['수익금'] = float(0)
            df['단순보유수익률'] = float(0)
            df['수수료'] = float(0)
            df['매수시간'] = int(0)
            df['매도시간'] = int(0)
            df['보유시간'] = int(0)
            df['uuid'] = 'empty'
            df=df.drop([df.index[-1]]) #마지막 행은 현재 만들어지고 있는거기 때문에 제거
            ticker = str(ticker[4:])
            df.to_sql(ticker, con,if_exists='replace')
            time.sleep(0.2)
        con.commit()
        con.close()
        print('초기db생성 완료')
def update_tickers(table_list,tickers,con,cur):
    print('ticker 업데이트')
    new_tickers = list(set(tickers) - set(table_list))
    old_tickers = list(set(table_list) - set(tickers))
    if new_tickers:
        for new_ticker in new_tickers:
            print('new_ticker:',new_ticker)
            df = pyupbit.get_ohlcv(new_ticker, interval=interval, count=100)
            df.index = df.index.strftime("%Y%m%d%H%M%S").astype(np.int64)
            df['now'] = int(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
            df['ma20'] = round(ta.MA(df['close'], timeperiod=20))
            df['ma60'] = round(ta.MA(df['close'], timeperiod=60))
            df['rsi'] = round(ta.RSI(df['close'], timeperiod=14))
            df['매매신호'] = int(0)
            df['손절신호'] = int(0)
            df['보유여부'] = int(0)
            df['매수가'] = float(0)
            df['매도가'] = float(0)
            df['매수수량'] = float(0)
            df['매수금액'] = float(0)
            df['매도금액'] = float(0)
            df['수익률'] = float(0)
            df['수익금'] = float(0)
            df['단순보유수익률'] = float(0)
            df['수수료'] = float(0)
            df['매수시간'] = int(0)
            df['매도시간'] = int(0)
            df['보유시간'] = int(0)
            df['uuid'] = 'empty'
            df = df.drop([df.index[-1]])  # 마지막 행은 현재 만들어지고 있는거기 때문에 제거
            new_ticker = str(new_ticker[4:])
            df.to_sql(new_ticker, con, if_exists='replace')
            con.commit()
            con.close()
            time.sleep(0.2)
    if old_tickers:
        for old_ticker in old_tickers:
            con.execute(f"DROP TABLE '{old_ticker}")
            print(f'{old_ticker}: 삭제')
            con.commit()
            con.close()
    return
if __name__ == '__main__':
    access_key = "i01OXZPmiL17IDgZPcY3typLsb0XVg0PgTxo52Ht"
    secret_key = "gtKrxcdxHO5mQh5FrAuIjH1ZA2kG4TGuxqmDi9bn"
    upbit = pyupbit.Upbit(access_key, secret_key)
    db_path = 'upbit.db'
    bet = 6000
    commission = 0.0005
    buy_hoga = -2
    sell_hoga = 2
    buy_limit = 7
    sell_limit = 3
    interval = 'minute3'
    divi_m = int(str(interval[6:]))
    init_db() #계산을 위해 초기에만 처음 필요한 데이터
    # tickers = pyupbit.get_tickers(fiat='KRW')

    while True:
    #     now = int(datetime.datetime.now().strftime('%M')) #현재시간의 분을 숫자로 반환
    #     # print(now)
    #     if (now % divi_m) == 0:
    #         run()
    #         while True:
    #             if now != int(datetime.datetime.now().strftime('%M')): #현재시간과 전 시간이 다르면 탈출 한번만 실행하기위해
    #                 break
        run()
    # make_df()