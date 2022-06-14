import pandas as pd
import sqlite3
import numpy as np
import datetime
import time
pd.set_option('mode.chained_assignment',  None) # SettingWithCopyWarning 경고를 끈다
pd.set_option('display.max_columns',None) #모든 열을 보고자 할 때
pd.set_option('display.width',1500)
pd.set_option("display.unicode.east_asian_width", True)

def buy_stg(df):
    # df.loc[(df.rsi < 30) & (df.ma20 > df.ma60) & (df.low<df.band_lower),'매매신호'] = True
    # df['매매신호'] = True
    df.loc[df.index ,'매수신호'] = True
    # df.loc[(df.hei_close < df.hei_open) & (df.매수신호==True) ,'매수신호'] = np.nan
    df.loc[(df.rsi>30) & (df.매수신호==True) ,'매수신호'] = np.nan
    df.loc[(df.고저평균대비등락율>-0.2) & (df.매수신호==True) ,'매수신호'] = np.nan
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

    # df.loc[(df['매매신호'].shift(1)==True) , '손절가'] = df['매수가'].apply(loss_hogaPriceReturn_per)
    return df
def sell_stg(df,i):
    # df['매수대비'] = (df['close']-df['매수가'])/df['매수가']*100

    # print(df)
    # quit()
    # df.loc[(df.close > df.band_upper) & (df.rsi > 70) ,'매매신호'] = False
    # df.loc[(df.cmo_20 < df.cmo_30) & (df.hmac_5 <= df.hmao_5) ,'매매신호'] = False
    df.loc[(df.매수그룹==i)&(df['수익률']>0.7) & (df['수익률'] < df['최고수익률'] * trail ) ,'매도신호'] = True

    # df.loc[(df.close < df.band_middle),'매매신호'] = False
    # df.loc[(df['매매신호'].shift(1)==True),'매매신호'] = False
    df.loc[(df.매수그룹==i)&(df['매도신호'].shift(1)==True), '매도호가'] = df['open'].apply(sell_hoga_return)
    df.loc[(df.매수그룹==i)&(df.매도호가<df.high) & (df['매도신호'].shift(1)==1) ,'매도체결가'] = df.매도호가
    # if True:
    #     return df
    cancel = True
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

