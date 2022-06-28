from PyQt5.QtWidgets import *
import sqlite3
import pandas as pd
import requests
from pandas import Series
# pd.set_option('display.max_row',None) #모든 행을 보고자 할 때
pd.set_option('display.max_columns',None) #모든 열을 보고자 할 때
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width',1500)
pd.set_option("display.unicode.east_asian_width", True)
pd.set_option('mode.chained_assignment',  None) # SettingWithCopyWarning 경고를 끈다
import numpy as np
import sys
import os.path
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore
from pyqtgraph.dockarea import *
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QSortFilterProxyModel,Qt
from PyQt5.QtWidgets import (QApplication, QTableWidget)
from collections import Counter
from pykrx import stock
from PyQt5.QtTest import QTest
import talib
import crosshair
import make_indicator
class Window(QWidget):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent=parent)
        # self.setGeometry(500, 100, 1000, 1000)
        # QTableWidget.setWindowTitle(self, "Custom table widget")
        proxymodel = QSortFilterProxyModel()  #정렬
        self.table1 = QTableWidget()

        self.table1.setMinimumSize(100, 500)
        # self.table1.setModel(proxymodel)
        self.table1.setSortingEnabled(True) #정렬
        self.table1.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers) #더블클릭 시 수정 금지
        # self.configureTable1(self.table1)
        # print(df)
        self.table2 = QTableWidget()
        self.table2.setSortingEnabled(True)
        self.table2.setMinimumSize(100, 50)
        self.table2.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        # self.configureTable2(self.table2)
        self.table3 = QTableWidget()
        self.table3.setMinimumSize(100, 250)
        self.table3.setSortingEnabled(True)
        self.table3.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table4 = QTableWidget()
        self.table4.setMinimumSize(100,  50)
        self.table4.setSortingEnabled(True)
        self.table4.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table5 = QTableWidget()
        self.table5.setMinimumSize(100, 250)
        self.table5.setSortingEnabled(True)
        self.table5.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        #https://appia.tistory.com/276
        # https://hello-bryan.tistory.com/213
        self.btn1 = QPushButton('stock_back')
        self.btn1.clicked.connect(lambda: self.configureTable1(self.table1))
        self.btn2 = QPushButton('backtest')
        self.btn2.clicked.connect(lambda: self.configureTable2(self.table2))
        self.btn3 = QPushButton('backtest_최적화')
        self.btn3.clicked.connect(lambda: self.configureTable4(self.table4))

        self.holic_btn1 = QPushButton('차멍 / 끄기')
        self.holic_btn1.clicked.connect(lambda: self.holic_mt(delay))
        self.holic_btn1.setCheckable(True)

        self.holic_btn2 = QPushButton('차멍 / 끄기')
        self.holic_btn2.clicked.connect(lambda: self.holic_back(delay))
        self.holic_btn2.setCheckable(True)

        self.holic_btn3 = QPushButton('차멍 / 끄기')
        self.holic_btn3.clicked.connect(lambda: self.holic_vc(delay))
        self.holic_btn3.setCheckable(True)

        # https: // www.pythonguis.com / tutorials / pyqt - layouts /
        self.ch_mt_3 = QRadioButton('3분')
        self.ch_mt_3.setCheckable(True)
        self.ch_mt_5 = QRadioButton('5분')
        self.ch_c_cap = QCheckBox('시총,주식수')
        self.ch_c_ohlcv = QCheckBox('시고저종')
        self.ch_c_fun = QCheckBox('지표')
        self.ch_r_cap = QCheckBox('시총,주식수')
        self.ch_r_ohlcv = QCheckBox('시고저종')
        self.ch_r_fun = QCheckBox('지표')
        # self.radio_ch1 = QRadioButton('Chart_1')
        # self.radio_ch1.setChecked(True)
        # self.radio_ch2 = QRadioButton('Chart_2')
        self.edit1 = QLineEdit(self)
        self.edit2 = QLineEdit(self)
        self.edit3 = QLineEdit(self)
        self.edit4 = QLineEdit(self)
        self.edit5 = QLineEdit(self)
        self.edit6 = QLineEdit(self)
        self.edit7 = QLineEdit(self)
        self.lbl1 = QLabel('avg')
        self.edit1.setText('30') #초기값
        self.lbl2 = QLabel('고저평균대비등락율')
        self.edit2.setText('0')
        self.lbl3 = QLabel('cci')
        self.edit3.setText('0')
        self.lbl4 = QLabel('매도총잔량평균')
        self.edit4.setText('60000')
        self.lbl5 = QLabel('value')
        self.edit5.setText('0')
        self.lbl6 = QLabel('체결강도max')
        self.edit6.setText('500')
        self.lbl7 = QLabel('최고등락')
        self.edit7.setText('0')
        # self.lbl_del = QLabel('백테삭제조건')
        # self.lbl_del_val = QLabel('백테삭제값')
        # self.btn_del = QPushButton('차멍 / 끄기')
        # self.btn_del.clicked.connect(lambda: self.holic_vc(delay))
        # self.btn_del.setCheckable(True)
        self.plain_buy_stg = QPlainTextEdit(self)
        self.plain_sell_stg = QPlainTextEdit(self)
        self.plain_range = QPlainTextEdit(self)


        self.edit1_t = self.edit1.text() #초기값을 전달
        self.edit2_t = self.edit2.text() #초기값을 전달
        self.edit3_t = self.edit3.text() #초기값을 전달
        self.edit4_t = self.edit4.text() #초기값을 전달
        self.edit5_t = self.edit5.text() #초기값을 전달
        self.edit6_t = self.edit6.text() #초기값을 전달
        self.edit7_t = self.edit7.text() #초기값을 전달

        self.edit1.textChanged[str].connect(self.val_change)
        self.edit2.textChanged[str].connect(self.val_change)
        self.edit3.textChanged[str].connect(self.val_change)
        self.edit4.textChanged[str].connect(self.val_change)
        self.edit5.textChanged[str].connect(self.val_change)
        self.edit6.textChanged[str].connect(self.val_change)
        self.edit7.textChanged[str].connect(self.val_change)

        # self.spinbox1.setRange(0, 200)
        # self.spinbox1.setSingleStep(1)
        # self.spinbox1.setValue(80)

        self.grid_top = QGridLayout(self)
        self.grid_top.setSpacing(10)
        # self.grid_top.addWidget(self.radio_ch1,0,0)
        # self.grid_top.addWidget(self.radio_ch2,1,0)
        self.grid_top.addWidget(self.lbl1,0,1)
        self.grid_top.addWidget(self.edit1,1,1)
        self.grid_top.addWidget(self.lbl2,0,2)
        self.grid_top.addWidget(self.edit2,1,2)
        self.grid_top.addWidget(self.lbl3,0,3)
        self.grid_top.addWidget(self.edit3,1,3)
        self.grid_top.addWidget(self.lbl4,0,4)
        self.grid_top.addWidget(self.edit4,1,4)
        self.grid_top.addWidget(self.lbl5,0,5)
        self.grid_top.addWidget(self.edit5,1,5)
        self.grid_top.addWidget(self.lbl6,0,6)
        self.grid_top.addWidget(self.edit6,1,6)
        self.grid_top.addWidget(self.lbl7,0,7)
        self.grid_top.addWidget(self.edit7,1,7)
        self.box_mt = QVBoxLayout(self)
        self.box_cu = QVBoxLayout(self)
        self.box_cd = QVBoxLayout(self)
        self.box_ru = QVBoxLayout(self)
        self.box_rd = QVBoxLayout(self)
        self.box_luu = QHBoxLayout(self)
        self.box_cuu = QHBoxLayout(self)
        self.box_ruu = QHBoxLayout(self)

        self.box_luu.addWidget(self.ch_mt_3)
        self.box_luu.addWidget(self.ch_mt_5)
        self.box_luu.addWidget(self.btn1)
        self.box_mt.addLayout(self.box_luu)
        self.box_mt.addWidget(self.table1)
        self.box_mt.addWidget(self.holic_btn1)
        self.box_cuu.addWidget(self.ch_c_cap)
        self.box_cuu.addWidget(self.ch_c_ohlcv)
        self.box_cuu.addWidget(self.ch_c_fun)
        self.box_cuu.addWidget(self.btn2)
        self.box_cu.addLayout(self.box_cuu)
        self.box_cu.addWidget(self.table2)
        self.box_cd.addWidget(self.table3)
        self.box_cd.addWidget(self.holic_btn2)
        self.box_ruu.addWidget(self.ch_r_cap)
        self.box_ruu.addWidget(self.ch_r_ohlcv)
        self.box_ruu.addWidget(self.ch_r_fun)
        self.box_ruu.addWidget(self.btn3)
        self.box_ru.addLayout(self.box_ruu)
        self.box_ru.addWidget(self.table4)
        self.box_rd.addWidget(self.table5)
        self.box_rd.addWidget(self.holic_btn3)

        self.frame_up = QFrame()
        self.frame_up.setMaximumSize(10000,  70)
        self.frame_up.setFrameShape(QFrame.StyledPanel)
        self.frame_up.setLayout(self.grid_top)

        self.Frame_mt = QFrame()
        self.Frame_mt.setFrameShape(QFrame.StyledPanel)
        self.Frame_mt.setLayout(self.box_mt)

        self.frame_vj_list = QFrame()
        self.frame_vj_list.setFrameShape(QFrame.StyledPanel)
        self.frame_vj_list.setLayout(self.box_cu)

        self.frame_jv_detail = QFrame()
        self.frame_jv_detail.setFrameShape(QFrame.StyledPanel)
        self.frame_jv_detail.setLayout(self.box_cd)

        self.frame_vc_list = QFrame()
        self.frame_vc_list.setFrameShape(QFrame.StyledPanel)
        self.frame_vc_list.setLayout(self.box_ru)

        self.frame_vc_detail = QFrame()
        self.frame_vc_detail.setFrameShape(QFrame.StyledPanel)
        self.frame_vc_detail.setLayout(self.box_rd)

        # self.frame_buy_stg = QFrame()
        # self.frame_buy_stg.setFrameShape(QFrame.StyledPanel)
        # # self.frame_buy_stg.setLayout(self.plain_buy_stg)
        # self.frame_sell_stg = QFrame()
        # self.frame_sell_stg.setFrameShape(QFrame.StyledPanel)
        # # self.frame_sell_stg.setLayout(self.plain_sell_stg)
        # self.frame_range = QFrame()
        # self.frame_range.setFrameShape(QFrame.StyledPanel)


        self.split_vj = QSplitter(Qt.Vertical)
        self.split_vj.addWidget(self.frame_vj_list)
        self.split_vj.addWidget(self.frame_jv_detail)

        self.split_vc = QSplitter(Qt.Vertical)
        self.split_vc.addWidget(self.frame_vc_list)
        self.split_vc.addWidget(self.frame_vc_detail)


        self.split_stg = QSplitter(Qt.Vertical)
        self.split_stg.addWidget(self.plain_buy_stg)
        self.split_stg.addWidget(self.plain_sell_stg)
        self.split_stg.addWidget(self.plain_range)

        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.Frame_mt)
        self.splitter.addWidget(self.split_vj)
        self.splitter.addWidget(self.split_vc)
        self.splitter.addWidget(self.split_stg)


        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.frame_up)
        self.vbox.addWidget(self.splitter)

        self.setLayout(self.vbox)

        self.table1.cellDoubleClicked.connect(self.celldoubleclicked_event1)
        self.table2.cellDoubleClicked.connect(self.celldoubleclicked_event2)
        self.table3.cellDoubleClicked.connect(self.celldoubleclicked_event3)
        self.table4.cellDoubleClicked.connect(self.celldoubleclicked_event4)
        self.table5.cellDoubleClicked.connect(self.celldoubleclicked_event5)
        # self.table3.doubleClicked.connect(self.celldoubleclicked_event2)

    def configureTable1(self, table):
        # table.setSortingEnabled(False)
        # table.clear()
        if self.ch_mt_3.isChecked():
            interval = 'minute3'
            print(interval)
        if self.ch_mt_5.isChecked():
            interval = 'minute5'
            print(interval)
        self.df1 = qtable_moneytop(interval)
        table.setRowCount(len(self.df1.index))
        table.setColumnCount(len(self.df1.columns))
        header = table.horizontalHeader()# 컬럼내용에따라 길이 자동조절
        for column in range(len(self.df1.columns)): #컬럼 생성
            table.setHorizontalHeaderItem(column, QTableWidgetItem(self.df1.columns[column]))
            header.setSectionResizeMode(column, QHeaderView.ResizeToContents) # 컬럼내용에따라 길이 자동조절
        # for i in range(len(self.df1.index)): #인덱스 생성
        #     table.setVerticalHeaderItem(i, QTableWidgetItem(str(self.df1.index[i])))
        table.verticalHeader().setVisible(False) #인덱스 삭제

        for row in range(len(self.df1.index)):
            for column in range(len(self.df1.columns)):
                val = self.df1.iloc[row, column]
                if type(val) != str:
                    val = val.item() #numpy.float 을 int로 변환
                    # print(type(val))
                it = QTableWidgetItem()
                it.setData(Qt.DisplayRole, val) #정렬 시 문자형이 아닌 숫자크기로 바꿈
                table.setItem(row, column, it)
        # table.setSortingEnabled(True) #소팅한 상태로 로딩 시 데이터가 이상해져 맨 앞과 뒤에 추가
    def configureTable2(self, table):
        table.setSortingEnabled(False)
        table.clear()
        select = 'vj'
        self.df2 = qtable_back_list(select)
        table.setRowCount(len(self.df2.index))
        table.setColumnCount(len(self.df2.columns))
        header = table.horizontalHeader()# 컬럼내용에따라 길이 자동조절

        for i in range(len(self.df2.columns)):
            table.setHorizontalHeaderItem(i, QTableWidgetItem(self.df2.columns[i]))
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents) # 컬럼내용에따라 길이 자동조절
        # for i in range(len(self.df2.index)):
        #     table.setVerticalHeaderItem(i, QTableWidgetItem(str(self.df2.index[i])[5:10]))
        table.verticalHeader().setVisible(False) #인덱스 삭제

        for row in range(len(self.df2.index)):
            for column in range(len(self.df2.columns)):
                val = self.df2.iloc[row, column]
                if type(val) != str:
                    val = val.item()  # numpy.float 을 float으로 변환
                it = QTableWidgetItem()
                it.setData(Qt.DisplayRole, val)  # 정렬 시 문자형이 아닌 숫자크기로 바꿈
                table.setItem(row, column, it)
        table.horizontalHeader().setStretchLastSection(True)
        # table.verticalHeader().setStretchLastSection(True)
        table.setSortingEnabled(True) #소팅한 상태로 로딩 시 데이터가 이상해져 맨 앞과 뒤에 추가
    def configureTable3(self, table,vj_time):
        table.setSortingEnabled(False)
        table.clear()
        cap = self.ch_c_cap.isChecked()
        ohlcv = self.ch_c_ohlcv.isChecked()
        fun = self.ch_c_fun.isChecked()
        self.df3 = qtable_backtest(vj_time,cap,ohlcv,fun)
        print('self.df3')
        print(self.df3)
        table.setRowCount(len(self.df3.index))
        table.setColumnCount(len(self.df3.columns))
        header = table.horizontalHeader()# 컬럼내용에따라 길이 자동조절

        for i in range(len(self.df3.columns)):
            table.setHorizontalHeaderItem(i, QTableWidgetItem(self.df3.columns[i]))
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents) # 컬럼내용에따라 길이 자동조절
        # for i in range(len(self.df3.index)):
        #     table.setVerticalHeaderItem(i, QTableWidgetItem(str(self.df3.index[i])[5:10]))
        table.verticalHeader().setVisible(False) #인덱스 삭제
        for row in range(len(self.df3.index)):
            for column in range(len(self.df3.columns)):
                val = self.df3.iloc[row, column]
                if type(val) != str:
                    val = val.item()  # numpy.float 을 int로 변환
                    # print(type(val))
                it = QTableWidgetItem()
                it.setData(Qt.DisplayRole, val)  # 정렬 시 문자형이 아닌 숫자크기로 바꿈
                table.setItem(row, column, it)
        # table.horizontalHeader().setStretchLastSection(True)
        # table.verticalHeader().setStretchLastSection(True)
        table.setSortingEnabled(True) #소팅한 상태로 로딩 시 데이터가 이상해져 맨 앞과 뒤에 추가
    def configureTable4(self, table):
        table.setSortingEnabled(False)
        table.clear()
        select = 'vc'
        self.df4 = qtable_back_list(select)
        table.setRowCount(len(self.df4.index))
        table.setColumnCount(len(self.df4.columns))
        header = table.horizontalHeader()# 컬럼내용에따라 길이 자동조절

        for i in range(len(self.df4.columns)):
            table.setHorizontalHeaderItem(i, QTableWidgetItem(self.df4.columns[i]))
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents) # 컬럼내용에따라 길이 자동조절
        # for i in range(len(self.df4.index)):
        #     table.setVerticalHeaderItem(i, QTableWidgetItem(str(self.df4.index[i])[5:10]))
        table.verticalHeader().setVisible(False) #인덱스 삭제

        for row in range(len(self.df4.index)):
            for column in range(len(self.df4.columns)):
                val = self.df4.iloc[row, column]
                if type(val) != str:
                    val = val.item()  # numpy.float 을 float으로 변환
                it = QTableWidgetItem()
                it.setData(Qt.DisplayRole, val)  # 정렬 시 문자형이 아닌 숫자크기로 바꿈
                table.setItem(row, column, it)
        table.horizontalHeader().setStretchLastSection(True)
        # table.verticalHeader().setStretchLastSection(True)
        table.setSortingEnabled(True) #소팅한 상태로 로딩 시 데이터가 이상해져 맨 앞과 뒤에 추가
    def configureTable5(self, table,vc_time):
        table.setSortingEnabled(False)
        table.clear()
        cap = self.ch_r_cap.isChecked()
        ohlcv = self.ch_r_ohlcv.isChecked()
        fun = self.ch_r_fun.isChecked()
        self.df5 = qtable_backtest(vc_time,cap,ohlcv,fun)
        #매수도시간 보기 편하게
        # self.df5['매수시간'] = self.df5['매수시간'].astype(str)
        # self.df5['매수시간'] = self.df5['매수시간'].str[4:6]+'/'+self.df5['매수시간'].str[6:8]+' '+self.df5['매수시간'].str[8:10]+':'+self.df5['매수시간'].str[10:12]+':'+self.df5['매수시간'].str[12:14]
        # self.df5['매도시간'] = self.df5['매도시간'].astype(str)
        # self.df5['매도시간'] = self.df5['매도시간'].str[4:6]+'/'+self.df5['매도시간'].str[6:8]+' '+self.df5['매도시간'].str[8:10]+':'+self.df5['매도시간'].str[10:12]+':'+self.df5['매도시간'].str[12:14]
        # print(self.df5)
        table.setRowCount(len(self.df5.index))
        table.setColumnCount(len(self.df5.columns))
        header = table.horizontalHeader()# 컬럼내용에따라 길이 자동조절

        for i in range(len(self.df5.columns)):
            table.setHorizontalHeaderItem(i, QTableWidgetItem(self.df5.columns[i]))
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents) # 컬럼내용에따라 길이 자동조절
        # for i in range(len(self.df5.index)):
        #     table.setVerticalHeaderItem(i, QTableWidgetItem(str(self.df5.index[i])[5:10]))
        table.verticalHeader().setVisible(False) #인덱스 삭제
        for row in range(len(self.df5.index)):
            for column in range(len(self.df5.columns)):
                val = self.df5.iloc[row, column]
                if type(val) != str:
                    val = val.item()  # numpy.float 을 int로 변환
                    # print(type(val))
                it = QTableWidgetItem()
                it.setData(Qt.DisplayRole, val)  # 정렬 시 문자형이 아닌 숫자크기로 바꿈
                table.setItem(row, column, it)
        # table.horizontalHeader().setStretchLastSection(True)
        # table.verticalHeader().setStretchLastSection(True)
        table.setSortingEnabled(True) #소팅한 상태로 로딩 시 데이터가 이상해져 맨 앞과 뒤에 추가
    def celldoubleclicked_event1(self):
        row = self.table1.currentRow()
        column = self.table1.currentColumn()
        item = self.table1.item(row, 0)
        stock_code = item.text()
        date = self.table1.horizontalHeaderItem(column).text()
        date = str(date)[0:4]
        stock_name = make_stock_name(stock_code)
        print(stock_code)
        print(date)
        df = get_ohlcv(stock_code, date)
        df = df_add(df,self.edit1_t,self.edit6_t)
        # View_Chart = self.select_chart()
        self.chart = Chart(df, stock_name, stock_code, date, self.edit2_t, self.edit3_t, self.edit4_t,self.edit5_t,self.edit7_t)
        self.chart.setGeometry(0, 30, 3850, 1010)
        self.chart.show()
    def celldoubleclicked_event2(self):
        self.plain_buy_stg.clear()
        self.plain_sell_stg.clear()
        self.plain_range.clear()
        row = self.table2.currentRow()
        vj_time = self.df2.index[row]
        print('vj_time=',vj_time)
        buy_stg = self.df2.loc[vj_time,'매수전략']
        sell_stg = self.df2.loc[vj_time,'매도전략']
        self.plain_buy_stg.setPlainText(buy_stg)
        self.plain_sell_stg.setPlainText(sell_stg)
        self.configureTable3(self.table3,vj_time)
    def celldoubleclicked_event3(self):
        row = self.table3.currentRow()
        stock_code = self.table3.item(row, 0).text()
        inter = self.table3.item(row, 1).text()
        # stock_code = item.text()
        buy_time = self.table3.item(row, 10).text() #매수시간에서 짤라가지고 date생성(컬럼수 늘어날 경우 숫자 변경해야됨)
        date = str(buy_time)[4:8]
        sell_time = self.table3.item(row, 11).text() #매수시간에서 짤라가지고 date생성(컬럼수 늘어날 경우 숫자 변경해야됨)
        # sell_time = str(sell_time)[4:8]
        # date = str(date)[0:2]+str(date)[2:4]
        get_code = stock_code+'-'+inter
        print(stock_code, buy_time, sell_time)
        df = get_data(get_code, buy_time,sell_time)
        print(df)
        stock_name = make_stock_name(stock_code)
        # print(df)
        df = df_add(df,self.edit1_t,self.edit6_t)
        df = df_backtest(stock_code, df,self.df3)
        # View_Chart = self.select_chart()
        self.chart = Chart(df, stock_name,stock_code,date,self.edit2_t,self.edit3_t,self.edit4_t,self.edit5_t,self.edit7_t)
        self.chart.setGeometry(0, 30, 3850, 1010)
        self.chart.show()
    def celldoubleclicked_event4(self):
        self.plain_buy_stg.clear()
        self.plain_sell_stg.clear()
        self.plain_range.clear()
        row = self.table4.currentRow()
        vc_time = self.df4.index[row]
        print('vc_time=',vc_time)
        buy_stg = self.df4.loc[vc_time,'매수전략']
        sell_stg = self.df4.loc[vc_time,'매도전략']
        range = self.df4.loc[vc_time,'범위설정']
        self.plain_buy_stg.setPlainText(buy_stg)
        self.plain_sell_stg.setPlainText(sell_stg)
        self.plain_range.setPlainText(range)
        self.configureTable5(self.table5,vc_time)
    def celldoubleclicked_event5(self):
        row = self.table5.currentRow()
        stock_code = self.table5.item(row, 0).text()
        # stock_code = item.text()
        date = self.table5.item(row, 8).text() #매수시간에서 짤라가지고 date생성(컬럼수 늘어날 경우 숫자 변경해야됨)
        date = str(date)[4:8]
        print(stock_code, date)
        df = get_data(stock_code, date, start, end, )
        stock_name = make_stock_name(stock_code)
        # print(df)
        df = df_add(df,self.edit1_t,self.edit6_t)
        df = df_backtest(stock_code, df,self.df5)
        # View_Chart = self.select_chart()
        self.chart = Chart(df, stock_name,stock_code, date,self.edit2_t,self.edit3_t,self.edit4_t,self.edit5_t,self.edit7_t)
        self.chart.setGeometry(0, 30, 3850, 1010)
        self.chart.show()
    def holic_mt(self,delay):
        col_num = self.df1.columns[2:].tolist()
        row_num = self.df1.index.tolist()
        for date in col_num:
            for stock_code in row_num:
                if self.df1.loc[stock_code, date] > 0: #머니탑에서 0이 아닌항목만 추출
                    if self.holic_btn1.isChecked() == True:
                        stock_name = make_stock_name(stock_code)
                        df = get_data(stock_code, date, start, end, )
                        df = df_add(df,self.edit1_t,self.edit6_t)
                        # View_Chart = self.select_chart()
                        self.holic_show_mt = Chart(df, stock_name, stock_code, date, self.edit2_t, self.edit3_t, self.edit4_t, self.edit5_t,self.edit7_t)
                        self.holic_show_mt.setGeometry(0, 30, 3850, 1010)
                        self.holic_show_mt.show()
                        QTest.qWait(delay)
                        self.holic_show_mt.close()
                    elif self.holic_btn1.isChecked() == False:
                        print(self.holic_btn1.isChecked())
                        exit = True
                        self.holic_show_mt.close()
                        break
            if exit == True:
                break
    def holic_back(self,delay):
        # print(df_back)
        # df_back.to_excel('table.xlsx')
        print(self.df3)
        self.df3['날짜'] = self.df3.매수시간.astype(str).str[4:8] ##index에서 str짤라가지고 date컬럼 생성
        groups = self.df3.groupby('날짜')  # 날짜별 그룹 만들기
        df_back2 = pd.DataFrame()
        days = list(groups.size().index)
        for day in days:  # 날짜별로접근
            df_mt_date = self.df3[self.df3.날짜 == day]  # 날짜 기준으로 돌아가며 df불러옴
            df_mt_date = df_mt_date.drop_duplicates(['종목코드'])
            df_back2 = pd.concat([df_back2,df_mt_date])
        for i in range(len(df_back2.index)):
            # if df_back2.iloc[i, 3] < 0: #당일수익이 0보다 작은 종목만 표시
                if self.holic_btn2.isChecked() == True:
                    stock_code = df_back2.iloc[i, 0]
                    date = df_back2.iloc[i, -1]
                    stock_name = make_stock_name(stock_code)
                    df = get_data(stock_code, date, start, end, )
                    df = df_add(df,self.edit1_t,self.edit6_t)
                    df = df_backtest(stock_code, df, self.df3)
                    # View_Chart = self.select_chart()
                    self.holic_show_back = Chart(df, stock_name, stock_code, date, self.edit2_t, self.edit3_t, self.edit4_t, self.edit5_t,self.edit7_t)
                    self.holic_show_back.setGeometry(0, 30, 3850, 1010)
                    self.holic_show_back.show()
                    QTest.qWait(delay)
                    self.holic_show_back.close()
                elif self.holic_btn2.isChecked() == False:
                    print(self.holic_btn2.isChecked())
                    self.holic_show_back.close()
                    break
    def holic_vc(self,delay):
        self.df5['날짜'] = self.df5.매수시간.astype(str).str[4:8] ##index에서 str짤라가지고 date컬럼 생성
        groups = self.df5.groupby('날짜')  # 날짜별 그룹 만들기
        df_back2 = pd.DataFrame()
        days = list(groups.size().index)
        for day in days:  # 날짜별로접근
            df_mt_date = self.df5[self.df5.날짜 == day]  # 날짜 기준으로 돌아가며 df불러옴
            df_mt_date = df_mt_date.drop_duplicates(['종목코드']) #중복된 종목코드 삭제
            df_back2 = pd.concat([df_back2,df_mt_date])
        for i in range(len(df_back2.index)):
            # if df_back2.loc[index, '당일수익'] < 0: #당일수익이 0보다 작은 종목만 표시
                if self.holic_btn3.isChecked() == True:
                    stock_code = df_back2.iloc[i,0]
                    date = df_back2.iloc[i,-1]
                    stock_name = make_stock_name(stock_code)
                    df = get_data(stock_code, date, start, end, )
                    df = df_add(df,self.edit1_t,self.edit6_t)
                    df = df_backtest(stock_code, df, self.df5)
                    # View_Chart = self.select_chart()
                    self.holic_show_back = Chart(df, stock_name, stock_code, date, self.edit2_t, self.edit3_t, self.edit4_t, self.edit5_t,self.edit7_t)
                    self.holic_show_back.setGeometry(0, 30, 3850, 1010)
                    self.holic_show_back.show()
                    QTest.qWait(delay)
                    self.holic_show_back.close()
                elif self.holic_btn3.isChecked() == False:
                    print(self.holic_btn3.isChecked())
                    self.holic_show_back.close()
                    break
    # def select_chart(self):
    #     view = False
    #     if self.radio_ch1.isChecked() == True:
    #         print('chart1')
    #         view = Chart_1
    #     elif self.radio_ch2.isChecked() ==True:
    #         print('chart2')
    #         view = Chart_2
    #     return view
    def val_change(self):
        self.edit1_t = self.edit1.text()
        self.edit2_t = self.edit2.text()
        self.edit3_t = self.edit3.text()
        self.edit4_t = self.edit4.text()
        self.edit5_t = self.edit5.text()
        self.edit6_t = self.edit6.text()
        self.edit7_t = self.edit7.text()
        pass

