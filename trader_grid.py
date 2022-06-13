import time
import datetime
import pandas as pd
pd.set_option('display.max_columns',None)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width',1200)
pd.set_option("display.unicode.east_asian_width", True)
import pyupbit
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
    record_evalue(con)
    for i,ticker in enumerate(table_list):
        time.sleep(0.1)
        df_db = pd.read_sql(f"SELECT * FROM '{ticker}'", con).set_index('index')
        df_add = pyupbit.get_ohlcv('KRW-'+ticker, interval=interval, count=5)
        if df_add.empty: #서버점검일 경우
            print('데이터 불러올 수 없음 (서버점검 확인 요망)')
            time.sleep(60)
            continue
        df_add.index = df_add.index.strftime("%Y%m%d%H%M").astype(np.int64)
        df_add = df_add.drop([df_add.index[-1]]) #마지막 행은 현재 만들어지고 있는거기 때문에 제거

        list_index = list(set(df_add.index.tolist())-set(df_db.index.tolist())) #새로받은 인덱스랑 기존인덱스 비교
        if list_index: #차집합으로 인덱스 추가되면
            # df_sum = pd.concat([df_db,df_add]) #df합치기
            # duplicateRowsDF = df_sum[df_sum.index.duplicated()] #중복되는인덱스의 데이터 추출
            # if not df_sum.index.is_unique: #인덱스가 고유하지 않을 경우(중복되는 인덱스가 있을 경우)
            #     df_add.drop(duplicateRowsDF.index,inplace=True) #중복되는 행의 인덱스 반환 후 삭제
            #     # df_db = df_db.loc[~df_db.index.duplicated(keep='last')] #인덱스가 중복인 행은 마지막꺼 살리고 제거
            df_add = df_add[-len(list_index):]
            df_add = make_df(ticker,df_db,df_add)
            df_add['now'] = int(datetime.datetime.now().strftime("%Y%m%d%H%M"))
            df_add.to_sql(ticker, con, if_exists='append')
    con.commit()
    con.close()
def make_df(ticker,df,df_add):
    add_lenth = len(df_add.index)
    for i in range (add_lenth):
        df = pd.concat([df,df_add.iloc[[i]]],axis=0)
        df.loc[df.index[-1], '보유여부'] = df.loc[df.index[-2], '보유여부']
        df.loc[df.index[-1], 'uuid'] = df.loc[df.index[-2], 'uuid']
        df.loc[df.index[-1], '총매수'] = df.loc[df.index[-2], '총매수']
        df.loc[df.index[-1], '보유수량'] = df.loc[df.index[-2], '보유수량']
        df.loc[df.index[-1], '매수금액'] = df.loc[df.index[-2], '매수금액']
        df.loc[df.index[-1], '수수료'] = df.loc[df.index[-2], '수수료']
        df.loc[df.index[-1], '매수횟수'] = df.loc[df.index[-2], '매수횟수']
        df.loc[df.index[-1], '수익률'] = df.loc[df.index[-2], '수익률']

        df.loc[df.index[-1], '최고수익률'] = df.loc[df.index[-2], '최고수익률']

        df = stg(df)
        signal = df.loc[df.index[-1], '매매신호']
        uuid = df.loc[df.index[-1], 'uuid']
        loss_cut = df.loc[df.index[-1], '손절신호']
        had = df.loc[df.index[-1], '보유여부']
        print(f'{datetime.datetime.now().strftime("%m.%d %H:%M:%S")} {ticker} - (인덱스 생성 {i+1} of {add_lenth}) ',end=' | ')

        if uuid =='empty': # 기존 주문 없음
            if signal == True or signal > 0: #매수신호 발생
                print(f'{datetime.datetime.now().strftime("%H:%M:%S")} - ',end=', ')
                df=order_buy(df,ticker)
            elif signal == False or signal < 0 : #매도신호 발생
                print(f'{datetime.datetime.now().strftime("%H:%M:%S")} - ',end=', ')
                if had == True:
                    df=order_sell(df,ticker)
                else:
                    print('매도신호에러 (보유하지 않음)')
            elif np.isnan(signal): # 신호 없음
                print(f'{datetime.datetime.now().strftime("%H:%M:%S")} - 신호 없음',end=', ')
            else :
                print('신호 없음')
        elif uuid != 'empty' and str == type(uuid):  # 기존 주문 있음
            df.loc[df.index[-1], '매수호가'] = df.loc[df.index[-2], '매수호가']
            df.loc[df.index[-1], '매도호가'] = df.loc[df.index[-2], '매도호가']
            df = check_order(df,ticker,uuid)
        else:
            print('* 이상감지_uuid 확인 *')

        if had == True:
            ror(df)
            총매수 = int(df.loc[df.index[-1], '총매수'])
            매수횟수 = int(df.loc[df.index[-1], '매수횟수'])
            수익률 = round(df.loc[df.index[-1], '수익률'],2)
            평가손익 = int(df.loc[df.index[-1], '평가손익'])
            print(f'매수금액: {총매수}, 매수횟수: {매수횟수}, 수익률: {수익률}, 평가손익: {평가손익}')
        else:
            print('보유 없음')

    df_add = df[-add_lenth:] #입력받은 df_add만 계산 후 다시 반환
    return df_add

