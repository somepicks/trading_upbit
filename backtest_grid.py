import pandas as pd
import sqlite3
import numpy as np
import datetime
import time
import talib
pd.set_option('mode.chained_assignment',  None) # SettingWithCopyWarning 경고를 끈다
pd.set_option('display.max_columns',None) #모든 열을 보고자 할 때
pd.set_option('display.width',1500)
pd.set_option("display.unicode.east_asian_width", True)
def df_col(df):
    df = df[['open', 'high', 'low', 'close','rsi', '고저평균대비등락율']]
    df['매수신호'] = np.nan
    df['매수호가'] = np.nan
    df['매수체결가'] = np.nan
    df['매도신호'] = np.nan
    df['매도호가'] = np.nan
    df['매도체결가'] = np.nan
    df['매수그룹'] = np.nan
    df['매수횟수'] = np.nan
    df['보유여부'] = np.nan
    df['보유현금'] = bet
    df['매수금액'] = np.nan
    df['총매수'] = np.nan
    df['보유수량'] = np.nan
    df['총평가'] = int(0)
    df['수익률'] = np.nan
    df['최고수익률'] = np.nan
    # df['최고대비'] = np.nan
    df['수익금'] = float(0)
    df['수수료'] = int(0)
    df['매수시간'] = int(0)
    df['매도시간'] = np.nan
    df['보유시간'] = np.nan
    df['손절'] = np.nan
    df['손절가'] = np.nan
    return df
def buy_stg(df):
    # df.loc[(df.rsi < 30) & (df.ma20 > df.ma60) & (df.low<df.band_lower),'매매신호'] = True
    # df['매매신호'] = True
    df.loc[df.index ,'매수신호'] = True
    # df.loc[(df.hei_close < df.hei_open) & (df.매수신호==True) ,'매수신호'] = np.nan
    df.loc[(df.rsi>rsi) & (df.매수신호==True) ,'매수신호'] = np.nan
    df.loc[(df.고저평균대비등락율>high_ratio) & (df.매수신호==True) ,'매수신호'] = np.nan
    # df.loc[(df.hei_close < df.hei_open) & (df.매수신호==True) ,'매수신호'] = np.nan
    # df.loc[(df.rsi > 30) & (df.매수신호==True) ,'매수신호'] = np.nan

    df.loc[(df['매수신호'].shift(1)==True) , '매수호가'] = df['open'].apply(buy_hoga_return)

    df.loc[(df.매수호가>df.low) & (df['매수신호'].shift(1)==1) ,'매수체결가'] = df.매수호가

    for i in range(signal_buy-1):
        df.loc[(df['매수신호'].shift(1)==i+1) & (df.매수신호!=True) & (df.매수체결가.isnull()) ,'매수신호'] = i+2
        df.loc[(df['매수신호'].shift(1)==i+2) & (df.매수신호!=True) & (df['매수체결가'].shift(1).isnull()) ,'매수호가'] = df['매수호가'].shift(1)
        df.loc[(df.매수호가>df.low) & (df['매수신호'].shift(1)>0) ,'매수체결가'] = df.매수호가

    # df.loc[(df['매수체결가'].shift(-1) > 0) & (df.매수체결가 > 0) ,'매수체결가'] = np.nan
    # df.loc[(df['매수신호'].shift(1)==True) & (df.매수체결가.isnull()) ,'매수호가'] = df['매수체결가'].shift(1)
    # df['매수호가'].fillna(method='ffill', inplace=True)  # nan값을 윗 값으로 채움

    # df.loc[(df['매매신호'].shift(1)==True) , '손절가'] = df['매수체결가'].apply(loss_hogaPriceReturn_per)
    return df