def df_time(df,start,end):
    start = start.replace(':', '')  # date변수의 ':'를 제거 후 저장
    end = end.replace(':', '')  # date변수의 ':'를 제거 후 저장
    start = start+'00' #시작시간에 초 를 더하기
    start = int(start) #시작시간을 정수형으로 변환
    end = end+'00' #끝시간에 초 를 더하기
    end = int(end) #끝시간을 정수형으로 변환
    df.index = df.index.astype(str)
    df['시간'] = df.index.str[8:14]  ##index에서 str짤라가지고 '시간'컬럼 생성
    df = df.astype({'시간':'int'}) #'시간'컬럼을 int형으로 변환
    df = df[df.시간 >= start]
    df = df[df.시간 <= end]
    return df
def qtable_moneytop(interval):
    def moneytop():
        conn = sqlite3.connect(ohlcv_file)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        table_list=cursor.fetchall() #fetchall 한번에 모든 로우 데이터 읽기 (종목코드 읽기)
        if not table_list:
            print('* DB 테이블이 비어있음 - 확인 필요 *')
        table_list = np.concatenate(table_list).tolist() #모든테이블을 리스트로변환 https://codechacha.com/ko/python-flatten-list/

        exist_list = []
        [exist_list.append(x) for x in table_list if str(x[x.find('-') + 1:]) == interval]  # for문을 컴프리헨션으로

        # print(exist_list)
        # val = ['BTC-minute3','BTC-minute3','ETH-minute3','ETH-minute3','XRP-minute3','XRP-minute3']
        # exist_list = [exist_list for x in exist_list if val in exist_list]
        # print(exist_list)

        df_mt = pd.read_sql("SELECT * FROM '"+ exist_list[0]+"'", conn).set_index('index')
        df_mt.index = df_mt.index.astype(str)
        df_mt.loc[df_mt.index, '날짜'] = df_mt.index.str[4:8]  ##index에서 str짤라가지고 '날짜'컬럼 생성
        groups = df_mt.groupby('날짜')  # 날짜별 그룹 만들기
        days = list(groups.size().index)
        df = pd.DataFrame(index=exist_list)
        df['종목코드'] = df.index
        # print(df)
        # df.columns = days
        for day in days:
            df[day] = day
        print(df)
        return df
    def moneytop_add(df,mt_list):
        df_add = pd.DataFrame(index = mt_list)
        conn = sqlite3.connect(ohlcv_file)
        for stock_code in mt_list:
            # name = make_stock_name(stock_code,stock_list)
            # df_add.loc[stock_code,'종목명'] = name
            df_db = pd.read_sql("SELECT * FROM " + "'"+ stock_code+"'", conn).set_index('index')
            df_db = df_time(df_db, start, end)

            df_db.loc[df_db.index, '날짜'] = df_db.index.str[4:8]  ##index에서 str짤라가지고 '날짜'컬럼 생성
            groups = df_db.groupby('날짜')  # 날짜별 그룹 만들기
            days = list(groups.size().index)
            for day in days:  # 날짜별로접근
                df_db_date = df_db[df_db.날짜 == day]  # 날짜가 같은 데이터만 df_db로 불러옴
                # print(df_db_date)
                low=df_db_date.loc[df_db_date.index[-1],'저가']

                high = df_db_date.loc[df_db_date.index[-1],'고가']
                amount = df_db_date.loc[df_db_date.index[-1],'당일거래대금']
                amount=round(amount)
                ch = df_db_date['체결강도'].max()
                ch=round(ch)
                byundong = (high-low)/low*100
                byundong=round(byundong)
                df_add.loc[stock_code,day+'거래대금']=amount
                df_add.loc[stock_code,day+'최고체강']=ch
                df_add.loc[stock_code,day+'변동률']=byundong
                # print(df_add)
        conn.close()
        df_add.fillna(0,inplace=True)
        df_add = df_add.sort_index(axis=1) #컬럼명을 날짜순으로 정렬
        df = pd.concat([df,df_add],axis=1)
        return df
    df = moneytop()
    detail = False
    if detail == True:
        df = moneytop_add(df,mt_list)
        # 컬럼순서 날짜별로 바꾸기
        # #https://hanawithdata.tistory.com/entry/pandas-column-%EC%88%9C%EC%84%9C-%EC%9E%AC%EB%B0%B0%EC%B9%98%ED%95%98%EB%8A%94-2%EA%B0%80%EC%A7%80-%EB%B0%A9%EB%B2%95
        col = df.columns[2:].tolist()
        col_num = int(len(col) / 4)
        col1 = df.columns[2:col_num + 2].tolist()
        col2 = df.columns[col_num + 2:].tolist()
        for i in range(col_num):
            for j in range(3):
                col1.insert((i * 4) + 1, col2.pop(0))
        df=df[col1]

    return df
