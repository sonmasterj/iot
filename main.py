import os
from turtle import left

from matplotlib.pyplot import title
import assets_qrc
from random import randint
from PyQt5.QtWidgets import QFileDialog, QMainWindow,QApplication,QTableWidgetItem,  QDialog,QMessageBox,QGraphicsDropShadowEffect,QFileDialog
from PyQt5 import uic
from PyQt5.QtCore import Qt,QThread,pyqtSignal, QTimer,QDate,QTime
from PyQt5.QtGui import QColor,QPixmap
import pyqtgraph as pg
from analoggaugewidget import AnalogGaugeWidget
import sys
from datetime import datetime
import socket
import xlsxwriter as xlsx
view_path = 'iot.ui'
application_path =os.path.dirname(os.path.abspath(__file__)) 
curren_path = os.path.join(application_path,os.pardir)

def checkInternet():
    host='1.1.1.1'
    port = 53
    timeout = 3
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False
def timestamp():
    return (datetime.now().timestamp())


class TimeAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setLabel(text='Thời gian', units=None)
        self.enableAutoSIPrefix(False)

    def tickStrings(self, values, scale, spacing):
        return [datetime.fromtimestamp(value).strftime("%H:%M:%S.%f")[:-5] for value in values]
class Main(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(view_path,self)
        self.stackedWidget.setCurrentIndex(0)
        self.query = None
        self.queryResult = None
        self.pageResult = 0
        self.totalPage = 0
        self.numItem = 20

        #set button events
        self.btn_home.clicked.connect(self.goHome)
        self.btn_history.clicked.connect(self.goHistory)
        self.btn_exit.clicked.connect(self.goClose)

        self.btn_off.clicked.connect(self.goClose)

        self.btn_temp.clicked.connect(self.goTemp)
        self.btn_humid.clicked.connect(self.goHumid)
        self.btn_press.clicked.connect(self.goPress)
        self.btn_o2kk.clicked.connect(self.goO2kk)
        self.btn_co2.clicked.connect(self.goCo2)
        self.btn_sound.clicked.connect(self.goSound)
        self.btn_ph.clicked.connect(self.goPh)
        self.btn_o2n.clicked.connect(self.goO2n)
        self.btn_elec.clicked.connect(self.goElec)

        

        #init qdate
        now = datetime.now()
        qdate = QDate(now.year,now.month,now.day)
        qtime = QTime(now.hour,now.minute,now.second)
        self.date_start.setMaximumDate(qdate)
        # self.date_start.setMaximumTime(qtime)

        self.date_end.setMaximumDate(qdate)
        # self.date_end.setMaximumTime(qtime)
        self.date_start.setDate(qdate)
        self.date_start.setTime(qtime)
        self.date_end.setDate(qdate)
        self.date_end.setTime(qtime)

        pg.setConfigOption('foreground', 'k')


        #page temperature
        self.graphTemp = pg.PlotWidget(title='Đồ thị nhiệt độ',axisItems={'bottom': TimeAxisItem(orientation='bottom')},left=u'Nhiệt độ(℃)')
        self.graphTemp.setMenuEnabled(False)
        self.graphTemp.setBackground('w')
        self.verticalLayout_6.addWidget(self.graphTemp,0)

        self.gaugeTemp = AnalogGaugeWidget()
        self.gaugeTemp.value_min =0
        self.gaugeTemp.enable_barGraph = True
        self.gaugeTemp.value_needle_snapzone = 1
        self.gaugeTemp.value_max =80
        self.gaugeTemp.scala_main_count=8
        self.gaugeTemp.set_enable_CenterPoint(False)
        self.gaugeTemp.update_value(11.5)
        self.verticalLayout_6.addWidget(self.gaugeTemp,1)
        self.verticalLayout_6.setStretch(0, 1)
        self.verticalLayout_6.setStretch(1, 1)

        #page humidity
        self.graphHumid = pg.PlotWidget(title='Đồ thị độ ẩm',axisItems={'bottom': TimeAxisItem(orientation='bottom')},left=u'Độ ẩm(%)')
        self.graphHumid.setMenuEnabled(False)
        self.graphHumid.setBackground('w')
        self.verticalLayout_7.addWidget(self.graphHumid,0)

        self.gaugeHumid = AnalogGaugeWidget()
        self.gaugeHumid.value_min =0
        self.gaugeHumid.enable_barGraph = True
        self.gaugeHumid.value_needle_snapzone = 1
        self.gaugeHumid.value_max =100
        self.gaugeHumid.scala_main_count=10
        self.gaugeHumid.set_enable_CenterPoint(False)
        self.gaugeHumid.update_value(11.5)
        self.verticalLayout_7.addWidget(self.gaugeHumid,1)
        self.verticalLayout_7.setStretch(0, 1)
        self.verticalLayout_7.setStretch(1, 1)

        #page press
        self.graphPress = pg.PlotWidget(title='Đồ thị áp suất',axisItems={'bottom': TimeAxisItem(orientation='bottom')},left=u'Áp suất(kPa)')
        self.graphPress.setMenuEnabled(False)
        self.graphPress.setBackground('w')
        self.verticalLayout_8.addWidget(self.graphPress,0)

        self.gaugePress = AnalogGaugeWidget()
        self.gaugePress.value_min =0
        self.gaugePress.enable_barGraph = True
        self.gaugePress.value_needle_snapzone = 1
        self.gaugePress.value_max =150
        self.gaugePress.scala_main_count=15
        self.gaugePress.set_enable_CenterPoint(False)
        self.gaugePress.update_value(11.5)
        self.verticalLayout_8.addWidget(self.gaugePress,1)
        self.verticalLayout_8.setStretch(0, 1)
        self.verticalLayout_8.setStretch(1, 1)

        #page O2 KK
        self.graphO2kk = pg.PlotWidget(title='Đồ thị nồng độ O2 trong không khí',axisItems={'bottom': TimeAxisItem(orientation='bottom')},left=u'N.độ O2 trong không khí(%Vol)')
        self.graphO2kk.setMenuEnabled(False)
        self.graphO2kk.setBackground('w')
        self.verticalLayout_9.addWidget(self.graphO2kk,0)

        self.gaugeO2kk = AnalogGaugeWidget()
        self.gaugeO2kk.value_min =0
        self.gaugeO2kk.enable_barGraph = True
        self.gaugeO2kk.value_needle_snapzone = 1
        self.gaugeO2kk.value_max =30
        self.gaugeO2kk.scala_main_count=6
        self.gaugeO2kk.set_enable_CenterPoint(False)
        self.gaugeO2kk.update_value(11.5)
        self.verticalLayout_9.addWidget(self.gaugeO2kk,1)
        self.verticalLayout_9.setStretch(0, 1)
        self.verticalLayout_9.setStretch(1, 1)


        #page CO2
        self.graphCO2 = pg.PlotWidget(title='Đồ thị nồng độ CO2',axisItems={'bottom': TimeAxisItem(orientation='bottom')},left=u'Nồng độ CO2(ppm)')
        self.graphCO2.setMenuEnabled(False)
        self.graphCO2.setBackground('w')
        self.verticalLayout_10.addWidget(self.graphCO2,0)

        self.gaugeCO2 = AnalogGaugeWidget()
        self.gaugeCO2.value_min =0
        self.gaugeCO2.enable_barGraph = True
        self.gaugeCO2.value_needle_snapzone = 1
        self.gaugeCO2.value_max =5000
        self.gaugeCO2.scala_main_count=10
        self.gaugeCO2.set_enable_CenterPoint(False)
        self.gaugeCO2.update_value(100)
        self.verticalLayout_10.addWidget(self.gaugeCO2,1)
        self.verticalLayout_10.setStretch(0, 1)
        self.verticalLayout_10.setStretch(1, 1)


        #page sound
        self.graphSound = pg.PlotWidget(title='Đồ thị cường độ âm thanh',axisItems={'bottom': TimeAxisItem(orientation='bottom')},left=u'Cường độ âm thanh(dBA)')
        self.graphSound.setMenuEnabled(False)
        self.graphSound.setBackground('w')
        self.verticalLayout_11.addWidget(self.graphSound,0)

        self.gaugeSound = AnalogGaugeWidget()
        self.gaugeSound.value_min =0
        self.gaugeSound.enable_barGraph = True
        self.gaugeSound.value_needle_snapzone = 1
        self.gaugeSound.value_max =130
        self.gaugeSound.scala_main_count=13
        self.gaugeSound.set_enable_CenterPoint(False)
        self.gaugeSound.update_value(50)
        self.verticalLayout_11.addWidget(self.gaugeSound,1)
        self.verticalLayout_11.setStretch(0, 1)
        self.verticalLayout_11.setStretch(1, 1)


        #page PH
        self.graphPH = pg.PlotWidget(title='Đồ thị độ PH',axisItems={'bottom': TimeAxisItem(orientation='bottom')},left=u'PH(pH)')
        self.graphPH.setMenuEnabled(False)
        self.graphPH.setBackground('w')
        self.verticalLayout_12.addWidget(self.graphPH,0)

        self.gaugePH = AnalogGaugeWidget()
        self.gaugePH.value_min =0
        self.gaugePH.enable_barGraph = True
        self.gaugePH.value_needle_snapzone = 1
        self.gaugePH.value_max =14
        self.gaugePH.scala_main_count=14
        self.gaugePH.set_enable_CenterPoint(False)
        self.gaugePH.update_value(7)
        self.verticalLayout_12.addWidget(self.gaugePH,1)
        self.verticalLayout_12.setStretch(0, 1)
        self.verticalLayout_12.setStretch(1, 1)


        #page O2 nuoc
        self.graphO2n = pg.PlotWidget(title='Đồ thị nồng độ O2 trong nước',axisItems={'bottom': TimeAxisItem(orientation='bottom')},left=u'Nồng độ O2 trong nước(mg/L)')
        self.graphO2n.setMenuEnabled(False)
        self.graphO2n.setBackground('w')
        self.verticalLayout_13.addWidget(self.graphO2n,0)

        self.gaugeO2n = AnalogGaugeWidget()
        self.gaugeO2n.value_min =0
        self.gaugeO2n.enable_barGraph = True
        self.gaugeO2n.value_needle_snapzone = 1
        self.gaugeO2n.value_max =20
        self.gaugeO2n.scala_main_count=4
        self.gaugeO2n.set_enable_CenterPoint(False)
        self.gaugeO2n.update_value(7)
        self.verticalLayout_13.addWidget(self.gaugeO2n,1)
        self.verticalLayout_13.setStretch(0, 1)
        self.verticalLayout_13.setStretch(1, 1)

        #page Electron
        self.graphElec = pg.PlotWidget(title='Đồ thị độ dẫn điện',axisItems={'bottom': TimeAxisItem(orientation='bottom')},left=u'Độ dẫn điện(ms/cm)')
        self.graphElec.setMenuEnabled(False)
        self.graphElec.setBackground('w')
        self.verticalLayout_14.addWidget(self.graphElec,0)

        self.gaugeElec = AnalogGaugeWidget()
        self.gaugeElec.value_min =0
        self.gaugeElec.enable_barGraph = True
        self.gaugeElec.value_needle_snapzone = 1
        self.gaugeElec.value_max =100
        self.gaugeElec.scala_main_count=10
        self.gaugeElec.set_enable_CenterPoint(False)
        self.gaugeElec.update_value(10)
        self.verticalLayout_14.addWidget(self.gaugeElec,1)
        self.verticalLayout_14.setStretch(0, 1)
        self.verticalLayout_14.setStretch(1, 1)

        self.show()




        

        
    

    # go to Page
    def goHome(self):
        self.stackedWidget.setCurrentIndex(0)  
    def goHistory(self):
        self.stackedWidget.setCurrentIndex(10)
    
    def goClose(self):
        # self.readSensor.stop()
        # self.readStatus.stop()
        # self.timer.stop()
        # db_close()
        self.close()
    
    def goTemp(self):
        self.stackedWidget.setCurrentIndex(1)  
    def goHumid(self):
        self.stackedWidget.setCurrentIndex(2)
    def goPress(self):
        self.stackedWidget.setCurrentIndex(3)
    def goO2kk(self):
        self.stackedWidget.setCurrentIndex(4)  
    def goCo2(self):
        self.stackedWidget.setCurrentIndex(5)
    def goSound(self):
        self.stackedWidget.setCurrentIndex(6)
    def goPh(self):
        self.stackedWidget.setCurrentIndex(7)  
    def goO2n(self):
        self.stackedWidget.setCurrentIndex(8)
    def goElec(self):
        self.stackedWidget.setCurrentIndex(9)

if __name__ == "__main__":
    # creat_table()
    app = QApplication(sys.argv)
    # window = Home("s")
    # window.show()
    win = Main()
    # win.show()
    app.exec_()