def stg(df):
    # print(stg)
    df['ma20'] = round(ta.MA(df['close'], timeperiod=20))
    df['ma60'] = round(ta.MA(df['close'], timeperiod=60))
    df['rsi'] = round(ta.RSI(df['close'], timeperiod=14))
    df['고저평균대비등락율'] = ((df['close'] / ((df['high'] + df['low']) / 2) - 1) * 100).round(2)
    if df.loc[df.index[-1], '매수횟수'] == 0:
        df.loc[(df.rsi < 30) & (df.고저평균대비등락율 <= -0.2), '매매신호'] = True  # 매수 신호
        df.loc[(df.수익률 > 0.7) & (df.수익률 > df.최고수익률*0.8),'매매신호'] = False  # 매도 신호
        # df.loc[(df.수익률 > 0.7),'매매신호'] = False  # 매도 신호
        df.loc[(df.수익률 < -80 ), '손절신호'] = True  # 손절 신호
    elif df.loc[df.index[-1], '매수횟수'] == 1:
        df.loc[(df.rsi < 30) & (df.고저평균대비등락율 <= -0.2) & (df.수익률 < -0.2), '매매신호'] = True  # 매수 신호
        df.loc[(df.수익률 > 0.7) & (df.수익률 < df.최고수익률*0.8),'매매신호'] = False  # 매도 신호
    elif df.loc[df.index[-1], '매수횟수'] == 2:
        df.loc[(df.rsi < 30) & (df.고저평균대비등락율 <= -0.2) & (df.수익률 < -0.5), '매매신호'] = True  # 매수 신호
        df.loc[(df.수익률 > 0.7) & (df.수익률 < df.최고수익률*0.8),'매매신호'] = False  # 매도 신호
        # df.loc[(df.수익률 > 0.7),'매매신호'] = False  # 매도 신호
    elif df.loc[df.index[-1], '매수횟수'] == 3:
        df.loc[(df.rsi < 30) & (df.고저평균대비등락율 <= -0.2) & (df.수익률 < -1), '매매신호'] = True  # 매수 신호
        df.loc[(df.수익률 > 0.7) & (df.수익률 < df.최고수익률*0.8),'매매신호'] = False  # 매도 신호
        # df.loc[(df.수익률 > 0.7),'매매신호'] = False  # 매도 신호
    elif df.loc[df.index[-1], '매수횟수'] == 4:
        df.loc[(df.rsi < 30) & (df.고저평균대비등락율 <= -0.2) & (df.수익률 < -2), '매매신호'] = True  # 매수 신호
        df.loc[(df.수익률 > 0.7) & (df.수익률 < df.최고수익률*0.8),'매매신호'] = False  # 매도 신호
        # df.loc[(df.수익률 > 0.7),'매매신호'] = False  # 매도 신호
    elif df.loc[df.index[-1], '매수횟수'] > 5:
        pass
    return df