def sell_stg(df,i):
    # df['매수대비'] = (df['close']-df['매수체결가'])/df['매수체결가']*100

    # print(df)
    # quit()
    # df.loc[(df.close > df.band_upper) & (df.rsi > 70) ,'매매신호'] = False
    # df.loc[(df.cmo_20 < df.cmo_30) & (df.hmac_5 <= df.hmao_5) ,'매매신호'] = False
    df.loc[(df.매수그룹==i)&(df['수익률']>margin) & (df['수익률'] < df['최고수익률'] * trail ) ,'매도신호'] = True

    # df.loc[(df.close < df.band_middle),'매매신호'] = False
    # df.loc[(df['매매신호'].shift(1)==True),'매매신호'] = False
    df.loc[(df.매수그룹==i)&(df['매도신호'].shift(1)==True), '매도호가'] = df['open'].apply(sell_hoga_return)
    df.loc[(df.매수그룹==i)&(df.매도호가<df.high) & (df['매도신호'].shift(1)==1) ,'매도체결가'] = df.매도호가
    # if True:
    #     return df
    cancel = True # 매도 안될 시 매도 취소
    for x in range(signal_sell):
        df.loc[(df.매수그룹==i)&(df['매도신호'].shift(1)==x+1) & (df['매도신호']>0) & (df.매도체결가.isnull()) ,'매도신호'] = x+2
        df.loc[(df.매수그룹==i)&(df['매도신호'].shift(1)==x+2) & (df['매도신호']>0) & (df['매도체결가'].shift(1).isnull()) ,'매도호가'] = df['매도호가'].shift(1)
        df.loc[(df.매수그룹==i)&(df.매도호가<df.high) & (df['매도신호'].shift(1)>0) ,'매도체결가'] = df.매도호가
        if cancel == True:
            df.loc[df['매도신호'].shift(1)==signal_sell,'매도신호'] = signal_sell+1
            df.loc[df['매도신호'].shift(1)==signal_sell,'매도체결가'] = df.low
            df.loc[df['매도신호'].shift(1)>signal_sell,'매도신호'] = np.nan
            df.loc[df['매도신호'].shift(1)>signal_sell,'매도호가'] = np.nan
            df.loc[df['매도신호'].shift(1)>signal_sell,'매도체결가'] = np.nan
    return df