def df_back(df,ticker):
    df = df[['open', 'high', 'low', 'close','rsi', '고저평균대비등락율',]]
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
    df['평가손익'] = float(0)
    df['수수료'] = int(0)
    df['매수시간'] = int(0)
    df['매도시간'] = int(0)
    df['보유시간'] = int(0)

    df = df.iloc[315:]
    length = len(df.index)
    ing_before=0
    df=buy_stg(df)
    df.loc[(df['매수신호'].shift(1) > 0) & (df.매수체결가>0), '보유여부'] = True
    df['매수체결가'].ffill(inplace=True) # NaN값을 윗 값으로 채움
    index = df.index[df['보유여부'] == True]  # 보유여부가 True인 인덱스만 추출
    max_ror = 0
    # print(idx)
    for i,idx in enumerate(index):
        df.loc[idx,'매수그룹'] = i
    df['매수그룹'].ffill(inplace=True) # NaN값을 윗 값으로 채움
    df['매수횟수'] = df['매수그룹']+1
    # print(df.index)
    list_index=df.index.to_list()
    for i, idx in enumerate(index):
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
            df.loc[(df.매수그룹 == i) & (df.매수횟수==1),'평가손익'] = round(df['총평가']-df['총매수']-df.loc[idx, '수수료'])
            df.loc[idx,'최고수익률'] = df.loc[idx,'수익률']
            for x,idx_x in enumerate(index_x):
                # print(df.loc[index_x[x-1], '최고수익률'].isnull())
                if df.loc[idx_x, '수익률'] >= max_ror:
                    max_ror = df.loc[idx_x, '수익률']
                    df.loc[idx_x, '최고수익률'] = df.loc[idx_x, '수익률']
                elif df.loc[idx_x, '수익률'] < max_ror:
                    df.loc[idx_x, '최고수익률'] = max_ror
            # df.loc[df.매수횟수==1,'최고대비'] = (df['수익률']-df['최고수익률'])/df['최고수익률']
        elif df.loc[idx, '매수횟수'] > 1:
            df.loc[(df.매수그룹 == i) , '매수횟수'] = df.loc[index_shift,'매수횟수']+1
            df.loc[df.매수그룹 == i, '매수금액'] = round(df.loc[index_shift, '매수금액']*bet_muliple)
            df.loc[df.매수그룹 == i, '보유현금'] = df.loc[index_shift, '보유현금'] - df.loc[idx, '매수금액']
            df.loc[idx, '수수료'] = round(df.loc[idx, '매수금액'] * fee_buy * 0.01)
            df.loc[df.매수그룹 == i, '총매수'] = df.loc[idx, '매수금액']+df.loc[index_shift, '총매수']
            df.loc[df.매수그룹 == i, '보유수량'] = round((df.loc[idx, '매수금액']-df.loc[idx, '수수료'])/df.loc[idx, '매수체결가'], 8)+df.loc[index[i-1], '보유수량']
            df.loc[df.매수그룹 == i,'총평가'] = round(df['close']*df['보유수량'])
            df.loc[df.매수그룹 == i,'수익률'] = round(((df['총평가']-df['총매수'])/df['총매수']*100)-fee_sell,2)
            df.loc[df.매수그룹 == i,'평가손익'] = round(df['총평가']-df['총매수']-df.loc[idx, '수수료'])
            df.loc[idx,'최고수익률'] = df.loc[idx,'수익률']
            for x,idx_x in enumerate(index_x):
                # print(df.loc[index_x[x-1], '최고수익률'].isnull())
                if df.loc[idx_x, '수익률'] >= max_ror:
                    max_ror = df.loc[idx_x, '수익률']
                    df.loc[idx_x, '최고수익률'] = df.loc[idx_x, '수익률']
                elif df.loc[idx_x, '수익률'] < max_ror:
                    df.loc[idx_x, '최고수익률'] = max_ror
        df = sell_stg(df,i)
        # df.loc[(df.매수그룹==i) & (df.매도체결가>0),'보유여부'] = False
        # df.loc[(df.매수그룹==i) ,'보유여부'] = df['보유여부'].ffill(inplace=True)  # NaN값을 윗 값으로 채움
        # df['보유여부'].ffill(inplace=True)  # NaN값을 윗 값으로 채움
        index_false = df.index[(df.매수그룹 == i) & (df.매도체결가>0)]  # 매수그룹별 세부인덱스 추출
        # index_false = (df.loc[(df.매수그룹==i) & (df.매도체결가>0),'매수그룹'])  # 매도체결가가 0 보다 큰 데이터만 추출
        # print(index_df)
        # index_final = index_df.index[-1]
        # print(index_false)
        # print(index_final)
        if not index_false.empty: #매도 시
            index_false = index_false[0]
            num_index = list_index.index(index_false) #인덱스 리스트의 매도체결 인덱스번호 추출
            index_sold = list_index[num_index+1] #인덱스 번호 다음칸의 인덱스 추출
            # print(index_false)
            # print(index_sold)
            # print(index_final)
            df.loc[index_false,'보유여부'] = False
            sell_price = round(df.loc[index_false,'보유수량']*df.loc[index_false,'매도체결가'])
            df.loc[index_false,'수수료'] = round(sell_price*fee_sell*0.01)
            df.loc[index_false,'총평가'] = sell_price-df.loc[index_false,'수수료']
            df.loc[index_false,'평가손익'] = df.loc[index_false,'총평가']-df.loc[index_false,'총매수']
            df.loc[index_false,'수익률'] = round(df.loc[index_false,'평가손익']/df.loc[index_false,'총매수']*100,2)
            df.loc[index_false:index_final,'최고수익률'] = np.nan
            df.loc[index_sold:index_final,'보유현금'] = round(df.loc[index_false,'보유현금']+df.loc[index_false,'총평가'])
            df.loc[index_sold:index_final,'매수금액'] = np.nan
            df.loc[index_sold:index_final,'총매수'] = np.nan
            df.loc[index_sold:index_final,'보유수량'] = np.nan
            df.loc[index_sold:index_final,'총평가'] = np.nan
            df.loc[index_sold:index_final,'수익률'] = np.nan
            df.loc[index_sold:index_final,'평가손익'] = np.nan
            df.loc[df.매수그룹 == i+1, '매수횟수'] = 1
            max_ror = 0
        # break

        # if i == 1:
        #     break
    # df['매수금액'] = df['보유현금'] / money_division
        # df.loc[(df['매수그룹'].shift(1)==i+1) & df]
    # for i, idx in enumerate(df.index):
    #     df.loc[(df.index == idx) & (df.보유여부 == True) & (df['고저평균대비등락율'].shift(1) <= high_ratio), '매수신호'] = True

    make_detail_db(df,ticker)
    commission_sell = df.loc[df.index[-1],'총평가']*fee_sell*0.01
    wallet = df.loc[df.index[-1],'보유현금'] + df.loc[df.index[-1],'총평가']-commission_sell
    benefit =  wallet - bet
    ror = round(benefit/bet*100,2)
    maximum = round(df['수익률'].max(),2)
    minimum = round(df['수익률'].min(),2)
    commission = df['수수료'].sum()
    signal = df['매수신호'].sum()
    origin_open = df.loc[df.index[0], 'open']
    origin_close = df.loc[df.index[-1], 'close']
    origin_ror = round((origin_close-origin_open)/origin_open*100,2)
    max_buy = round(df['총매수'].max(),2)
    print(f'배팅배수: {bet_muliple}, rsi: {rsi}, 고저대비: {high_ratio}, 트레일링스탑: {trail}, 수익률: {ror}, 수익금: {benefit}, 수수료: {commission}, 매수횟수: {signal}, 매수최고금액: {max_buy},최고수익률: {maximum}, 최저수익률: {minimum}, 단순보유수익률: {origin_ror} ')

    df = {'배팅배수':[bet_muliple],'rsi':[rsi],'고저대비':[high_ratio],'트레일링스탑':[trail],'수익률':[ror],'수익금':[benefit],'수수료':[commission],'매수횟수':[signal],'매수최고금액':[max_buy],'최고수익률':[maximum],'최저수익률':[minimum]}
    quit()
    # print(df)
    # quit()
    for i, idx in enumerate(df.index):
        ing = round(i / length * 100)
        if ing_before != ing:
            ing_before = ing
            # print(f'진행률: {ing_before}%',end=' ')
        # 매수
        # if df.loc[idx,]
        # if (df.loc[idx, '매수횟수'] == 0):
        # 수정사항 배팅금액
        #매수인데 미체결 후 다시 매수

        # def stg_buy(df):
        df.loc[(df.index == idx) & (df['rsi'].shift(1) < rsi) & (df['고저평균대비등락율'].shift(1) <= high_ratio), '매수신호'] = True

        # df.loc[(df.index == idx) & (df['매수횟수'].shift(1) == 1) & (df['rsi'].shift(1) < 30) & (df['고저평균대비등락율'].shift(1) <= -0.2) & (df['수익률'].shift(1)<-0.2), '매수신호'] = True
        # df.loc[(df.index == idx) & (df['매수횟수'].shift(1) == 2) & (df['rsi'].shift(1) < 30) & (df['고저평균대비등락율'].shift(1) <= -0.2) & (df['수익률'].shift(1)<-0.2), '매수신호'] = True
        # df.loc[(df.index == idx) & (df['매수횟수'].shift(1) == 3) & (df['rsi'].shift(1) < 30) & (df['고저평균대비등락율'].shift(1) <= -0.2) & (df['수익률'].shift(1)<-0.2), '매수신호'] = True
        # df.loc[(df.index == idx) & (df['매수횟수'].shift(1) == 4) & (df['rsi'].shift(1) < 30) & (df['고저평균대비등락율'].shift(1) <= -0.2) & (df['수익률'].shift(1)<-0.2), '매수신호'] = True

        df.loc[(df.index == idx) & (df['매수신호'] == 1), '매수호가'] = df['open'].apply(buy_hoga_return)
        df.loc[(df.index == idx) & (df['매수신호'] > 1), '매수호가'] = df.loc[df.index[i-1], '매수호가']

        # 매도
        def stg_sell(df):
            df.loc[(df.index == idx) & (df['매도신호'].isnull()) & (df['수익률'].shift(1) > 0.7) & (df['수익률'].shift(1) < df['최고수익률'].shift(1) * trail), '매도신호'] = True
            return df
        # df = stg_buy(df)
        df = stg_sell(df)
        df.loc[(df.index == idx) & (df['매도신호'] == True), '매도호가'] = df['open'].apply(sell_hoga_return)
        df.loc[(df.index == idx) & (df['매도신호'] > 1), '매도호가'] = df.loc[df.index[i-1], '매도호가']

        # if idx == 20220502011200:
        #     print(df.loc[idx,'수익률'])
        #     print(df.loc[idx,'최고수익률'])

        df.loc[idx, '보유여부'] = df.loc[df.index[i - 1], '보유여부']
        df.loc[idx, '보유현금'] = df.loc[df.index[i - 1], '보유현금']
        df.loc[idx, '보유수량'] = df.loc[df.index[i - 1], '보유수량']
        df.loc[idx, '매수횟수'] = df.loc[df.index[i - 1], '매수횟수']
        df.loc[idx, '매수금액'] = df.loc[df.index[i - 1], '매수금액']
        df.loc[idx, '총매수'] = df.loc[df.index[i - 1], '총매수']

        # 매수 체결
        if (df.loc[idx, '매수신호'] > 0):
            if df.loc[df.index[i], 'low'] < df.loc[df.index[i], '매수호가']:  # 매수 체결
                df.loc[idx, '보유여부'] = True
                df.loc[idx, '매수체결가'] = df.loc[idx, '매수호가']
                df.loc[idx, '매수횟수'] = df.loc[idx, '매수횟수'] + 1
                df.loc[idx, '매수시간'] = df.index[i]
                if (df.loc[idx, '매수횟수'] == 1) & ((df.loc[idx, '보유현금'] / money_division) > 5000) :
                    df.loc[idx, '매수금액'] = round(df.loc[idx, '보유현금'] / money_division)
                    df.loc[idx, '수수료'] = round(df.loc[idx, '매수금액'] * fee_buy * 0.01)
                    df.loc[idx, '총매수'] = df.loc[idx, '매수금액']
                    df.loc[idx, '보유현금'] = df.loc[idx, '보유현금'] - df.loc[idx, '매수금액']
                    df.loc[idx, '보유수량'] = round((df.loc[idx, '매수금액']-df.loc[idx, '수수료'])/df.loc[idx, '매수체결가'], 8)
                # elif (df.loc[idx, '매수횟수'] > 1) & (df.loc[idx, '보유현금'] > df.loc[idx, '매수금액']):
                #     df.loc[idx, '매수금액'] = df.loc[idx, '매수금액'] * 2
                #     df.loc[idx, '수수료'] = round(df.loc[idx, '매수금액'] * fee_buy * 0.01)
                #     df.loc[idx, '총매수'] = df.loc[idx, '매수금액'] + df.loc[idx, '총매수']
                #     df.loc[idx, '보유현금'] = df.loc[idx, '보유현금'] - df.loc[idx, '매수금액']
                #     df.loc[idx, '보유수량'] = round(df.loc[idx, '보유수량']+(df.loc[idx, '매수금액']-df.loc[idx, '수수료'])/df.loc[idx, '매수체결가'], 8)
                elif (df.loc[idx, '매수횟수'] > 1) & (df.loc[idx, '보유현금'] > df.loc[idx, '매수금액']):
                    df.loc[idx, '매수금액'] = round(df.loc[idx, '매수금액']*bet_m)
                    df.loc[idx, '수수료'] = round(df.loc[idx, '매수금액'] * fee_buy * 0.01)
                    df.loc[idx, '총매수'] = df.loc[idx, '매수금액'] + df.loc[idx, '총매수']
                    df.loc[idx, '보유현금'] = df.loc[idx, '보유현금'] - df.loc[idx, '매수금액']
                    df.loc[idx, '보유수량'] = round(df.loc[idx, '보유수량']+(df.loc[idx, '매수금액']-df.loc[idx, '수수료'])/df.loc[idx, '매수체결가'], 8)
                else:
                    quit()
            elif df.loc[idx, '매수신호'] == signal_buy:  # 매수 횟수 초과 시
                # print('매수취소')
                df.loc[df.index[i + 1], '매수신호'] = np.nan
            elif df.loc[df.index[i], 'low'] >= df.loc[df.index[i], '매수호가']:  # 매수 미체결
                # print('미체결')
                df.loc[df.index[i+1], '매수신호'] = df.loc[idx, '매수신호'] + 1
            # print(f"매수횟수: {df.loc[idx,'매수횟수']}")


        # 매도 체결
        elif (df.loc[idx, '매도신호'] >= 0):
            if df.loc[df.index[i], 'high'] > df.loc[df.index[i], '매도호가']:  # 매도 체결
                df.loc[idx, '보유여부'] = False
                df.loc[idx, '매도체결가'] = df.loc[idx, '매도호가']
                df.loc[idx, '수수료'] = round(df.loc[idx, '총매수'] * fee_sell * 0.01)
                df.loc[idx, '보유현금'] = df.loc[idx, '보유현금'] + \
                                      round(df.loc[idx, '매도체결가'] * df.loc[idx, '보유수량'] - df.loc[idx, '수수료'])
                df.loc[idx, '매수횟수'] = 0
                df.loc[idx, '총매수'] = np.nan
                df.loc[idx, '매수금액'] = np.nan
                df.loc[idx, '보유수량'] = np.nan
                df.loc[idx, '총평가'] = 0

                df.loc[idx, '매도시간'] = df.index[i]
            elif df.loc[idx, '매도신호'] == signal_sell :  # 매도 횟수 초과 시
                # print('매도횟수 초과: ',end='')
                df.loc[idx, '매도신호'] = np.nan
                df = stg_sell(df)
                if df.loc[idx, '매도신호'] == True:
                    # print('open가 매도')
                    df.loc[idx, '보유여부'] = False
                    df.loc[idx, '매도체결가'] = df.loc[idx, 'open'] #시작가로 다 던지기
                    df.loc[idx, '수수료'] = round(df.loc[idx, '총매수'] * fee_sell * 0.01)
                    df.loc[idx, '보유현금'] = df.loc[idx, '보유현금'] + \
                                          round(df.loc[idx, '매도체결가'] * df.loc[idx, '보유수량'] - df.loc[idx, '수수료'])
                    df.loc[idx, '매수횟수'] = 0
                    df.loc[idx, '총매수'] = np.nan
                    df.loc[idx, '매수금액'] = np.nan
                    df.loc[idx, '보유수량'] = np.nan
                    df.loc[idx, '매도시간'] = df.index[i]
                    df.loc[idx, '총평가'] = 0
                else:
                    df.loc[df.index[i+1], '매도신호'] = np.nan  # 매도 취소
                    # print('매도취소')
            elif df.loc[df.index[i], 'high'] <= df.loc[df.index[i], '매도호가']:  # 매도 미체결
                # print('미체결')
                df.loc[df.index[i+1], '매도신호'] = df.loc[idx, '매도신호'] + 1
        # 보유
        if df.loc[idx, '보유여부'] == True:  # 보유
            close = df.loc[idx, 'close']
            price = df.loc[idx, '총매수']
            volume = df.loc[idx, '보유수량']
            evalue = round(close * volume)  # 총평가
            df.loc[idx, '총평가'] = round(close * volume)
            df.loc[idx, '수익률'] = round((evalue - price) / price, 3) * 100 - fee_sell
            df.loc[idx, '평가손익'] = round(evalue - price - fee_sell)
            if df.loc[idx, '수익률'] >= df.loc[df.index[i - 1], '최고수익률']:
                df.loc[idx, '최고수익률'] = df.loc[idx, '수익률']
            else:
                df.loc[idx, '최고수익률'] = df.loc[df.index[i - 1], '최고수익률']
    make_detail_db(df,ticker)
    wallet = df.loc[df.index[-1],'보유현금'] + df.loc[df.index[-1],'총평가']
    benefit =  wallet - bet
    ror = round(benefit/bet*100,2)
    maximum = round(df['수익률'].max(),2)
    minimum = round(df['수익률'].min(),2)
    commission = df['수수료'].sum()
    signal = df['매수신호'].sum()
    origin_open = df.loc[df.index[0], 'open']
    origin_close = df.loc[df.index[-1], 'close']
    origin_ror = round((origin_close-origin_open)/origin_open*100,2)
    max_buy = round(df['총매수'].max(),2)
    print(f'배팅배수: {bet_m}, rsi: {rsi}, 고저대비: {high_ratio}, 트레일링스탑: {trail}, 수익률: {ror}, 수익금: {benefit}, 수수료: {commission}, 매수횟수: {signal}, 매수최고금액: {max_buy},최고수익률: {maximum}, 최저수익률: {minimum}, 단순보유수익률: {origin_ror} ')

    df = {'배팅배수':[bet_m],'rsi':[rsi],'고저대비':[high_ratio],'트레일링스탑':[trail],'수익률':[ror],'수익금':[benefit],'수수료':[commission],'매수횟수':[signal],'매수최고금액':[max_buy],'최고수익률':[maximum],'최저수익률':[minimum]}
    # print(df)

    return df