def order_buy(df,ticker):
    buy_count = df.loc[df.index[-1], '매수횟수']
    df_evalue = evaluated()
    wallet = df_evalue.loc[df_evalue.index[-1], '보유현금']
    if buy_count == False: #처음 매수 시
        print('처음매수')
        bet = wallet/money_division
    elif buy_count > 0:
        print(f'{buy_count+1}회 물타기',end=' ')
        bet = df.loc[df.index[-1], '매수금액'] * 1.5
    else:
        print('매수 에러')
        return df

    if bet < wallet and bet < 5010: #매수금액이 보유현금보다는 작고 최소주문금액 보다 작을 경우
        if wallet >= 5010:
            bet = 5010
        else:
            print(f'*주문할 수 없음1 - 보유현금:{wallet}, 배팅금액: {bet}')
            return df
    elif bet > wallet > 5010: # 매수금액이 보유현금을 초과
        bet = wallet * 0.99
        if bet >= 5010:
            pass
        else:
            print(f'*주문할 수 없음2 - 보유현금:{wallet}, 배팅금액: {bet}')
            return df
    elif wallet < 5010: # 보유현금이 최소주문 금액보다 작을 경우
        print(f'*주문할 수 없음3 - 보유현금:{wallet}, 배팅금액: {bet}')
        return df


    close = pyupbit.get_current_price('KRW-'+ticker) #현재가 조회
    buy_price = hoga.hogaPriceReturn(close,buy_hoga,'업비트') #매수호가 계산
    volume = round(bet*(1-commission)/buy_price,8)
    order_b = upbit.buy_limit_order('KRW-'+ticker, buy_price, volume)  # 500원에 리플20개 매수
    uuid = order_b['uuid']
    print(f'매수주문 -> [현재가: {close}, '
          f'매수호가{buy_hoga}, 매수가: {buy_price}, 매수수량: {volume}], 매수금액{round(buy_price * volume)}\n{uuid}')
    df.loc[df.index[-1], '현재가'] = close
    df.loc[df.index[-1], '매수호가'] = buy_price
    df.loc[df.index[-1], '매수금액'] = round(float(order_b['locked'])) #주문과 동시에 체결되면 에러날 수 있을 것 같음
    df.loc[df.index[-1], 'uuid'] = uuid

    return df


def order_sell(df,ticker):
    volume = df.loc[df.index[-1], '보유수량']
    close = pyupbit.get_current_price('KRW-'+ticker)
    sell_price = hoga.hogaPriceReturn(close,sell_hoga,'업비트')
    order_s=upbit.sell_limit_order('KRW-'+ticker, sell_price, volume)  # 500원에 리플20개 매도
    uuid = order_s['uuid']
    df.loc[df.index[-1], '현재가'] = close
    df.loc[df.index[-1], '매도호가'] = sell_price
    df.loc[df.index[-1], 'uuid'] = uuid
    print(f'매도주문 -> [현재가{close}, '
          f'매도호가: {sell_hoga}, 매도가: {sell_price}, 매도수량: {volume}], 매도금액{round(sell_price*volume)}\n{uuid}')
    print(f'{datetime.datetime.now().strftime("%H:%M:%S")} - 매도 ',end=', ')
    return df