# def losscut_stg(df):
#     df.loc[df['기간수익률']<loss_per,'손절'] = True
#     df.loc[df.index,'기간수익률'] = np.nan
#     df.loc[df.index,'보유여부'] = np.nan
#     df=buy_stg(df)
#     df=sell_stg(df)
#     df.loc[(df['매매신호'].shift(1) == True) & (df['low'] < df['매수체결가']) & (df['손절']!=True), '보유여부'] = True
#     df.loc[(df['매매신호'].shift(1) == False) & (df['high'] > df['매도체결가']) | (df['손절']==True), '보유여부'] = False
#
#     df['보유여부'].ffill(inplace=True) # NaN값을 윗 값으로 채움
#     df['보유여부'].fillna(False, inplace=True) # NaN값을 False로 채움
#     df.loc[(df['보유여부']==False) & (df['보유여부'].shift(1)==True)& (df['손절']==True),'매도체결가' ] = df['low']
#     df.loc[df['보유여부']==True,'기간수익률'] = round((df['close']-df['매수체결가'])/df['매수체결가']*100,1)
#     df.loc[df['보유여부'].shift(1)==False,'매도체결가' ] = np.nan
#     df.loc[(df.보유여부==True),'손절가'] = df['매수체결가']-(df['매수체결가']*abs(loss_per)*0.01)
#     return df
def df_backtest(df,ticker):
    df=buy_stg(df)
    df.loc[(df['매수신호'].shift(1) > 0) & (df.매수체결가>0), '보유여부'] = True
    df['매수체결가'].ffill(inplace=True) # NaN값을 윗 값으로 채움
    index_true = df.index[df['보유여부'] == True]  # 보유여부가 True인 인덱스만 추출
    max_ror = 0
    for i,idx in enumerate(index_true):
        df.loc[idx,'매수그룹'] = i
    df['매수그룹'].ffill(inplace=True) # NaN값을 윗 값으로 채움
    df['매수횟수'] = df['매수그룹']+1
    # print(df.index)
    list_index=df.index.to_list()
    for i, idx in enumerate(index_true):
        index_shift=df.index[list_index.index(idx)-1] #앞의 인덱스 추출
        # index_final = df.loc[(df.매수그룹==i),'매수그룹'].index[-1] #매수그룹의 마지막 인덱스 추출
        index_x = df.index[df['매수그룹'] == i]  # 매수그룹별 세부인덱스 추출
        index_final = index_x[-1]

        if df.loc[idx, '매수횟수'] == 1:
            df.loc[(df.매수그룹 == i) & (df.매수횟수==1), '매수금액'] = round(df.loc[index_shift, '보유현금']/money_division)
            df.loc[df.매수그룹 == i, '보유현금'] = df.loc[index_shift, '보유현금'] - df.loc[idx, '매수금액']
            df.loc[idx, '수수료'] = round(df.loc[idx, '매수금액'] * fee_buy * 0.01)
            df.loc[(df.매수그룹 == i) & (df.매수횟수==1), '총매수'] = df.loc[idx, '매수금액']
            df.loc[(df.매수그룹 == i) & (df.매수횟수==1), '보유수량'] = round((df.loc[idx, '매수금액']-df.loc[idx, '수수료'])/df.loc[idx, '매수체결가'], 8)
            df.loc[(df.매수그룹 == i) & (df.매수횟수==1),'총평가'] = round(df['close']*df['보유수량'])
            df.loc[(df.매수그룹 == i) & (df.매수횟수==1),'수익률'] = round(((df['총평가']-df['총매수'])/df['총매수']*100)-fee_sell,2)
            df.loc[(df.매수그룹 == i) & (df.매수횟수==1),'수익금'] = round(df['총평가']-df['총매수']-df.loc[idx, '수수료'])
            df.loc[idx,'최고수익률'] = df.loc[idx,'수익률']
            for x,idx_x in enumerate(index_x):
                # print(df.loc[index_x[x-1], '최고수익률'].isnull())
                if df.loc[idx_x, '수익률'] >= max_ror:
                    max_ror = df.loc[idx_x, '수익률']
                    df.loc[idx_x, '최고수익률'] = df.loc[idx_x, '수익률']
                elif df.loc[idx_x, '수익률'] < max_ror:
                    df.loc[idx_x, '최고수익률'] = max_ror
            # df.loc[df.매수횟수==1,'최고대비'] = (df['수익률']-df['최고수익률'])/df['최고수익률']
        elif df.loc[idx, '매수횟수'] > 1 and df.loc[index_shift,'보유현금'] > df.loc[index_shift,'매수금액']*bet_m:
            df.loc[(df.매수그룹 == i) , '매수횟수'] = df.loc[index_shift,'매수횟수']+1
            df.loc[df.매수그룹 == i, '매수금액'] = round(df.loc[index_shift, '매수금액'] * bet_m)
            df.loc[df.매수그룹 == i, '보유현금'] = df.loc[index_shift, '보유현금'] - df.loc[idx, '매수금액']
            df.loc[idx, '수수료'] = round(df.loc[idx, '매수금액'] * fee_buy * 0.01)
            df.loc[df.매수그룹 == i, '총매수'] = df.loc[idx, '매수금액']+df.loc[index_shift, '총매수']
            df.loc[df.매수그룹 == i, '보유수량'] = round((df.loc[idx, '매수금액']-df.loc[idx, '수수료'])/df.loc[idx, '매수체결가'], 8)+df.loc[index_shift, '보유수량']
            df.loc[df.매수그룹 == i,'총평가'] = round(df['close']*df['보유수량'])
            df.loc[df.매수그룹 == i,'수익률'] = round(((df['총평가']-df['총매수'])/df['총매수']*100)-fee_sell,2)
            df.loc[df.매수그룹 == i,'수익금'] = round(df['총평가']-df['총매수']-df.loc[idx, '수수료'])
            df.loc[idx,'최고수익률'] = df.loc[idx,'수익률']
            for x,idx_x in enumerate(index_x):
                # print(df.loc[index_x[x-1], '최고수익률'].isnull())
                if df.loc[idx_x, '수익률'] >= max_ror:
                    max_ror = df.loc[idx_x, '수익률']
                    df.loc[idx_x, '최고수익률'] = df.loc[idx_x, '수익률']
                elif df.loc[idx_x, '수익률'] < max_ror:
                    df.loc[idx_x, '최고수익률'] = max_ror
        elif df.loc[idx, '매수횟수'] > 1 and df.loc[index_shift,'보유현금'] <= df.loc[index_shift,'매수금액']*bet_m: #보유 현금이 부족 할 시
            df.loc[(df.매수그룹 == i) , '매수횟수'] = df.loc[index_shift,'매수횟수']
            df.loc[df.매수그룹 == i, '매수금액'] = df.loc[index_shift,'매수금액']
            df.loc[df.매수그룹 == i, '보유현금'] = df.loc[index_shift, '보유현금']
            df.loc[idx, '수수료'] = 0
            df.loc[df.매수그룹 == i, '총매수'] = df.loc[index_shift, '총매수']
            df.loc[df.매수그룹 == i, '보유수량'] = df.loc[index_shift, '보유수량']
            df.loc[df.매수그룹 == i,'총평가'] = round(df['close']*df['보유수량'])
            df.loc[df.매수그룹 == i,'수익률'] = round(((df['총평가']-df['총매수'])/df['총매수']*100),2)
            df.loc[df.매수그룹 == i,'수익금'] = round(df['총평가']-df['총매수'])
            df.loc[df.매수그룹 == i,'보유여부'] = np.nan
            df.loc[idx,'최고수익률'] = df.loc[idx,'수익률']
            for x,idx_x in enumerate(index_x):
                # print(df.loc[index_x[x-1], '최고수익률'].isnull())
                if df.loc[idx_x, '수익률'] >= max_ror:
                    max_ror = df.loc[idx_x, '수익률']
                    df.loc[idx_x, '최고수익률'] = df.loc[idx_x, '수익률']
                elif df.loc[idx_x, '수익률'] < max_ror:
                    df.loc[idx_x, '최고수익률'] = max_ror

        df = sell_stg(df,i)
        # df.loc[(df.매수그룹==i) ,'보유여부'] = df['보유여부'].ffill(inplace=True)  # NaN값을 윗 값으로 채움
        index_false = df.index[(df.매수그룹 == i) & (df.매도체결가>0)]  # 매수그룹별 세부인덱스 추출
        # index_false = (df.loc[(df.매수그룹==i) & (df.매도체결가>0),'매수그룹'])  # 매도체결가가 0 보다 큰 데이터만 추출
        if not index_false.empty: #매도 시
            index_false = index_false[0]
            num_index = list_index.index(index_false) #인덱스 리스트의 매도체결 인덱스번호 추출
            index_sold = list_index[num_index+1] #인덱스 번호 다음칸의 인덱스 추출
            df.loc[index_false,'보유여부'] = False
            sell_price = round(df.loc[index_false,'보유수량']*df.loc[index_false,'매도체결가'])
            df.loc[index_false,'수수료'] = round(sell_price*fee_sell*0.01)
            df.loc[index_false,'총평가'] = sell_price-df.loc[index_false,'수수료']
            df.loc[index_false,'수익금'] = df.loc[index_false,'총평가']-df.loc[index_false,'총매수']
            df.loc[index_false,'수익률'] = round(df.loc[index_false,'수익금']/df.loc[index_false,'총매수']*100,2)
            df.loc[index_false:index_final,'최고수익률'] = np.nan
            df.loc[index_sold:index_final,'보유현금'] = round(df.loc[index_false,'보유현금']+df.loc[index_false,'총평가'])
            df.loc[index_sold:index_final,'매수금액'] = np.nan
            df.loc[index_sold:index_final,'총매수'] = np.nan
            df.loc[index_sold:index_final,'보유수량'] = np.nan
            df.loc[index_sold:index_final,'총평가'] = np.nan
            df.loc[index_sold:index_final,'수익률'] = np.nan
            df.loc[index_sold:index_final,'수익금'] = np.nan
            df.loc[index_sold:index_final,'매도신호'] = np.nan
            df.loc[index_sold:index_final,'매도호가'] = np.nan
            df.loc[index_sold:index_final,'매도체결가'] = np.nan
            df.loc[df.매수그룹 == i+1, '매수횟수'] = 1
            max_ror = 0

        # if i==6:
        #     break

    df.loc[(df.보유여부==1),'매수시간'] = pd.Series(df.index,index=df.index)
    df.loc[(df.보유여부==0),'매도시간'] = pd.Series(df.index,index=df.index)

    df.loc[(df.보유여부==0)&(df.매수신호==1),'보유여부'] = np.nan
    df.loc[(df.보유여부==0)&(df.매수신호==1),'매도시간'] = np.nan
    # make_detail_db(df, ticker)
    wallet = 0
    make_detail_db(df,ticker)
    # quit()
    if df.loc[df.index[-1],'매수금액'] is None: #마지막행 보유 시 일괄 매도
        wallet = df.loc[df.index[-1],'보유현금']

    elif df.loc[df.index[-1],'매수금액'] is not None:         #마지막행 보유 시 일괄 매도
        commission_sell = round(df.loc[df.index[-1],'총평가']*fee_sell*0.01)
        wallet = df.loc[df.index[-1],'보유현금'] + df.loc[df.index[-1],'총평가']-commission_sell
        df.loc[df.index[-1],'매도시간'] = df.index[-1]
        df.loc[df.index[-1],'보유여부'] = False
        df.loc[df.index[-1],'매도호가'] = df.loc[df.index[-1],'close']
        df.loc[df.index[-1],'매도체결가'] = df.loc[df.index[-1],'매도호가']
        sell_price = round(df.loc[df.index[-1], '보유수량'] * df.loc[df.index[-1], '매도체결가'])
        df.loc[df.index[-1],'수수료'] = round(sell_price*fee_sell*0.01)
    df['종목명']=str(ticker[:ticker.find('-')])
    benefit =  wallet - bet
    ror = round(benefit/bet*100,2)
    maximum = round(df['수익률'].max(),2)
    minimum = round(df['수익률'].min(),2)
    commission = df['수수료'].sum()
    signal = len(df.loc[df['매수신호']==1])  #매수신호가 1인 값 추출
    lock_buy = len(df.loc[df['보유여부']==1])  #보유여부가 1인 값 추출
    lock_sell = len(df.loc[df['보유여부']==0])  #보유여부가 1인 값 추출
    origin_open = df.loc[df.index[0], 'open']
    origin_close = df.loc[df.index[-1], 'close']
    origin_ror = round((origin_close-origin_open)/origin_open*100,2)
    max_bet = round(df['총매수'].max(),2)
    max_buy = round(df['매수횟수'].max(),2)
    print(f'{ticker}-배팅배수: {bet_m}, rsi: {rsi}, 고저대비: {high_ratio}, 트레일링스탑: {trail}, 최소마진: {margin}, 수익률: {ror}, 수익금: {benefit}, 수수료: {commission}, 매수신호횟수: {signal},매수체결횟수:{lock_buy},매도체결횟수:{lock_sell}, 매수최고금액: {max_bet}, 최대매수횟수: {max_buy}, 최고수익률: {maximum}, 최저수익률: {minimum}, 단순보유수익률: {origin_ror} ')
    dict_result = {'ticker':[ticker],'배팅배수':[bet_m],'rsi':[rsi],'고저대비':[high_ratio],'트레일링스탑':[trail],'최소마진':[margin],'수익률':[ror],'수익금':[benefit],'수수료':[commission],'매수신호횟수':[signal],'매수체결횟수':[lock_buy],'매도체결횟수':[lock_sell],'매수최고금액':[max_bet],'최대매수횟수':[max_buy],'최고수익률':[maximum],'최저수익률':[minimum]}
    dt_now = str(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
    df_result = pd.DataFrame(dict_result, index=[dt_now])
    df.dropna(subset=['보유여부'],axis=0,inplace=True) #보유여부가 nan인 행을 찾아 삭제
    # quit()
    df['매도시간'].fillna(method='bfill',inplace=True) #바로 밑 데이터로 채움
    df.loc[df.index!=df.매도시간,'수익금'] = 0 # 손절없이 물타기 때문에 수익금만 남김
    # df.drop(df[df['보유여부']==False].index,inplace=True) #보유여부가 False인 행을 찾아서 삭제
    df.loc[df.매수시간==0,'매수시간'] = df['매수시간'].shift(1)
    # make_detail_db(df, ticker)

    df=df[['종목명','매수시간','매도시간','매수체결가','매도체결가','손절','손절가','수익률','수익금','수수료']]
    return df,df_result

def make_back_db(df,df_result,ticker):
    ror = df['수익률'].mean()
    plus=df[df['수익률'] > 0]
    minus=df[df['수익률'] < 0]
    benefit = df['수익금'].sum()
    df['interval'] = interval
    df['수익금합계']=df['수익금'].cumsum()
    df['매수시간'] = df['매수시간'].astype(str).str[0:14]
    df['매도시간'] = df['매도시간'].astype(str).str[0:14]
    df['매도체결가'].fillna(method='bfill',inplace=True) #바로 밑 데이터로 채움
    df['매수체결가'] = df['매수체결가'].astype(str)
    df['매도체결가'] = df['매도체결가'].astype(str)
    df['수익률'] = df['수익률'].astype(str)
    df.rename(columns={'매수체결가': '매수가'}, inplace=True)
    df.rename(columns={'매도체결가': '매도가'}, inplace=True)
    df['매수시간_dt'] = pd.to_datetime(df['매수시간'], format='%Y%m%d%H%M%S') #int형을 datetime으로 변환
    df['매도시간_dt'] = pd.to_datetime(df['매도시간'], format='%Y%m%d%H%M%S') #int형을 datetime으로 변환
    df['보유시간']=df['매도시간_dt']-df['매수시간_dt']
    had_time = df['보유시간'].mean()
    df['매수시간_dt']=df['매수시간_dt'].astype(str)
    df['매도시간_dt']=df['매도시간_dt'].astype(str)
    df['보유시간']=df['보유시간'].astype(str)
    # print(df)
    # df = df[df.duplicated(subset=['매수시간', '매도시간'], keep=False)]
    con = sqlite3.connect(db_back)
    dt_now = str(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
    table = 'coins_vj_' + dt_now
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

def make_opt_db(df_result,ticker):
    df_result.rename(index={df_result.index[0]:index_num},inplace=True) #인덱스 이름 바꾸기
    back_grid_con = sqlite3.connect(db_optimization)
    df_result.to_sql('coins_vc_' + ticker + '_grid2', back_grid_con, if_exists='append')
    back_grid_con.commit()
    back_grid_con.close()

def make_detail_db(df,ticker):
    con = sqlite3.connect(db_back_detail)
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
    df['hmao_20'] = df['hei_open'].rolling(window=5).mean().round(3)
    df['hmao_30'] = df['hei_open'].rolling(window=10).mean().round(3)
    df['hmac_20'] = df['hei_close'].rolling(window=5).mean().round(3)
    df['hmac_30'] = df['hei_close'].rolling(window=10).mean().round(3)
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

if __name__ == '__main__':
    db_path = 'D:/db_files/'
    db_ohlcv = db_path + 'upbit_ohlcv.db'
    db_back = db_path + 'upbit_backtest.db'
    db_back_detail = db_path + 'upbit_backtest_grid_detail.db'
    db_optimization = db_path + 'upbit_backtest_grid_최적화.db'
    index_num = 0



    buy_hoga = -1 #매수호가
    sell_hoga = 1 #매도호가

    interval = 'minute3'
    bet = 1000000 #최초 배팅금액
    signal_buy = 5 #매수신호 시 상한 횟수
    signal_sell = 3 #매도신호 시 상한 횟수
    money_division = 100
    fee_buy = 0.05 # %
    fee_sell = 0.05 # %
    loss_per = -50
    optimization = None

    if optimization == True:
        bet_multiple = [1.2]
        rsis = [40]
        high_ratios = [-0.15]
        trailings = [0.8]
        margins = [0.3,0.5,0.7,0.9,1.2,1.5] #매도 수익률
    else:
        bet_multiple = [1.2]
        rsis = [40]
        high_ratios = [-0.15]
        trailings = [0.8]
        margins = [0.5]


    df_amount = pd.DataFrame()
    get_con = sqlite3.connect(db_ohlcv)
    cur = get_con.cursor()
    # tickers= get_ticker_list(cur,interval)
    # print(tickers)
    tickers =['BTC-'+interval]
    for ticker in tickers:
        start = time.time()
        df_ohlcv = pd.read_sql(f"SELECT * FROM '{ticker}'", get_con).set_index('index')
        df_ohlcv = df_col(df_ohlcv)
        # df = df_add(df)
        # df = df.iloc[1640:]
        for bet_m in bet_multiple:
            for margin in margins:
                for rsi in rsis:
                    for high_ratio in high_ratios:
                        for trail in trailings:
                            df_back,df_result = df_backtest(df_ohlcv,ticker)
                            if optimization == True:
                                make_opt_db(df_result,ticker)
                                index_num = index_num+1
                            elif optimization == False:
                                make_back_db(df_back, df_result, ticker)
        get_con.close()

    # df_result = make_back_db(df_amount)
    # print(df_result)