def qtable_back_list(select):
    conn = sqlite3.connect(back_file)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    table_list = cursor.fetchall()  # fetchall 한번에 모든 로우 데이터 읽기 (종목코드 읽기)
    if not table_list:
        print('* DB 테이블이 비어있음 - 확인 필요 *')
    table_list = np.concatenate(table_list).tolist()  # 모든테이블을 리스트로변환 https://codechacha.com/ko/python-flatten-list/
    # print(table_list)
    table = ''
    if select == 'vj':
        table = 'coins_vj' #백테스트 불러오기
        print('vj 불러오기')
    elif select == 'vc':
        table = 'stock_vc' #최적화 불러오기
        print('vc 불러오기')
    df = pd.read_sql("SELECT * FROM '"+table+"'", conn).set_index('index')
    print(df)
    df.index = df.index.astype(str)
    df['index'] = df.index.str[4:6]+'/'+df.index.str[6:8]+' '+df.index.str[8:10]+':'+df.index.str[10:12] #db테이블의 테이블 제목이랑 stock_vj의 index가 다름 주의
    df['index'] = df.index

    # print('back 컬럼명=',df.columns.tolist())
    if select == 'vj':
        df = df[['index','interval','평균수익률','승률','최대낙폭률','일평균거래횟수','최대보유종목수', '수익률합계', '수익금합계', '거래횟수', '필요자금', '배팅금액', '평균보유기간',
                 '익절','손절','매수전략','매도전략'
                 ]]
    elif select == 'vc':
        df = df[['index','interval', '평균수익률', '승률', '최대낙폭률', '일평균거래횟수', '최대보유종목수', '수익률합계', '수익금합계', '거래횟수','필요자금', '배팅금액', '평균보유기간',
                 '익절', '손절', '변수','매수전략', '매도전략', '범위설정']]
    # print(df)
    conn.close()
    return df