def check_order(df,ticker,uuid):
    my_order = upbit.get_order(ticker_or_uuid=uuid)
    # print(my_order)
    if my_order['state'] == 'done':  # 주문 체결 시
        if my_order['side'] == 'bid':  # 매수 완료
            print(f'{datetime.datetime.now().strftime("%H:%M:%S")} - 매수체결 | ', my_order)
            df.loc[df.index[-1], '보유여부'] = True
            df.loc[df.index[-1], '매수시간'] = int(datetime.datetime.now().strftime("%Y%m%d%H%M"))
            df.loc[df.index[-1], 'uuid'] = 'empty'
            df.loc[df.index[-1], '총매수'] = df.loc[df.index[-1], '총매수'] + round(float(my_order['trades'][0]['funds']))
            df.loc[df.index[-1], '보유수량'] = df.loc[df.index[-1], '보유수량'] + float(my_order['volume'])
            df.loc[df.index[-1], '수수료'] = df.loc[df.index[-1], '수수료'] + round(float(my_order['paid_fee']))
            df.loc[df.index[-1], '매수횟수'] = df.loc[df.index[-1], '매수횟수'] + 1
        elif my_order['side'] == 'ask':  # 매도 완료
            print(f'{datetime.datetime.now().strftime("%H:%M:%S")} - 매도체결 | ', my_order)
            amount = df.loc[df.index[-1], '총매수']
            sell_price = df.loc[df.index[-1], '매도호가']
            volume = df.loc[df.index[-1], '보유수량']
            evalue = round(sell_price * volume)
            df.loc[df.index[-1], '총평가'] = evalue
            sell_fee = round(float(my_order['paid_fee']))
            df.loc[df.index[-1], '수익률'] = round((evalue - amount) / amount, 3) * 100 - 0.05
            df.loc[df.index[-1], '평가손익'] = round(evalue - amount - sell_fee)
            df.loc[df.index[-1], '수수료'] = df.loc[df.index[-1], '수수료'] + sell_fee
            df.loc[df.index[-1], '보유여부'] = False
            df.loc[df.index[-1], '보유수량'] = 0
            df.loc[df.index[-1], '총매수'] = 0
            df.loc[df.index[-1], '매수횟수'] = 0
            df.loc[df.index[-1], '최고수익률'] = 0
            df.loc[df.index[-1], '평가손익'] = evalue - amount
            df.loc[df.index[-1], '매도시간'] = int(datetime.datetime.now().strftime("%Y%m%d%H%M"))
            df.loc[df.index[-1], 'uuid'] = 'empty'

    elif my_order['state'] == 'wait':  # 주문 미 체결 시
        # 중복주문 확인
        if my_order['side'] == 'bid' and df.loc[df.index[-1], '매매신호'] == True: #미체결 매수 - 현재 매수
            print(f'{ticker} - 매수취소: 중복 추가 매수신호 발생 |',upbit.cancel_order(uuid))
            df.loc[df.index[-1], 'uuid'] = 'empty'
            order_buy(df,ticker)
        elif my_order['side'] == 'bid' and df.loc[df.index[-1], '매매신호'] == False: #미체결 매수 - 현재 매도
            print(f'{ticker} - 매수취소: 매도신호 발생 |',upbit.cancel_order(uuid))
            df.loc[df.index[-1], 'uuid'] = 'empty'
        elif my_order['side'] == 'ask' and df.loc[df.index[-1], '매매신호'] == True: #미체결 매도 - 현재 매수
            print(f'{ticker} - 매도취소: 매도신호 발생 |',upbit.cancel_order(uuid))
            df.loc[df.index[-1], 'uuid'] = 'empty'
        elif my_order['side'] == 'ask' and df.loc[df.index[-1], '매매신호'] == False: #미체결 매도 - 현재 매도
            print(f'{ticker} - 매도취소: 중복 추가 매도신호 발생 |',upbit.cancel_order(uuid))
            df.loc[df.index[-1], 'uuid'] = 'empty'
            order_sell(df,ticker)
        elif my_order['side'] == 'bid' and my_order['state'] == 'wait':  # 매수 미 체결 시
            df.loc[df.index[-1], '매매신호'] = df.loc[df.index[-2], '매매신호'] + 1
            signal_num =df.loc[df.index[-1], '매매신호']
            print(f'{datetime.datetime.now().strftime("%H:%M:%S")} - 매수 미체결 {signal_num}회 동안 매수하지 못 함 |')
            if df.loc[df.index[-1], '매매신호'] == buy_limit:  # 매수호가 buy_limit 횟수만큼 안될 시 매수 취소
                print(f'{ticker} - 매수취소: {buy_limit}회 동안 매수하지 못 함 |',upbit.cancel_order(uuid))
                df.loc[df.index[-1], 'uuid'] = 'empty'
                df.loc[df.index[-1], '매수금액'] = df.loc[df.index[-buy_limit], '매수금액']
        elif my_order['side'] == 'ask' and my_order['state'] == 'wait':  # 매도 미 체결 시
            df.loc[df.index[-1], '매매신호'] = df.loc[df.index[-2], '매매신호'] - 1
            signal_num =df.loc[df.index[-1], '매매신호']
            print(f'{datetime.datetime.now().strftime("%H:%M:%S")} - 매도 미체결 {signal_num}회 동안 매도하지 못 함 |')
        elif my_order['state'] == 'cancel':  # 주문 취소 시
            print(f'{datetime.datetime.now().strftime("%H:%M:%S")} - 매도취소(state == cancel)')
            df.loc[df.index[-1], 'uuid'] = 'empty'
            print('체크이상감지')

    return df