def make_back_db(df):
    con = sqlite3.connect('backtest.db')
    dt_now = str(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
    # dt_now = 'coins_vj_'+ dt_now[0:16]
    # table = 'coins_vj_'+ dt_now
    ror = df['수익률'].mean()
    benefit = df['수익금'].sum()
    plus=df[df['수익률'] > 0]
    minus=df[df['수익률'] < 0]
    df['interval']=interval
    df['수익금합계']=df['수익금'].cumsum()
    df['매수시간'] = df['매수시간'].astype(str)
    df['매도시간'] = df['매도시간'].astype(str)
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
    # df = df[df.duplicated(subset=['매수시간', '매도시간'], keep=False)]

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
    con = sqlite3.connect(db_path+'upbit_back_grid.db')
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
# def loss_hogaPriceReturn_per(currentPrice): #퍼센트로 반환
#     hogaPrice = currentPrice * ((loss_per * 0.01) + 1)
#     hogaUnit = hogaUnitCalc(hogaPrice)
#     minPrice = hogaUnitCalc_per(hogaPrice)
#     while True:
#         minPrice = (minPrice - hogaUnit)
#         if minPrice <= hogaPrice:
#             return round(minPrice, 2)
if __name__ == '__main__':
    db_path = 'D:/db_files/'
    # db_path = ''
    con = sqlite3.connect(db_path+'upbit.db')
    cur = con.cursor()

    interval = 'minute3'
    buy_hoga = -1 #매수호가
    sell_hoga = 1 #매도호가
    loss_per = -1 #손절
    sell_per = 0.7 #매도 수익률
    bet = 1000000 #최초 배팅금액
    rsi = 30
    high_ratio = -0.2
    trail = 0.8
    bet_muliple = 1.2
    signal_buy = 5 #매수신호 시 상한 횟수
    signal_sell = 3 #매도신호 시 상한 횟수
    money_division = 100
    fee_buy = 0.05 # %
    fee_sell = 0.05 # %


    # interval = 'minute3'
    # buy_hoga = -2 #매수호가
    # sell_hoga = 1 #매도호가
    # sell_per = 0.7 #매도 수익률
    # bet = 1000000 #최초 배팅금액
    # bet_multiple = [1,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2,2.1,2.2,2.3,2.4,2.5]
    # rsis = [25,26,27,28,29,30,31,32,33,34,35]
    # high_ratios = [-0.25,-0.24,-0.23,-0.22,-0.21,-0.2,-0.19,-0.18,-0.17,-0.16,-0.15]
    # trailing = [0.9,0.95,0.85,0.8,0.75,0.7]
    # signal_buy = 5 #매수신호 시 상한 횟수
    # signal_sell = 3 #매도신호 시 상한 횟수
    # money_division = 100
    # # tickers = get_ticker_list(cur,interval)
    # df_amount = pd.DataFrame()
    table_list= get_ticker_list(cur,interval)
    print(table_list)
    # print(exist_list)
    # quit()
        # tickers =['AVAX-'+interval,'ALGO-'+interval,'GLM-'+interval,'SRM-'+interval,'TON-'+interval,'BAT-'+interval]
    for ticker in table_list:
        start = time.time()
        df = pd.read_sql(f"SELECT * FROM '{ticker}'", con).set_index('index')
        df = df.iloc[1070:]
        # for bet_m in bet_multiple:
        #     for rsi in rsis:
        #         for high_ratio in high_ratios:
        #             for trail in trailing:
        result = df_back(df,ticker)
        dt_now = str(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
        result = pd.DataFrame(result,index=[dt_now])
        back_grid_con = sqlite3.connect(db_path + 'upbit_back_grid.db')
        result.to_sql('test',back_grid_con,if_exists='append')
        back_grid_con.commit()
        back_grid_con.close()

    con.close()
    # df_result = make_back_db(df_amount)
    # print(df_result)