def qtable_backtest(v_time,cap,ohlcv,fun):
    def backtest(v_time):
        # print(v_time)
        conn = sqlite3.connect(back_file)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        back_table_list = cursor.fetchall()  # fetchall 한번에 모든 로우 데이터 읽기
        back_table_list = np.concatenate(back_table_list).tolist()  # 모든테이블을 리스트로변환 https://codechacha.com/ko/python-flatten-list/
        # print(back_table_list)
        v_table = [x for x in back_table_list if str(x)[-14:-2] == str(v_time)[:-2]] #백리스트 목록에서 입력받은 값과 같은거 찾기
        # print('vtable',v_table)
        # print(v_time)
        back_table = v_table[0]
        # print(type(back_table))
        df_back_list = pd.read_sql("SELECT * FROM " + back_table, conn).set_index('index')
        # print('df_back_list')
        # print(df_back_list)
        # df_back_list = df_time(df_back_list, start, end)  # 백테스트 시간 슬라이싱
        # conn.close()
        # dict_bt = df_back_list['종목명'].to_dict()
        # bt_list = list(set(';'.join(list(dict_bt.values())).split(';')))
        # stock_name = df_back_list['종목명'].str.split(';').apply(Series, 1).stack()
        # buy_time = df_back_list['매수시간'].str.split(';').apply(Series, 1).stack()
        # sell_time = df_back_list['매도시간'].str.split(';').apply(Series, 1).stack()
        # buy_price = df_back_list['매수가'].str.split(';').apply(Series, 1).stack()
        # sell_price = df_back_list['매도가'].str.split(';').apply(Series, 1).stack()
        # profit = df_back_list['수익률'].str.split(';').apply(Series, 1).stack()
        # stock_name.index = stock_name.index.droplevel(-1)  # to line up with df_back_list's index
        # buy_time.index = buy_time.index.droplevel(-1)  # to line up with df_back_list's index
        # sell_time.index = sell_time.index.droplevel(-1)  # to line up with df_back_list's index
        # buy_price.index = buy_price.index.droplevel(-1)  # to line up with df_back_list's index
        # sell_price.index = sell_price.index.droplevel(-1)  # to line up with df_back_list's index
        # profit.index = profit.index.droplevel(-1)  # to line up with df_back_list's index
        # stock_name.name = '종목명'  # needs a name to join
        # buy_time.name = '매수시간'  # needs a name to join
        # sell_time.name = '매도시간'  # needs a name to join
        # buy_price.name = '매수가'  # needs a name to join
        # sell_price.name = '매도가'  # needs a name to join
        # profit.name = '수익률'  # needs a name to join
        # del df_back_list['종목명']
        # del df_back_list['매수시간']
        # del df_back_list['매도시간']
        # del df_back_list['매수가']
        # del df_back_list['매도가']
        # del df_back_list['수익률']
        # del df_back_list['시간']
        # del df_back_list['수익금']
        # del df_back_list['수익금합계']
        # df = pd.DataFrame()
        # df = pd.concat([stock_name, buy_time, sell_time, buy_price, sell_price, profit], axis=1)  # 시리즈를 열방향으로 합치기
        # df['매수시간'] = pd.to_numeric(df['매수시간'])
        # df['매도시간'] = pd.to_numeric(df['매도시간'])
        # df[['수익률']] = df[['수익률']].astype(float)  # 수익률 컬럼 float으로 변환
        # df['보유시간'] = df['매도시간'] - df['매수시간']
        # df['청산횟수'] = df.groupby(['종목명']).매수시간.transform('count') #종목명이 같은그룹을 매수시간 기준으로 카운트
        # df['날짜'] = df.index.str[0:8] ##index에서 str짤라가지고 date컬럼 생성
        # df['당일청산'] = df.groupby(['종목명', '날짜']).날짜.transform('count') #종목명,날짜가 같은그룹을 날짜 기준으로 카운트
        # df['전체수익'] = df.groupby(['종목명']).수익률.transform('sum') #종목명,날짜가 같은그룹을 수익률 기준으로 합산
        # df['당일수익'] = df.groupby(['종목명', '날짜']).수익률.transform('sum')
        # print(df)
        # for stock_name in df['종목명']:
        #     stock_code = make_stock_code(stock_name)
        #     df.loc[df.종목명 == stock_name, '종목코드'] = stock_code
        # df['전일날짜'] = (df['매수시간'] - 1000000).astype(str).str[0:8]  # -1000000넣는 이유는 전일 기준으로 하기위해
        # df = df[['종목명','수익률','당일수익','전체수익','보유시간','당일청산','청산횟수','전일날짜','매수시간','매도시간','매수가','매도가' ]]
        # df.to_excel("D:/PythonProjects/df_sort.xlsx")
        df = df_back_list[['종목명','interval','수익률','수익금','보유시간','매수가','매도가','수익금합계','매수시간_dt','매도시간_dt','매수시간','매도시간']]
        return df
    def backtest_cap(df):
        df_del = df[['종목코드','전일날짜']]
        groups = df_del.groupby('전일날짜')
        df_back = pd.DataFrame() #빈프레임
        days = list(groups.size().index)
        for day in days:  # 날짜 그룹별로 접근(종가,시총,거래량,거래대금,주식수)
            df_db_date = df_del[df_del.전일날짜 == day]  # 날짜가 같은 데이터만 df_db로 불러옴
            df_cap = stock.get_market_cap(day)
            df_cap.reset_index(drop=False, inplace=True)  # 인덱스 번호순 으로 재 정의
            df_cap.rename(columns={'티커': '종목코드'}, inplace=True)  # 컬럼명 변경
            df_db_date = pd.merge(df_db_date, df_cap, how='left', left_on='종목코드', right_on='종목코드') # 종목코드 기준으로 합치기 pykrx에서 가져온 정보 넣기
            df_back = pd.concat([df_back, df_db_date])
        df_back.drop(['종목코드','전일날짜','종가','거래량','거래대금'], axis=1,inplace=True)  # 중복되고 필요없는 열 삭제
        df_back['시가총액'] = round(df_back['시가총액']/100000000,1)
        df_back['상장주식수'] = round(df_back['상장주식수']/1000000,1)
        df_back.rename(columns={'시가총액':'전일시총(억)','상장주식수':'주식수(백만)'}, inplace=True)  # 컬럼명 변경
        df.reset_index(drop=True, inplace=True)  #서로 합치기 위해 인덱스를 재정의하여 맞춰줌
        df_back.reset_index(drop=True, inplace=True)  #서로 합치기 위해 인덱스를 재정의하여 맞춰줌
        df_back = pd.concat([df, df_back],axis=1)
        return df_back
    def backtest_ohlcv(df):
        df_del = df[['종목코드','전일날짜']]
        groups = df_del.groupby('전일날짜')
        df_back = pd.DataFrame() #빈프레임
        days = list(groups.size().index)
        for day in days:  # 날짜 그룹별로 접근(ohlcv)
            df_db_date = df_del[df_del.전일날짜 == day]  # 날짜가 같은 데이터만 df_db로 불러옴
            df_cap = stock.get_market_ohlcv(day,market='ALL')
            df_cap.reset_index(drop=False, inplace=True)  # 인덱스 번호순 으로 재 정의
            df_cap.rename(columns={'티커': '종목코드'}, inplace=True)  # 컬럼명 변경
            df_db_date = pd.merge(df_db_date, df_cap, how='left', left_on='종목코드', right_on='종목코드') # 종목코드 기준으로 합치기 pykrx에서 가져온 정보 넣기
            df_back = pd.concat([df_back, df_db_date])
        df_back.drop(['종목코드','전일날짜'], axis=1,inplace=True)  # 중복되고 필요없는 열 삭제
        df_back['거래량'] = round(df_back['거래량']/1000000,1)
        df_back['거래대금'] = round(df_back['거래대금']/100000000,1)
        df_back['전일고저'] = round(((df_back['고가']-df_back['저가'])/df_back['저가'])*100,2)
        df_back.rename(columns={'시가':'전일시가','고가': '전일고가','저가': '전일저가','종가': '전일종가','거래량':'전거래량(백만)','거래대금':'전거래대금(억)','등락률':'전일등락'}, inplace=True)  # 컬럼명 변경
        df.reset_index(drop=True, inplace=True)  #서로 합치기 위해 인덱스를 재정의하여 맞춰줌
        df_back.reset_index(drop=True, inplace=True)  #서로 합치기 위해 인덱스를 재정의하여 맞춰줌
        df_back = pd.concat([df, df_back],axis=1)
        return df_back
    def backtest_fun(df):
        df_del = df[['종목코드','전일날짜']]
        groups = df_del.groupby('전일날짜')
        df_back = pd.DataFrame() #빈프레임
        days = list(groups.size().index)
        for day in days:  # 날짜 그룹별로 접근(펀더멘탈)
            df_db_date = df_del[df_del.전일날짜 == day]  # 날짜가 같은 데이터만 df_db로 불러옴
            df_cap = stock.get_market_fundamental(day,market='ALL')
            df_cap.reset_index(drop=False, inplace=True)  # 인덱스 번호순 으로 재 정의
            df_cap.rename(columns={'티커': '종목코드'}, inplace=True)  # 컬럼명 변경
            df_db_date = pd.merge(df_db_date, df_cap, how='left', left_on='종목코드', right_on='종목코드') # 종목코드 기준으로 합치기 pykrx에서 가져온 정보 넣기
            df_back = pd.concat([df_back, df_db_date])
        df_back.drop(['종목코드','전일날짜'], axis=1,inplace=True)  # 중복되고 필요없는 열 삭제
        df.reset_index(drop=True, inplace=True)  #서로 합치기 위해 인덱스를 재정의하여 맞춰줌
        df_back.reset_index(drop=True, inplace=True)  #서로 합치기 위해 인덱스를 재정의하여 맞춰줌
        df_back = pd.concat([df, df_back],axis=1)
        return df_back
    df = backtest(v_time)
    # print(df)
    if cap == True:
        df = backtest_cap(df)
    if ohlcv == True:
        df = backtest_ohlcv(df)
    if fun == True:
        df = backtest_fun(df)
    # print(df)
    # df.drop(['전일날짜'], axis=1, inplace=True)  # 중복되거나 필요없는 열 삭제
    # print('back 컬럼명=',df.columns.tolist())
    # print(df.sort_values(by=['매수시간']))
    return df