def ror(df):
    close = df.loc[df.index[-1], 'close']
    price = df.loc[df.index[-1], '총매수']
    volume = df.loc[df.index[-1], '보유수량']
    evalue = round(close * volume) #총평가
    df.loc[df.index[-1], '총평가'] = evalue
    sell_fee = evalue * commission
    df.loc[df.index[-1], '수익률'] = round((evalue - price) / price, 3) * 100 - 0.05
    df.loc[df.index[-1], '평가손익'] = round(evalue - price - sell_fee)
    if df.loc[df.index[-1],'수익률'] >= df.loc[df.index[-2],'최고수익률']:
        df.loc[df.index[-1], '최고수익률'] = df.loc[df.index[-1], '수익률']
    else:
        df.loc[df.index[-1], '최고수익률'] = df.loc[df.index[-2], '최고수익률']
    return df
def record_evalue(con):
    try:
        df_evalue = evaluated()
        df = pd.read_sql(f"SELECT * FROM '잔고조회'", con).set_index('index')
        if df_evalue.index != df.index[-1]:
            df_evalue.to_sql('잔고조회', con, if_exists='append')
    except:
        print('record_evalue() 에러')
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
    date = int(datetime.datetime.now().strftime("%Y%m%d%H%M"))
    cash = int(upbit.get_balance(ticker="KRW"))
    bought = round(upbit.get_amount('ALL'))
    # evalue = evaluated()
    wallet = {'총보유자산':0,'보유현금':0,'매수금액':0,'총평가자산':0,'평가손익':0,'수익률':0 }
    wallet['총보유자산'] = round(cash+value)
    wallet['보유현금'] = cash
    wallet['매수금액'] = bought
    wallet['총평가자산'] = round(value)
    wallet['평가손익'] = round(value-bought)
    wallet['수익률'] = round(((value-bought)/bought)*100,2)
    df_evalue = pd.DataFrame(wallet,index=[date])
    return df_evalue