def make_stock_name(stock_code):
    url = "https://api.upbit.com/v1/market/all"
    resp = requests.get(url)
    data = resp.json()
    # print(data)
    stock_code = 'KRW-'+stock_code
    # print(stock_code)
    stock_name = ''
    for i, ticker in enumerate(data):
        if stock_code == ticker['market']:
            stock_name = ticker['korean_name']
    # print(stock_name)
    return stock_name
def get_ohlcv(stock_code,date):
    if not os.path.isfile(ohlcv_file):
        print('* 파일 없음 - 경로 확인 *')
    conn = sqlite3.connect(ohlcv_file)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    try:
        df_db = pd.read_sql("SELECT * FROM " + "'" + stock_code + "'", conn).set_index('index')
    except:
        print('* db파일에 종목 없음 *')
        df = []
    df_db.index = df_db.index.astype(str)
    df_db.loc[df_db.index, '날짜'] = df_db.index.str[4:8]  ##index에서 str짤라가지고 '날짜'컬럼 생성
    groups = df_db.groupby('날짜')  # 날짜별 그룹 만들기
    days = list(groups.size().index)
    for day in days:  # 날짜별로접근
        df_db_date = df_db[df_db.날짜 == date]  # 날짜가 같은 데이터만 df_db로 불러옴
    print(df_db_date)

    if df_db_date.empty:
        print('* db테이블에 종목은 있으나 데이터가 비어있음 또는 머니탑에 종목은 있으나 테이블이 비어있음- 확인 필요 *')

    conn.close()
    return df_db_date
def get_data(stock_code,buy_time,sell_time):
    if not os.path.isfile(ohlcv_file):
        print('* 파일 없음 - 경로 확인 *')
    conn = sqlite3.connect(ohlcv_file)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    try:
        df = pd.read_sql("SELECT * FROM " + "'" + stock_code + "'", conn).set_index('index')
    except:
        print('* db파일에 종목 없음 *')
        df = []
    buy_time = int(buy_time)
    sell_time = int(sell_time)
    for i,idx in enumerate(df.index):
        if idx == buy_time:
            start = i-gap_interval
        elif idx == sell_time:
            end = i+gap_interval
    df = df.iloc[start:end]
    print(df)
    # df = df[df.index >= buy_time] #date변수의 앞숫자 보다 크거나 같은 값의 범위만 df에 저장
    # df = df[df.index <= sell_time] #date변수의 뒷숫자 보다 작거나 같은 값의 범위만 df에 다시 저장
    df.index = df.index.astype(str)
    df.loc[df.index,'날짜'] = df.index.str[4:8] ##index에서 str짤라가지고 date컬럼 생성
    # df = df_time(df, start, end)
    if df.empty:
        print('* db테이블에 종목은 있으나 데이터가 비어있음 또는 머니탑에 종목은 있으나 테이블이 비어있음- 확인 필요 *')

    conn.close()
    return df

def df_backtest(stock_code,df,df_back_list):
    # print(df_back_list)
    marker_index=df_back_list.index[df_back_list['종목명'] == stock_code].tolist() #종목명 매칭하여 완벽히 동일한 글자가 들어가면 인덱스 값 추출
    if not marker_index :
        print('* 백테스트 db파일에 종목 없음 *')
    df_back = df_back_list.loc[marker_index] #인덱스 매칭하여 해당 행만 추출
    df_back = df_back[df_back['종목명'] == stock_code] #동일한 시간에 2종목이 매수될 수 있으므로 다시 걸러줌
    df_back_time_buy = df_back[['매수시간','매수가']] #매수에 대한 DF추출
    df_back_time_sell = df_back[['매도시간','매도가','수익률']]#매도에 대한 DF추출
    df_back_time_buy.set_index('매수시간',inplace=True) #매수에 대한 인덱스 재 정의
    df_back_time_sell.set_index('매도시간',inplace=True) #매도에 대한 인덱스 재 정의
    df_back_time_buy = df_back_time_buy.astype(float) #str을 float으로 변환
    df_back_time_sell = df_back_time_sell.astype(float)
    df_back = pd.concat([df_back_time_buy,df_back_time_sell]) # buy + sell 행방향으로 합치기
    df_back.index = df_back.index.astype(str) #df를 합치기위해 index타입 변경
    df.drop(['매수가','매도가'],axis=1,inplace=True) #df_add에서 매수가,매도가를 만들어줬는데 이를 지우기 위함
    df=pd.merge(df, df_back,left_index = True, right_index = True,how = 'left') # 인덱스기준으로 df + df_back 합치기

    # df.to_csv("D:/PythonProjects/df_marker.csv", header=True, index=True, encoding='utf-8-sig')
    return df
def db_stock_list():
    conn = sqlite3.connect(ohlcv_file)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    table = 'codename'
    df = pd.read_sql("SELECT * FROM " + "'" + table + "'", conn).set_index('index')
    # df['종목코드'] = df.index
    conn.close()
    df.reset_index(drop=False, inplace=True)  # 인덱스 번호순 으로 재 정의
    df.rename(columns={'index': '종목코드'}, inplace=True)  # 컬럼명 변경
    return df