def init_db():
    if not os.path.isfile(db_path):#실행 중 에러가 났을 경우 다시 시작 했을 때 기존 주문데이터를 갖고오기 위해
        #잔고조회
        print('초기db생성 중...')
        con = sqlite3.connect(db_path)
        df_evalue = evaluated()
        df_evalue.to_sql('잔고조회',con,if_exists='replace')
        # tickers = pyupbit.get_tickers(fiat='KRW')
        # tickers = ['KRW-BTC']
        # if True:
        #     ticker = 'KRW-BTC'
        for ticker in tickers:
            df = pyupbit.get_ohlcv(ticker, interval=interval, count=100)
            df.index = df.index.strftime("%Y%m%d%H%M").astype(np.int64)
            df['now'] = int(datetime.datetime.now().strftime("%Y%m%d%H%M"))
            df['ma20'] = round(ta.MA(df['close'], timeperiod=20))
            df['ma60'] = round(ta.MA(df['close'], timeperiod=60))
            df['rsi'] = round(ta.RSI(df['close'], timeperiod=14),1)
            df['고저평균대비등락율'] = ((df['close'] / ((df['high'] + df['low']) / 2) - 1) * 100).round(2)
            df['매매신호'] = int(0)
            df['손절신호'] = int(0)
            df['보유여부'] = int(0)
            df['현재가'] = float(0)
            df['매수호가'] = float(0)
            df['매도호가'] = float(0)
            df['보유수량'] = float(0)
            df['매수금액'] = int(0)
            df['총매수'] = int(0)
            df['매수횟수'] = int(0)
            df['총평가'] = int(0)
            df['수익률'] = float(0)
            df['최고수익률'] = float(0)
            df['평가손익'] = int(0)
            df['수수료'] = int(0)
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
    else:
        print('기존 db 불러오는 중... ')
        con = sqlite3.connect(db_path)
        df_evalue = pd.read_sql(f"SELECT * FROM '잔고조회'", con).set_index('index')
    return df_evalue

def update_tickers(table_list,tickers,con,cur):
    print('ticker 업데이트')
    new_tickers = list(set(tickers) - set(table_list))
    old_tickers = list(set(table_list) - set(tickers))
    if new_tickers:
        for new_ticker in new_tickers:
            print('new_ticker:',new_ticker)
            df = pyupbit.get_ohlcv(new_ticker, interval=interval, count=100)
            df.index = df.index.strftime("%Y%m%d%H%M").astype(np.int64)
            df['now'] = int(datetime.datetime.now().strftime("%Y%m%d%H%M"))
            df['ma20'] = round(ta.MA(df['close'], timeperiod=20))
            df['ma60'] = round(ta.MA(df['close'], timeperiod=60))
            df['rsi'] = round(ta.RSI(df['close'], timeperiod=14))
            df['매매신호'] = int(0)
            df['손절신호'] = int(0)
            df['보유여부'] = int(0)
            df['매수호가'] = float(0)
            df['매도호가'] = float(0)
            df['보유수량'] = float(0)
            df['매수금액'] = float(0)
            df['매도금액'] = float(0)
            df['수익률'] = float(0)
            df['평가손익'] = float(0)
            df['수수료'] = float(0)
            df['매수시간'] = int(0)
            df['매도시간'] = int(0)
            df['보유시간'] = int(0)
            df['uuid'] = 'empty'
            df = df.drop([df.index[-1]])  # 마지막 행은 현재 만들어지고 있는거기 때문에 제거
            new_ticker = str(new_ticker[4:])
    return
if __name__ == '__main__':
    access_key = "i01OXZPmiL17IDgZPcY3typLsb0XVg0PgTxo52Ht"
    secret_key = "gtKrxcdxHO5mQh5FrAuIjH1ZA2kG4TGuxqmDi9bn"
    upbit = pyupbit.Upbit(access_key, secret_key)
    db_path = 'D:/db_files/trade_upbit_grid.db'
    interval = 'minute3'

    tickers = ['KRW-BTC']
    commission = 0.0005
    buy_hoga = -2
    sell_hoga = 2
    buy_limit = 7 # 횟수동안 미 체결 시 취소
    sell_limit = 3 # 횟수동안 미 체결 시 취소
    # divi_m = int(str(interval[6:]))
    df_evalue=init_db() #계산을 위해 초기에만 처음 필요한 데이터
    money_division = 100
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