class Chart(QWidget):
    def __init__(self,df,stock_name,stock_code,date,edit2,edit3,edit4,edit5,edit7):
    # def __init__(self):
        super().__init__()
        # self.win = pg.GraphicsLayoutWidget(show=True)
        self.win1 = pg.GraphicsLayoutWidget(self) #pyqtgraph
        self.win2 = pg.GraphicsLayoutWidget(self) #pyqtgraph

        tabs = QTabWidget()
        tabs.addTab(self.win1, 'Tab1')
        tabs.addTab(self.win2, 'Tab2')
        # self.table = QTableWidget(self)
        # self.plaintext = QPlainTextEdit(self)
        vbox = QVBoxLayout()
        vbox.addWidget(tabs)
        self.setLayout(vbox)
        vbox.setContentsMargins(0,0,0,0)

        # self.win1.setWindowTitle('주식차트')
        # self.win2.setWindowTitle('주식차트')
        self.win1.setGeometry(0, 0, 3850, 1010)
        self.win2.setGeometry(0, 0, 3850, 1010)
        bottomAxis_1 = pg.AxisItem(orientation='bottom')
        bottomAxis_2 = pg.AxisItem(orientation='bottom')
        bottomAxis_date_1 = pg.AxisItem(orientation='bottom')
        bottomAxis_date_2 = pg.AxisItem(orientation='bottom')

        # link_view
        area = DockArea()
        # d1 = Dock("Dock1")
        area.addDock(Dock("Dock1"), 'bottom')

        # p1_1 = self.win.addPlot(row=0, col=0,title=stock_name + date,axisItems={'bottom': pg.DateAxisItem()})
        # p1_2 = self.win.addPlot(row=1, col=0,title='체결강도',axisItems={'bottom': pg.AxisItem(orientation='bottom')})

        p1_1 = self.win1.addPlot(row=0, col=0,title=f'{stock_name}({stock_code}), {str(date)[:2]}/{str(date)[2:4]}',axisItems={'bottom': bottomAxis_1})
        p1_2 = self.win1.addPlot(row=1, col=0,title='1_2 체결강도',axisItems={'bottom': pg.AxisItem(orientation='bottom')})
        p1_3 = self.win1.addPlot(row=2, col=0,title='1_3 체결강도',axisItems={'bottom': pg.AxisItem(orientation='bottom')})
        # p1_4 = self.win1.addPlot(row=0, col=1,title='거래대금',axisItems={'bottom': bottomAxis_date_1})
        p1_4 = self.win1.addPlot(row=0, col=1,title='1_4 거래대금',axisItems={'bottom': pg.AxisItem(orientation='bottom')})
        p1_5 = self.win1.addPlot(row=1, col=1,title='1_5 거래대금/속도',axisItems={'bottom': pg.AxisItem(orientation='bottom')})
        p1_6 = self.win1.addPlot(row=2, col=1,title='1_6 거래대금각도',axisItems={'bottom': pg.AxisItem(orientation='bottom')})
        p1_7 = self.win1.addPlot(row=0, col=2,title='1_7 초당대금',axisItems={'bottom': pg.AxisItem(orientation='bottom')})
        p1_8 = self.win1.addPlot(row=1, col=2,title='1_8 초당대금평균',axisItems={'bottom': pg.AxisItem(orientation='bottom')})
        p1_9 = self.win1.addPlot(row=2, col=2,title='1_9 총잔량',axisItems={'bottom': pg.AxisItem(orientation='bottom')})
        p1_10 = self.win1.addPlot(row=0, col=3,title='1_10 호가',axisItems={'bottom': pg.AxisItem(orientation='bottom')})
        p1_11 = self.win1.addPlot(row=1, col=3,title='1_11 잔량1',axisItems={'bottom': pg.AxisItem(orientation='bottom')})
        p1_12 = self.win1.addPlot(row=2, col=3,title='1_12 잔량2',axisItems={'bottom': pg.AxisItem(orientation='bottom')})

        p2_1 = self.win2.addPlot(row=0, col=0, title=f'{stock_name}({stock_code}), {str(date)[:2]}/{str(date)[2:4]}',axisItems={'bottom': bottomAxis_2})
        p2_2 = self.win2.addPlot(row=1, col=0, title='2_2 체결강도', axisItems={'bottom': pg.AxisItem(orientation='bottom')})
        p2_3 = self.win2.addPlot(row=2, col=0, title='2_3 체결강도', axisItems={'bottom': pg.AxisItem(orientation='bottom')})
        p2_4 = self.win2.addPlot(row=0, col=1, title='2_4 거래대금', axisItems={'bottom': pg.AxisItem(orientation='bottom')})
        p2_5 = self.win2.addPlot(row=1, col=1, title='2_5 등락율', axisItems={'bottom': pg.AxisItem(orientation='bottom')})
        p2_6 = self.win2.addPlot(row=2, col=1, title='2_6 고저평균대비등락율', axisItems={'bottom': pg.AxisItem(orientation='bottom')})
        p2_7 = self.win2.addPlot(row=0, col=2, title='2_7 초당대금', axisItems={'bottom': pg.AxisItem(orientation='bottom')})
        p2_8 = self.win2.addPlot(row=1, col=2, title='2_8 초당대금평균', axisItems={'bottom': pg.AxisItem(orientation='bottom')})
        p2_9 = self.win2.addPlot(row=2, col=2, title='2_9 총잔량', axisItems={'bottom': pg.AxisItem(orientation='bottom')})
        p2_10 = self.win2.addPlot(row=0, col=3, title='2_10 호가', axisItems={'bottom': pg.AxisItem(orientation='bottom')})
        p2_11 = self.win2.addPlot(row=1, col=3, title='2_11 잔량1', axisItems={'bottom': pg.AxisItem(orientation='bottom')})
        p2_12 = self.win2.addPlot(row=2, col=3, title='2_12 잔량2', axisItems={'bottom': pg.AxisItem(orientation='bottom')})

        p1_1.addLegend()
        p1_2.addLegend()
        p1_3.addLegend()
        p1_4.addLegend()
        p1_5.addLegend()
        p1_6.addLegend()
        p1_7.addLegend()
        p1_8.addLegend()
        p1_9.addLegend()
        p1_10.addLegend()
        p1_11.addLegend()
        p1_12.addLegend()

        p2_1.addLegend()
        p2_2.addLegend()
        p2_3.addLegend()
        p2_4.addLegend()
        p2_5.addLegend()
        p2_6.addLegend()
        p2_7.addLegend()
        p2_8.addLegend()
        p2_9.addLegend()
        p2_10.addLegend()
        p2_11.addLegend()
        p2_12.addLegend()

        p1_1.showGrid(x=True, y=True)
        # d1.addWidget(p1_1)
        p1_2.showGrid(x=True, y=True)
        p1_3.showGrid(x=True, y=True)
        p1_4.showGrid(x=True, y=True)
        p1_5.showGrid(x=True, y=True)
        p1_6.showGrid(x=True, y=True)
        p1_7.showGrid(x=True, y=True)
        p1_8.showGrid(x=True, y=True)
        p1_9.showGrid(x=True, y=True)
        p1_10.showGrid(x=True, y=True)
        p1_11.showGrid(x=True, y=True)
        p1_12.showGrid(x=True, y=True)

        p2_1.showGrid(x=True, y=True)
        p2_2.showGrid(x=True, y=True)
        p2_3.showGrid(x=True, y=True)
        p2_4.showGrid(x=True, y=True)
        p2_5.showGrid(x=True, y=True)
        p2_6.showGrid(x=True, y=True)
        p2_7.showGrid(x=True, y=True)
        p2_8.showGrid(x=True, y=True)
        p2_9.showGrid(x=True, y=True)
        p2_10.showGrid(x=True, y=True)
        p2_11.showGrid(x=True, y=True)
        p2_12.showGrid(x=True, y=True)

        p1_2.setXLink(p1_1)
        p1_3.setXLink(p1_1)
        p1_4.setXLink(p1_1)
        p1_5.setXLink(p1_1)
        p1_6.setXLink(p1_1)
        p1_7.setXLink(p1_1)
        p1_8.setXLink(p1_1)
        p1_9.setXLink(p1_1)
        p1_10.setXLink(p1_1)
        p1_11.setXLink(p1_1)
        p1_12.setXLink(p1_1)

        p2_2.setXLink(p2_1)
        p2_3.setXLink(p2_1)
        p2_4.setXLink(p2_1)
        p2_5.setXLink(p2_1)
        p2_6.setXLink(p2_1)
        p2_7.setXLink(p2_1)
        p2_8.setXLink(p2_1)
        p2_9.setXLink(p2_1)
        p2_10.setXLink(p2_1)
        p2_11.setXLink(p2_1)
        p2_12.setXLink(p2_1)

        self.win1.ci.layout.setColumnStretchFactor(0, 100)
        self.win1.ci.layout.setColumnStretchFactor(1, 105)
        self.win1.ci.layout.setColumnStretchFactor(2, 105)
        self.win1.ci.layout.setColumnStretchFactor(3,  85)

        self.win2.ci.layout.setColumnStretchFactor(0, 100)
        self.win2.ci.layout.setColumnStretchFactor(1, 105)
        self.win2.ci.layout.setColumnStretchFactor(2, 105)
        self.win2.ci.layout.setColumnStretchFactor(3, 85)

        # Enable antialiasing for prettier plots
        pg.setConfigOptions(antialias=True)

        # # Basic Array Plotting
        p1_1.clear()
        p1_2.clear()
        p1_3.clear()
        p1_4.clear()
        p1_5.clear()
        p1_6.clear()
        p1_7.clear()
        p1_8.clear()
        p1_9.clear()
        p1_10.clear()
        p1_11.clear()
        p1_12.clear()

        p2_1.clear()
        p2_2.clear()
        p2_3.clear()
        p2_4.clear()
        p2_5.clear()
        p2_6.clear()
        p2_7.clear()
        p2_8.clear()
        p2_9.clear()
        p2_10.clear()
        p2_11.clear()
        p2_12.clear()

        # xticks = [x.timestamp() - 32400 for x in df.index]
        df['index_time'] = pd.to_datetime(df.index, format='%Y%m%d%H%M%S')
        print(df)
        df = df.astype({'index_time': 'str'})
        df=df.drop_duplicates(['index_time']) #시간이 중복인 행 제거
        df.loc[df.index, 'index_time'] = df[df.index_time.str[-5:-3] == '00']   # index_chart의 초가 '00'인 경우만 index_chart컬럼 값 저장
        print()
        df = df.astype({'index_time': 'str'}) #'index_time'컬럼을 str로 변환
        df['index_time'] = df['index_time'].str[11:-3]

        df['index_date'] = pd.to_datetime(df.index, format='%Y%m%d%H%M%S')
        df = df.astype({'index_date': 'str'})
        p = df.index[df['날짜']!=df['날짜'].shift(1)] # 날짜가 바뀌는 행의 인덱스를 추출
        df['index_date'] = df.loc[p,'index_date'] #추출한 인덱스값의 'index_date'컬럼 값만 남김
        df['index_date'] = df['index_date'].str[5:11]
        df['index_date'] = df['index_date'].replace(np.nan,'',regex=True) #nan값을 공백으로 변경

        df['index_chart']=df['index_date']+df['index_time'] #더하기
        df['index_chart'] = df['index_chart'].str[0:5]
        df['index_chart'] = df['index_chart'].replace(end,'',regex=True) #차트의 마지막 index 값을 공백으로 변경
        # df['매수가'] = df['매수가'].replace(np.nan,'',regex=True) #nan값을 공백으로 변경

        df['number'] = range(0,len(df)) # 넘버링 컬럼 추가
        # print(df)
        buy_index = df['number'][df['매수가'].isna() == False] #'매수가'가 nan이 아닌 행의 'number' 컬럼 값을 추출
        buy_price = df['매수가'][df['매수가'].isna() == False] #'매수가'가 nan이 아닌 행의 '매수가' 컬럼의 값을 추출
        sell_index = df['number'][df['매도가'].isna() == False] #'매도가'가 nan이 아닌 행의 'number' 컬럼 값을 추출
        sell_price = df['매도가'][df['매도가'].isna() == False] #'매도가'가 nan이 아닌 행의 '매도가' 컬럼의 값을 추출

        time = df['index_chart'].tolist()
        xDict=dict(enumerate(time))
        xValue=list(xDict.keys())
        xtickts=[xDict.items()]
        bottomAxis_1.setTicks(xtickts)
        bottomAxis_2.setTicks(xtickts)

        date = df['index_date'].tolist()
        xDict=dict(enumerate(date))
        xDate=list(xDict.keys())
        xtickts_date=[xDict.items()]
        bottomAxis_date_1.setTicks(xtickts_date)
        bottomAxis_date_2.setTicks(xtickts_date)

        # time = df['index_chart'].tolist()
        # xDict = dict(enumerate(time))
        # xValue = list(xDict.keys())
        # xtickts = [xDict.items()]
        #
        # date = df['index_date'].tolist()
        # xDict = dict(enumerate(date))
        # xDate = list(xDict.keys())
        # xtickts_date = [xDict.items()]

        # print('사용가능지표: ',end="")
        # for i in range (len(df.columns)):
        #     col_name = df.columns[i]
        #     globals()['{}'.format(col_name)] = df[col_name].tolist()
        #     print(col_name,', ',end="")
        #     if i % 16==0:
        #         print('\n')

        y_dot = pg.mkPen(color='y', width=1, style=QtCore.Qt.DotLine)
        g_dot = pg.mkPen(color='g', width=1, style=QtCore.Qt.DotLine)
        w_dot = pg.mkPen(color='w', width=1, style=QtCore.Qt.DotLine)
        r_dash = pg.mkPen(color='r', width=1, style=QtCore.Qt.DashLine)
        g_dash = pg.mkPen(color=[0,130,153], width=1.2, style=QtCore.Qt.DashLine)
        color_1 = (255,0,0)

        # p1_1.plot(x=xValue, y=df['high'], pen=(120,200,200),name='high')
        # p1_1.plot(x=xValue, y=df['low'], pen=(120,150,150),name='low')
        # p1_1.plot(x=xValue, y=df['이평60마지' ], pen=y_dot,name='이평60마지')
        p1_1.plot(x=xValue, y=df['ma5'], pen=(128, 65,117),name='ma5')
        # p1_1.plot(x=xValue, y=df['이평300마지' ], pen=g_dot,name='이평300마지')
        p1_1.plot(x=xValue, y=df['ma60'], pen=(120, 150, 50),name='ma60')
        # p1_1.plot(x=xValue, y=df['ma60마지'], pen=r_dash,name='ma60마지')
        # p1_1.plot(x=xValue, y=df['ma300'], pen=g_dash,name='ma300')
        # p1_1.plot(x=xValue, y=df['ma300마지'], pen=(  0, 51,153),name='ma300마지')
        p1_1.plot(x=xValue, y=df['ma20'], pen=(200, 250, 50),name='ma20')
        # p1_1.plot(x=xValue, y=df['트레일링'], pen='g',name='트레일링')
        p1_1.plot(x=xValue, y=df['high'], pen=w_dot,name='high')
        p1_1.plot(x=xValue, y=df['close'], pen='r',name='close')
        p1_1.plot(x=xValue, y=df['low'], pen=w_dot,name='low')

        p1_1.plot(x=buy_index, y=buy_price,   pen =None, symbolBrush =(  200,  0, 0),symbolPen ='w', symbol='t1' , symbolSize=10, name="진입") #마커
        p1_1.plot(x=sell_index, y=sell_price, pen =None, symbolBrush =(0,  0,  200),symbolPen ='w', symbol='t', symbolSize=10, name="청산") #마커
        # lr = pg.LinearRegionItem([50, 100])
        # lr.setZValue(-1)
        # p1_1.addItem(lr)

        # p1_2.plot(x=xValue, y=df['고저평균대비등락율'],pen=(200, 50, 50),fillLevel=int(edit2),brush=(50,50,200,50),name='고저평균대비등락율')

        p1_2.plot(x=xValue, y=df['hmao_5'], pen=color_1, name='hmao_5')
        p1_2.plot(x=xValue, y=df['hmao_10'], pen=(255, 160, 0), name='hmao_10')
        p1_2.plot(x=xValue, y=df['hmao_20'], pen=(123, 94, 0), name='hmao_20')
        p1_2.plot(x=xValue, y=df['hmao_30'], pen=(65, 228, 0), name='hmao_30')
        p1_2.plot(x=xValue, y=df['hmac_5'], pen=(0, 216, 0), name='hmac_5')
        p1_2.plot(x=xValue, y=df['hmac_10'], pen=(0, 216, 255), name='hmac_10')
        p1_2.plot(x=xValue, y=df['hmac_20'], pen=(0, 0, 255), name='hmac_20')
        p1_2.plot(x=xValue, y=df['hmac_30'], pen=(95, 0, 255), name='hmac_30')
        # p1_2.plot(x=xValue, y=df['체결강도평균'],   pen=(204,114, 61), name='체결강도평균')
        # p1_2.plot(x=xValue, y=df['체결강도최고'],   pen=y_dot,         name='체결강도최고')
        # p1_2.plot(x=xValue, y=df['체결강도최저'],   pen=g_dot,         name='체결강도최저')
        # p1_2.plot(x=xValue, y=df['체결강도평균마지+'], pen=g_dash,        name='체결강도평균마지+')
        # p1_2.plot(x=xValue, y=df['체결강도평균마지-'], pen=g_dash,        name='체결강도평균마지-')

        # p1_3.plot(x=xValue, y=df['체강차체강평균'], pen=(50, 50, 200),name='체강차체강평균')
        # p1_3.plot(x=xValue, y=df['체결강도'], pen=(50, 100, 50),name='체결강도')
        p1_2.plot(x=xValue, y=df['band_lower'], pen=(152, 20, 20), brush=(50,50,200,50),name='band_l')
        p1_2.plot(x=xValue, y=df['band_upper'], pen=g_dot,name='band_u')
        p1_2.plot(x=xValue, y=df['band_middle'], pen=y_dot,name='band_m')
        # p1_3.plot(x=xValue, y=df['band_'], pen=y_dot,name='등락평균')

        p1_4.plot(x=xValue,y=df['rsi'], pen='r',fillLevel=int(edit3), brush=(50,50,200,50),name='rsi')
        p1_4.plot(x=xValue,y=df['rsi_upper'], pen='r',fillLevel=int(edit3), brush=(50,50,100,50),name='rsi_upper')
        p1_4.plot(x=xValue,y=df['rsi_lower'], pen='r',fillLevel=int(edit3), brush=(50,50,100,50),name='rsi_lower')

        # p1_5.plot(x=xValue, y=df['초당거래대금'], pen=(50, 50, 200),name='초당거래대금')
        # p1_5.plot(x=xValue, y=df['초당거래대금변동'], pen=(50, 50, 200),name='초당거래대금변동')
        p1_5.plot(x=xValue, y=df['rsi_gap'],     pen=(200, 50, 50),fillLevel=5,brush=(200,50,50,50),name='rsi_gap')
        p1_6.plot(x=xValue, y=df['거래대금평균최고'], pen=y_dot,name='거래대금평균최고')
        p1_6.plot(x=xValue, y=df['거래대금평균최고마지'], pen=g_dot,name='거래대금평균최고마지')
        p1_6.plot(x=xValue, y=df['초대금평균차초대금평균최고'],     pen=(120,200,200),name='초대금평균차초대금평균최고')
        # p1_5.plot(x=xValue, y=df['초당거래대금변동평균' ],pen=(128, 65,217),name='초당거래대금변동평균')


        p1_7.plot(x=xValue, y=df['거래대금평균60' ],  pen=(120,200,200), name='거래대금평균60')
        # p1_6.plot(x=xValue, y=df['초당거래대금평균120'],  pen=(128, 65,217), name='초당거래대금평균120')


        # p1_7.plot(x=xValue, y=df['수익률'],     pen=(152, 20, 20),name='수익률')
        # p1_7.plot(x=xValue, y=df['초당매도수량'],     pen=(20 , 50,150),name='초당매도수량')

        # p1_8.plot(x=xValue, y=df['value'], pen=(200, 50, 50),name='value')
        p1_8.plot(x=xValue, y=df['val_avg'], pen=y_dot,name='val_avg')
        p1_8.plot(x=xValue, y=df['val_avg_최'], pen=(120,200,200),name='val_avg_최')
        # p1_8.plot(x=xValue, y=df['초당거래대금평균'],     pen=(100, 50, 50),name='초당거래대금평균')


        p1_9.plot(x=xValue, y=df['hei_open'], pen=(152, 20, 20), name='hei_open')
        p1_9.plot(x=xValue, y=df['hei_close'], pen=(20, 50, 150), name='hei_close')

        # p1_9.plot(x=xValue, y=df['매도총잔량평균'], pen=(120,200,200),fillLevel=int(edit4), brush=(50,50,200,50),name='매도총잔량평균')
        # p1_9.plot(x=xValue, y=df['매도총잔량평균최고'], pen=y_dot,name='매도총잔량평균최고')
        # p1_9.plot(x=xValue, y=df['매수총잔량평균최저'], pen=w_dot,name='매수총잔량평균최저')
        # p1_9.plot(x=xValue, y=df['매도총잔량평균최저'], pen=g_dot,name='매도총잔량평균최저')


        p1_10.plot(x=xValue, y=df['value'], pen=(242,203, 95),fillLevel=int(edit5), brush=(50,50,200,50),name='value')
        # p1_10.plot(x=xValue, y=df['매수호가1'], pen=(255,  0,  0),name='매수호가1')
        # p1_10.plot(x=xValue, y=df['매수호가2'], pen=(255, 94,  0),name='매수호가2')
        # p1_10.plot(x=xValue, y=df['매도호가1'], pen=(  1,  0,255),name='매도호가1')
        # p1_10.plot(x=xValue, y=df['매도호가2'], pen=( 95,  0,255),name='매도호가2')


        # p1_11.plot(x=xValue, y=df['volume'], pen=(200, 50, 50),name='volume')

        p1_11.plot(x=xValue, y=df['hmao_20'], pen=(255, 94, 0), name='hmao_20')
        p1_11.plot(x=xValue, y=df['hmao_30'], pen=(255, 228, 0), name='hmao_30')
        p1_11.plot(x=xValue, y=df['hmac_20'], pen=(0, 216, 255), name='hmac_20')
        p1_11.plot(x=xValue, y=df['hmac_30'], pen=(95, 0, 255), name='hmac_30')
        # p1_11.plot(x=xValue, y=df['매수잔량1평균'], pen=(242, 203, 95), name='매수잔량1평균')
        # p1_11.plot(x=xValue, y=df['매도잔량1평균'], pen=(92, 210, 229), name='매도잔량1평균')
        # p1_11.plot(x=xValue, y=df['매도잔량1평균최고'], pen=(y_dot), name='매도잔량1평균최고')

        p1_12.plot(x=xValue, y=df['고저평균대비등락율절대'], pen=(242, 203, 95), fillLevel=int(edit5), brush=(50, 50, 200, 50),name='고저평균대비등락율절대')

        # p1_12.plot(x=xValue, y=df['매도잔량2'], pen=(20, 50, 150),name='매도잔량2')
        # p1_12.plot(x=xValue, y=df['매수잔량2평균'], pen=(242, 203, 95),name='매수잔량2평균')
        # p1_12.plot(x=xValue, y=df['매도잔량2평균'], pen=(92, 210, 229),name='매도잔량2평균')
        # p1_12.plot(x=xValue, y=df['매도잔량2평균최고'], pen=(y_dot), name='매도잔량2평균최고')

        # p2_1.plot(x=xValue, y=df['high'  ], pen=r_dash,       name='high')
        # p2_1.plot(x=xValue, y=df['low'  ], pen=r_dash,name='low')

        p2_1.plot(x=xValue, y=df['band_upper'], pen=(200, 50, 50), name='band_upper')
        p2_1.plot(x=xValue, y=df['band_middle'], pen=(128, 65, 217), name='band_middle')
        p2_1.plot(x=xValue, y=df['band_lower'], pen=(50, 50, 200), name='band_lower')
        p2_1.plot(x=xValue, y=df['ma5'],  pen=(255, 228, 0),name='ma5')
        p2_1.plot(x=xValue, y=df['ma20' ],pen=(0, 216, 255),name='ma20')
        # p2_1.plot(x=xValue, y=df['ma60' ], pen=(120,150,150),name='ma60')
        # p2_1.plot(x=xValue, y=df['ma60마지' ], pen=y_dot,name='ma60마지')
        # p2_1.plot(x=xValue, y=df['ma300' ], pen=(128, 65,217),name='ma300')
        # p2_1.plot(x=xValue, y=df['ma300마지' ], pen=g_dot,name='ma300마지')
        # p2_1.plot(x=xValue, y=df['ma'], pen=(204,114, 61),name='ma')
        p2_1.plot(x=xValue, y=df['high'], pen=w_dot,name='high')
        p2_1.plot(x=xValue, y=df['close'], pen='r',name='close')
        p2_1.plot(x=xValue, y=df['low'], pen=w_dot,name='close')
        p2_1.plot(x=buy_index, y=buy_price, pen=None, symbolBrush=(200, 0, 0), symbolPen='w', symbol='t1', symbolSize=10, name="진입")  # 마커
        p2_1.plot(x=sell_index, y=sell_price, pen=None, symbolBrush=(0, 0, 200), symbolPen='w', symbol='t', symbolSize=10, name="청산")  # 마커
        # lr = pg.LinearRegionItem([50, 100])
        # lr.setZValue(-1)
        # p1_1.addItem(lr)

        p2_2.plot(x=xValue, y=df['hmao_20'], pen=(255, 94, 0), name='hmao_20')
        p2_2.plot(x=xValue, y=df['hmao_30'],pen=(255, 228, 0), name='hmao_30')
        p2_2.plot(x=xValue, y=df['hmac_20'], pen=(0, 216, 255), name='hmac_20')
        p2_2.plot(x=xValue, y=df['hmac_30'], pen=(95, 0, 255), name='hmac_30')
        # p2_2.plot(x=xValue, y=df['거래대금평균최고마지'], pen=y_dot, name='거래대금평균최고마지')
        # p2_2.plot(x=xValue, y=df['초대금평균차초대금평균최고'], pen=g_dot, name='초대금평균차초대금평균최고')
        # p2_2.plot(x=xValue, y=df['체결강도평균마지+'], pen=g_dash, name='체결강도평균마지+')
        # p2_2.plot(x=xValue, y=df['체결강도평균마지-'], pen=g_dash, name='체결강도평균마지-')

        # p1_3.plot(x=xValue, y=df['체결강도'], pen=(50, 100, 50),name='체결강도')
        p2_3.plot(x=xValue, y=df['hei_open'], pen=(152, 20, 20), name='hei_open')

        p2_3.plot(x=xValue, y=df['hei_close'], pen=('b'), name='hei_close')


    # p2_3.plot(x=xValue, y=df['체강차체강평균최저'], pen=g_dot, name='체강-체강평균(최저)')
        # p2_3.plot(x=xValue, y=df['체강차체강평균최고'], pen=y_dot, name='체강-체강평균(최고)')

        p2_4.plot(x=xDate, y=df['hma'], pen='c', fillLevel=int(edit3), brush=(50, 50, 200, 50), name='hma')
        p2_4.plot(x=xDate, y=df['hma최고'], pen=g_dot, name='hma최고')
        p2_4.plot(x=xDate, y=df['hma최저'], pen=y_dot , name='hma최저')
        # p2_5.plot(x=xValue, y=df['초당거래대금'], pen=(50, 50, 200),name='초당거래대금')
        # p2_5.plot(x=xValue, y=df['초당거래대금변동'], pen=(50, 50, 200),name='초당거래대금변동')

        # p2_5.plot(x=xValue, y=df['cmo'], pen=(152, 20, 20), name='cmo')
        # p2_5.plot(x=xValue, y=df['cmo_5'], pen=(20, 50, 150), name='cmo_5')
        # p2_5.plot(x=xValue, y=df['cmo_20'], pen=(242, 203, 95), name='cmo_20')
        # p2_5.plot(x=xValue, y=df['cmo_30'], pen=(92, 210, 229), name='cmo_30')
        # p2_5.plot(x=xValue, y=df['cmo_60'], pen=(y_dot), name='cmo_60')
        p2_5.plot(x=xValue, y=df['hma_gap_l'], pen=(y_dot), name='hma_gap_l')


        p2_6.plot(x=xValue, y=df['hma_gap_h'], pen=(y_dot), name='hma_gap_h')
        # p2_6.plot(x=xValue, y=df['rsi'], pen=(152, 20, 20), name='rsi')

        p2_6.plot(x=xValue, y=df['rsi_upper'], pen=(128, 65, 217), name='rsi_upper')
        p2_6.plot(x=xValue, y=df['rsi_lower'], pen=(128, 65, 217), name='rsi_lower')
        # p2_6.plot(x=xValue, y=df['체결강도평균각도'], pen=(152, 20, 20), name='체결강도평균각도')
        # p2_6.plot(x=xValue, y=df['매도잔량2'], pen=(20, 50, 150), name='매도잔량2')
        # p2_6.plot(x=xValue, y=df['매수잔량2평균'], pen=(242, 203, 95), name='매수잔량2평균')
        # p2_6.plot(x=xValue, y=df['매도잔량2평균'], pen=(92, 210, 229), name='매도잔량2평균')
        # p2_6.plot(x=xValue, y=df['매도잔량2평균최고'], pen=(y_dot), name='매도잔량2평균최고')

        p2_7.plot(x=xValue, y=df['band_upper' ],pen=(200, 50, 50),name='band_upper')
        p2_7.plot(x=xValue, y=df['band_middle'],pen=(128, 65,217),name='band_middle')
        p2_7.plot(x=xValue, y=df['band_lower' ],pen=(50, 50, 200),name='band_lower')
        p2_7.plot(x=xValue, y=df['high'], pen=w_dot,name='high')
        p2_7.plot(x=xValue, y=df['close'], pen='r',name='close')
        p2_7.plot(x=xValue, y=df['low'], pen=w_dot,name='close')


        p2_8.plot(x=xValue, y=df['atr' ],pen=(50, 50, 200),name='atr')

        p2_9.plot(x=xValue, y=df['value'], pen=(255,  0,  0),name='value')


        p2_10.plot(x=xValue, y=df['value'], pen=(200, 50, 50), name='value')
        p2_10.plot(x=xValue, y=df['val_3'], pen=(100, 50, 50), name='val_3')
        p2_10.plot(x=xValue, y=df['val_5'], pen=(100, 50, 50), name='val_5')
        p2_10.plot(x=xValue, y=df['val_7'], pen=(100, 50, 50), name='val_7')
        p2_10.plot(x=xValue, y=df['val_10'], pen=(100, 50, 50), name='val_10')
        p2_10.plot(x=xValue, y=df['val_12'], pen=(100, 50, 50), name='val_12')
        p2_10.plot(x=xValue, y=df['val_15'], pen=(100, 50, 50), name='val_15')
        p2_10.plot(x=xValue, y=df['val_avg'], pen=y_dot, name='val_avg')
        p2_10.plot(x=xValue, y=df['val_avg_최'], pen=(120, 200, 200), name='val_avg_최')

        # p2_11.plot(x=xValue, y=df['val_rsi'], pen=(243,97,166), name='val_rsi')
        # p2_11.plot(x=xValue, y=df['val_rsi_5'], pen=(20, 50, 150), name='val_rsi_5')
        # p2_11.plot(x=xValue, y=df['val_rsi_20'], pen=(242, 203, 95), name='val_rsi_20')
        # p2_11.plot(x=xValue, y=df['val_rsi_30'], pen=(92, 210, 229), name='val_rsi_30')
        # p2_11.plot(x=xValue, y=df['val_rsi_60'], pen=(y_dot), name='val_rsi_60')

        # p2_6.plot(x=xValue, y=df['거래대금각도'], pen=(120, 200, 200), name='거래대금각도')
        p2_12.plot(x=xValue, y=df['고저평균대비등락율'], pen=(242, 203, 95), fillLevel=int(edit5), brush=(50, 50, 200, 50), name='고저평균대비등락율')
        # p1_6.plot(x=xValue, y=df['초당거래대금평균120'],  pen=(128, 65,217), name='초당거래대금평균120')

        crosshair.crosshair1(main_pg=p1_1, sub_pg1=p1_2, sub_pg2=p1_3,sub_pg3=p1_4,sub_pg4=p1_5,sub_pg5=p1_6,sub_pg6=p1_7,sub_pg7=p1_8,sub_pg8=p1_9,sub_pg9=p1_10,sub_pg10=p1_11,sub_pg11=p1_12)
        crosshair.crosshair2(main_pg=p2_1, sub_pg1=p2_2, sub_pg2=p2_3,sub_pg3=p2_4,sub_pg4=p2_5,sub_pg5=p2_6,sub_pg6=p2_7,sub_pg7=p2_8,sub_pg8=p2_9,sub_pg9=p2_10,sub_pg10=p2_11,sub_pg11=p2_12)

def df_add(df,avg,ch_max):
    avgtime = 30
    print(df)
    df = make_indicator.sma(df)
    df = make_indicator.CCI(df)
    df = make_indicator.CMO(df)
    df = make_indicator.RSI(df)
    df = make_indicator.df_add(df)
    df = make_indicator.BBAND(df)
    df = make_indicator.ATR(df)
    df = make_indicator.heikin_ashi(df)
    df['고저평균대비등락율'] = (df['close'] / ((df['high'] + df['low']) / 2) - 1) * 100
    df['고저평균대비등락율'] = df['고저평균대비등락율'].round(2)
    df['고저평균대비등락율절대'] = df['고저평균대비등락율'].abs()
    df['트레일링'] = df['close'].rolling(window=5).max()*0.98
    df['최고등락'] = (df['high']-df['low'])/df['low']*100
    df['최고등락평균'] = df['최고등락'].rolling(window=60).mean().round(3)
    df['등락'] = (df['close']-df['open'])/df['open']*100
    df['등락평균'] = df['등락'].rolling(window=60).mean().round(3)
    df['rsi_gap'] = df['rsi'] - df['rsi'].shift(1)
    # df['직전당일거래대금'] = df['당일거래대금'].shift(1)
    df['value'] = df['value']/((df['open']+df['close'])/2)
    df['거래대금차'] = df['value'] - df['value'].shift(1)
    # df['거래대금차'].iloc[0] = 0  # 초반 튀는값 잡기위해

    df['거래대금차평균'] = df['거래대금차'].rolling(window=avgtime).mean().round(3)
    # df['초당거래대금평균'] = df['초당거래대금평균'].round(3)
    # df.loc[df["초당거래대금평균"] > 거래대금max, "초당거래대금평균"] = 거래대금max
    # df.loc[df["초당거래대금평균"] < 거래대금min, "초당거래대금평균"] = 거래대금min

    df['직전거래대금차'] = df['거래대금차'].shift(1)
    df['거래대금변동'] = (df['직전거래대금차'] - df['거래대금차'])
    # df.loc[df["초당거래대금변동"] > 거래대금max, "초당거래대금변동"] = 거래대금max
    # df.loc[df["초당거래대금변동"] < 거래대금min, "초당거래대금변동"] = 거래대금min

    df['거래대금변동절대'] = abs(df['직전거래대금차'] - df['거래대금차'])
    df['거래대금변동평균'] = df['거래대금변동절대'].rolling(window=avgtime).mean().round(3)
    df['거래대금변동평균최고'] = df['거래대금변동절대'].rolling(window=avgtime).max()
    # df.loc[df["초당거래대금변동절대"] > 거래대금max, "초당거래대금변동절대"] = 거래대금max
    # df.loc[df["초당거래대금변동절대"] < 거래대금min, "초당거래대금변동절대"] = 거래대금min
    df['cmo_5']=df['cmo'].rolling(window=5).mean().round(3)
    df['cmo_20']=df['cmo'].rolling(window=20).mean().round(3)
    df['cmo_30']=df['cmo'].rolling(window=30).mean().round(3)
    df['cmo_60']=df['cmo'].rolling(window=60).mean().round(3)
    df['hmao_5'] = df['hei_open'].rolling(window=5).mean().round(3)
    df['hmao_10'] = df['hei_open'].rolling(window=10).mean().round(3)
    df['hmao_20']=df['hei_open'].rolling(window=20).mean().round(3)
    df['hmao_30']=df['hei_open'].rolling(window=30).mean().round(3)
    df['hmac_5'] = df['hei_close'].rolling(window=5).mean().round(3)
    df['hmac_10'] = df['hei_close'].rolling(window=10).mean().round(3)
    df['hmac_20']=df['hei_close'].rolling(window=20).mean().round(3)
    df['hmac_30']=df['hei_close'].rolling(window=30).mean().round(3)
    df['hma']=df['hmac_20']-df['hmac_30']
    df['hma최고']=df['hma'].rolling(window=5).max()
    df['hma최저']=df['hma'].rolling(window=5).min()
    df['hma_gap_l'] = df['hma']-df['hma최저']
    df['hma_gap_h'] = df['hma최고']-df['hma']
    # df['val_rsi']=round(talib.RSI(df['value'], timeperiod=14), 1)
    # df['val_rsi_5']=df['val_rsi'].rolling(window=5).mean().round(3)
    # df['val_rsi_20']=df['val_rsi'].rolling(window=20).mean().round(3)
    # df['val_rsi_30']=df['val_rsi'].rolling(window=30).mean().round(3)
    # df['val_rsi_60']=df['val_rsi'].rolling(window=60).mean().round(3)

    df['거래대금평균최고'] = df['거래대금차평균'].rolling(window=avgtime).max()
    df['거래대금평균최고'] = df['거래대금평균최고'].round(3)
    df['거래대금평균최고마지'] = df['거래대금평균최고']*0.9
    # df.loc[df["초당거래대금평균최고"] > 거래대금max, "초당거래대금평균최고"] = 거래대금max
    # df.loc[df["초당거래대금평균최고"] < 거래대금min, "초당거래대금평균최고"] = 거래대금min
    df['초대금평균차초대금평균최고'] = abs(df['거래대금차평균'] - df['거래대금평균최고'])

    df['거래대금평균60'] = df['거래대금차'].rolling(window=60).mean()
    df['거래대금평균60'] = df['거래대금평균60'].round(3)

    df['거래대금평균120'] = df['거래대금차'].rolling(window=120).mean()
    df['거래대금평균120'] = df['거래대금평균120'].round(3)

    df['거래대금각도'] = np.arctan((df['value']-df['value'].shift(1))/1000) * 180 / np.pi

    df['val_avg'] = df['value'].rolling(window=avgtime).mean().round(3)
    df['val_3'] = df['value'].rolling(window=3).mean().round(3)
    df['val_5'] = df['value'].rolling(window=5).mean().round(3)
    df['val_7'] = df['value'].rolling(window=7).mean().round(3)
    df['val_10'] = df['value'].rolling(window=10).mean().round(3)
    df['val_12'] = df['value'].rolling(window=12).mean().round(3)
    df['val_15'] = df['value'].rolling(window=15).mean().round(3)
    df['val_avg_최'] = df['val_avg'].rolling(window=5).max().round(3)

    # df['초당매수대금평균'] = df['초당매수대금평균'].round(3)

    # df['초당매도대금평균'] = df['초당매도대금'].rolling(window=avgtime).mean()
    # df['초당매도대금평균'] = df['초당매도대금평균'].round(3)


    # df['초당매도대금평균최고'] = df['초당매도대금평균'].rolling(window=avgtime).max()
    # df['초당매도대금평균최고'] = df['초당매도대금평균최고'].round(3)


    df['매수가'] = np.nan
    df['매도가'] = np.nan
    # df.to_csv(path+'/database/' + stock_name + ".csv", header=True, index=True, encoding='utf-8-sig')
    return df
if __name__ == '__main__':
    path = "D:/db_files"
    ohlcv_file = path + '/upbit.db'
    back_file = path + '/upbit_backtest.db'

    start = '00:01'
    end = '24:59'
    delay = 20000 #차멍 딜레이시간 ms(밀리세컨)
    gap_interval = 100
    # stock_code = '1INCH-minute3'
    # sell_time = '20220325230900'
    # buy_time = '20220325224800'
    # buy_time=str(buy_time)[4:8]
    # sell_time=str(sell_time)[4:8]
    # df=get_data(stock_code='1INCH-minute3',buy_time=buy_time,sell_time=sell_time)

    app = QApplication(sys.argv)
    w = Window()
    w.show()
    sys.exit(app.exec_())