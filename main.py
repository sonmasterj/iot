import os
import glob
import sys
import subprocess
from tokenize import String
# import signal
# from matplotlib.pyplot import title
import assets_qrc
# from random import randint
from PyQt5.QtWidgets import  QMainWindow,QApplication,QTableWidgetItem,QMessageBox,QHeaderView,QTabWidget,QInputDialog
from PyQt5 import uic
from PyQt5.QtCore import Qt,QThread,pyqtSignal, QTimer,QDate,QTime,QObject
from PyQt5.QtGui import QIcon,QGuiApplication,QRegion,QPixmap,QColor,QBrush
import pyqtgraph as pg
from analoggaugewidget import AnalogGaugeWidget
from mail import Mail
import sys
from datetime import datetime
import socket
import RPi.GPIO as GPIO
from ultil.asyncSleep import delay
from sensors.ds18b20 import DS18B20
from sensors.co2 import MHZ19
from sensors.sht31 import SHT31
from sensors.bmp280 import BMP280
from sensors.airoxigen import DFRobot_Oxygen_IIC
from sensors.wateroxigen import convertWaterOxygen
from sensors.ph import convertPH
from sensors.ec import convertEC
from sensors.ADS1x15 import ADS1115
from sensors.battery import UPS2
import smbus
from collections import deque
from database.model import creat_table,db_close,Temp,CO2,Analog,Digital,Sound,db_rollback,Setting
view_path = 'iot.ui'
# application_path =os.path.dirname(os.path.abspath(__file__)) 
# curren_path = os.path.join(application_path,os.pardir)
# print(curren_path)
# win = None
# mypid= os.getpid()
from ultil.spinner import QtWaitingSpinner
from sensors.wifi import WiFiManager
# from asyncqt import QEventLoop
# import asyncio
try:
    CHECK_INTERVAL = 1500
    INTERNET_INTERVAL = 5000

    SLOW_INTERVAL = 4000
    FAST_INTERVAL = 300
    MAX_STEPS = 10
    TIME_MEASURE = 5 # 5 phut

    add1_1=13
    add1_2=16
    add1_3=26

    add2_1=23
    add2_2=27
    add2_3=17

    ada1_1=22
    ada1_2=24
    ada1_3=10

    ada2_1=11
    ada2_2=8
    ada2_3=9

    ada3_1=1
    ada3_2=0
    ada3_3=7

    ada4_1=12
    ada4_2=6
    ada4_3=5

    tempEnable = False

    ADC_GAIN = 1
    adc_adapter = ADS1115()
    
    gpio_adapter = GPIO
    gpio_adapter.setmode(gpio_adapter.BCM)
    list_pins=[add1_1,add1_2,add1_3, add2_1,add2_2,add2_3,ada1_1,ada1_2,ada1_3,ada2_1,ada2_2,ada2_3,ada3_1,ada3_2,ada3_3,ada4_1,ada4_2,ada4_3]
    for pin in list_pins:
        try:
            gpio_adapter.setup(pin,gpio_adapter.IN, pull_up_down=gpio_adapter.PUD_UP)
        except Exception as ex:
            print('error set up pin ',pin)

    def convertTime(time):
        t = datetime.fromtimestamp(time)
        return t.strftime('%d/%m/%Y %H:%M:%S:%f')[:-5]
    def checkInternet():
        host='1.1.1.1'
        port = 53
        timeout = 3
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            return 1
        except socket.error:
            return 0
    def timestamp():
        return (datetime.now().timestamp())
    
    def parseWifiScan(dt):
        res = dt.split('\n')
        list_wifi=[]
        old_connect=''
        for item in res:
            if len(item)>0:
                val = item.split(':')
                temp = {
                    'status':val[0],
                    'ssid':val[1],
                    'signal':val[2]+'%',
                    'security':val[3]
                }
                if temp not in list_wifi:
                    list_wifi.append(temp)
                if val[0]=='yes':
                    old_connect=val[1]
        return list_wifi,old_connect

    # thread wifi 
    class wifiThread(QThread):
        updateData = pyqtSignal(object)
        def __init__(self,*args, **kwargs):
            super().__init__(*args, **kwargs)
            self.threadActive = True
            self.wifi = WiFiManager()
            self.cmd=''
            self.data={}
        def run(self):
            while self.threadActive == True:
                if len(self.cmd)>0:
                    res=''
                    if self.cmd=='scan':
                        res =self.wifi.scan()
                    elif self.cmd=='rescan':
                        res = self.wifi.rescan()
                        self.cmd='scan'
                    elif self.cmd=='connect':
                        # print(self.data)
                        res = self.wifi.connectWifi(self.data['ssid'],self.data['password'],self.data['oldWifi'])
                    self.updateData.emit({
                        'cmd':self.cmd,
                        'result':res
                    })
                    self.cmd=''
                else:
                    self.msleep(200)


        def stop(self):
            self.threadActive = False
            # self.terminate()
            # self.wait()
            self.quit()    

    #thread check sensor
    class checkThread(QThread):
        updateStatus = pyqtSignal(list)
        def __init__(self,*args, **kwargs):
            super().__init__(*args, **kwargs)
            self.threadActive = True
            self.interval = CHECK_INTERVAL
            self.step = self.interval/MAX_STEPS
            
        def run(self):
            global tempEnable
            global gpio_adapter
            while self.threadActive == True:
               
                dt_pin=[]
                dt_sensor=[0]*10
                for pin in list_pins:
                    val = gpio_adapter.input(pin)
                    dt_pin.append(val)
                portD_1= dt_pin[0]+dt_pin[1]*2+dt_pin[2]*4
                portD_2= dt_pin[3]+dt_pin[4]*2+dt_pin[5]*4
                # print(portD_1)

                portA_1= dt_pin[6]+dt_pin[7]*2+dt_pin[8]*4
                portA_2= dt_pin[9]+dt_pin[10]*2+dt_pin[11]*4
                portA_3= dt_pin[12]+dt_pin[13]*2+dt_pin[14]*4
                portA_4= dt_pin[15]+dt_pin[16]*2+dt_pin[17]*4
                #check cam bien nhiet do
                if portA_1==5 or portA_2==5 or portA_3==5 or portA_4==5:
                    dt_sensor[0]=1
                
                
                #check cam bien do am
                if portD_1==4 or portD_2==4:
                    dt_sensor[1]=1
                
                #check cam bien ap suat
                if portD_1==2 or portD_2==2:
                    dt_sensor[2]=1
                
                #check cam bien o2 kk
                if portD_1==6 or portD_2==6:
                    dt_sensor[3]=1
                
                #check cam bien Co2
                if portD_1==1 or portD_2==1:
                    dt_sensor[4]=1
                
                #check cam bien luc
                if portD_1 ==5 or portD_2==5:
                    dt_sensor[9]=1
                
                #check cam bien am thanh
                if portA_1==1 or portA_2==1 or portA_3==1 or portA_4==1:
                    dt_sensor[5]=1

                #check cam bien PH
                if portA_1==2 or portA_2==2 or portA_3==2 or portA_4==2:
                    dt_sensor[6]=1

                #check cam bien o2 nuoc
                if portA_1==4 or portA_2==4 or portA_3==4 or portA_4==4:
                    dt_sensor[7]=1
                
                #check cam bien do dan dien
                if portA_1==6 or portA_2==6 or portA_3==6 or portA_4==6:
                    dt_sensor[8]=1             
                self.updateStatus.emit(dt_sensor)
                if dt_sensor[0]==1 and tempEnable==False :
                    # delay(2000)
                    try:
                        base_dir = '/sys/bus/w1/devices/'
                        device_folder = glob.glob(base_dir + '28*')[0]
                        # device_file = device_folder + '/w1_slave'
                        # tempSensor = DS18B20(device_file)
                        tempEnable = True
                        print('set up done ds18b20!')
                    except:
                        pass
                i=0
                while i<self.step and self.threadActive == True:
                    i=i+1
                    self.msleep(MAX_STEPS)
                
        def stop(self):
            self.threadActive = False
            # self.terminate()
            # self.wait()
            self.quit()

    class batteryThread(QThread):
        updateBat = pyqtSignal(object)
        def __init__(self,*args, **kwargs):
            global adc_adapter
            super().__init__(*args, **kwargs)
            self.threadActive = True
            self.interval = SLOW_INTERVAL-2000
            self.bat = UPS2()
            self.step = self.interval/MAX_STEPS
        
        def run(self):
            while self.threadActive == True:
                try:
                    vin,batcap = self.bat.decode_uart()
                    
                    dt={
                        'vin':vin,
                        'batcap':batcap
                    }
                    self.updateBat.emit(dt)
                except Exception as ex:
                    print(ex)
                    pass
                i=0
                while i< self.step and self.threadActive == True:
                    i=i+1
                    self.msleep(MAX_STEPS)
        def stop(self):
            self.threadActive = False
            self.bat.close_serial()
            # self.terminate()
            self.quit()
    
    class soundThread(QThread):
        updateDt = pyqtSignal(object)
        def __init__(self,*args, **kwargs):
            global adc_adapter
            super().__init__(*args, **kwargs)
            self.threadActive = True
            self.interval = FAST_INTERVAL
            self.adc = adc_adapter
            self.step = self.interval/MAX_STEPS
        
        def run(self):
            global gpio_adapter
            while self.threadActive == True:
                
                sound = 0.0
                if gpio_adapter.input(ada1_2)==0 and gpio_adapter.input(ada1_3)==0:
                    vol = self.adc.read_adc(0,gain=ADC_GAIN)*4.096/32767.0
                    sound = round(vol*50-12,1)
                elif gpio_adapter.input(ada2_2)==0 and gpio_adapter.input(ada2_3)==0:
                    vol = self.adc.read_adc(1,gain=ADC_GAIN)*4.096/32767.0
                    sound = round(vol*50-12,1)
                elif gpio_adapter.input(ada3_2)==0 and gpio_adapter.input(ada3_3)==0:
                    vol = self.adc.read_adc(2,gain=ADC_GAIN)*4.096/32767.0
                    sound = round(vol*50-12,1)
                elif gpio_adapter.input(ada4_2)==0 and gpio_adapter.input(ada4_3)==0:
                    vol = self.adc.read_adc(3,gain=ADC_GAIN)*4.096/32767.0
                    sound = round(vol*50-12,1)
                if sound<0:
                    sound = 0.0
                dt={
                    'time':timestamp(),
                    'sound':sound
                }
                self.updateDt.emit(dt)
                i=0
                while i< self.step and self.threadActive == True:
                    i=i+1
                    self.msleep(MAX_STEPS)
        def stop(self):
            self.threadActive = False
            # self.terminate()
            self.quit()
            # self.wait()

    class tempThread(QThread):
        updateDt = pyqtSignal(object)
        def __init__(self,*args, **kwargs):
            super().__init__(*args, **kwargs)
            self.threadActive = True
            self.interval = SLOW_INTERVAL-900
            self.temp = None
            self.step = self.interval/MAX_STEPS

        def run(self):
            global tempEnable
            while self.threadActive == True:
                _temp=0.0
                if tempEnable == True:
                    if self.temp == None:
                        base_dir = '/sys/bus/w1/devices/'
                        device_folder = glob.glob(base_dir + '28*')[0]
                        device_file = device_folder + '/w1_slave'
                        self.temp = DS18B20(device_file)
                        _temp = self.temp.readTemp()
                        # self.msleep(100)
                    else:
                        _temp = self.temp.readTemp()
                now = timestamp()
                dt={
                    'time':now,
                    'temp':_temp
                }
                self.updateDt.emit(dt)
                # self.updateDt.emit()
                i=0
                while i< self.step and self.threadActive == True:
                    i=i+1
                    self.msleep(MAX_STEPS)
                
        def stop(self):
            self.threadActive = False
            # self.terminate()
            # self.wait()
            self.quit()

    #reading sensor thread
    class digitalThread(QThread):
        updateDt = pyqtSignal(object)
        def __init__(self,*args, **kwargs):
            super().__init__(*args, **kwargs)
            self.threadActive = True
            self.interval = SLOW_INTERVAL
            bus = smbus.SMBus(1)
            self.humid = SHT31(bus)
            self.air_oxy = DFRobot_Oxygen_IIC(bus=bus,addr=0x73)
            self.press = BMP280(bus)
            self.step = self.interval/MAX_STEPS
            


        def run(self):
            while self.threadActive == True:
                _humid = self.humid.read_data()
                _air_oxy = round(self.air_oxy.get_oxygen_data(10),1)
                _press = round(self.press.readPress(),1)
                now = timestamp()
                dt={
                    'time':now,
                    'humid':_humid,
                    'press':_press,
                    'air_oxy':_air_oxy,
                }    
                self.updateDt.emit(dt) 
                i=0
                while i< self.step and self.threadActive == True:
                    i=i+1
                    self.msleep(MAX_STEPS)
        def stop(self):
            self.threadActive = False
            # self.terminate()
            # self.wait()
            self.quit()
    
    #analog sensor
    class analogThread(QThread):
        updateDt = pyqtSignal(object)
        def __init__(self,*args, **kwargs):
            global adc_adapter
            super().__init__(*args, **kwargs)
            self.threadActive = True
            self.interval = SLOW_INTERVAL
            self.adc = adc_adapter
            self.step = self.interval/MAX_STEPS
            

        def run(self):
            global gpio_adapter
            global list_pins
            while self.threadActive == True:
                #read adc
                # start = timestamp()
                raw_adc = [0,0,0,0]
                for i in range(3):
                    raw_adc[0]= raw_adc[0]+ self.adc.read_adc(0,gain=ADC_GAIN)
                    raw_adc[1]= raw_adc[1]+ self.adc.read_adc(1,gain=ADC_GAIN)
                    raw_adc[2]= raw_adc[2]+ self.adc.read_adc(2,gain=ADC_GAIN)
                    raw_adc[3]= raw_adc[3]+ self.adc.read_adc(3,gain=ADC_GAIN)
                    delay(0.05)
                
                
                for i in range(4):
                    raw_adc[i] = raw_adc[i]/3.0
                
                listPin_status=[]
                for i in range(6,18):
                    listPin_status.append(gpio_adapter.input(list_pins[i]))
                
                
                portA_1 = listPin_status[0]+listPin_status[1]*2+listPin_status[2]*4
                portA_2 = listPin_status[3]+listPin_status[4]*2+listPin_status[5]*4
                portA_3 = listPin_status[6]+listPin_status[7]*2+listPin_status[8]*4
                portA_4 = listPin_status[9]+listPin_status[10]*2+listPin_status[11]*4
                
                portA=[portA_1,portA_2,portA_3,portA_4]
                # print(portA)
                #check ph sensor
                _ph=0.0
                if portA_1==2 or portA_2==2 or portA_3==2 or portA_4==2:
                    for i in range(4):
                        if portA[i]==2:
                            _ph = convertPH(raw_adc[i])
                            break

                #check water oxy sensor
                _water_oxy=0.0
                if portA_1==4 or portA_2==4 or portA_3==4 or portA_4==4:
                    for i in range(4):
                        if portA[i]==4:
                            _water_oxy = convertWaterOxygen(raw_adc[i])
                            break  
                #check ec sensor
                _ec=0.0
                if portA_1==6 or portA_2==6 or portA_3==6 or portA_4==6:
                    for i in range(4):
                        if portA[i]==6:
                            _ec = convertEC(raw_adc[i])
                            break       
                  

                dt={
                    'pH':_ph,
                    'water_oxy':_water_oxy,
                    'ec':_ec,
                    'time':timestamp()
                }    
                # end = timestamp()
                # print('time analog reading:',end-start)
                self.updateDt.emit(dt) 
                i=0
                while i< self.step and self.threadActive == True:
                    i=i+1
                    self.msleep(MAX_STEPS)
                
        def stop(self):
            self.threadActive = False
            # self.terminate()
            # self.wait()
            self.quit()
    #reading co2 thread
    class co2Thread(QThread):
        updateDt = pyqtSignal(object)
        def __init__(self,*args, **kwargs):
            super().__init__(*args, **kwargs)
            self.threadActive = True
            self.interval = SLOW_INTERVAL
            self.co2 = MHZ19()
            self.step = self.interval/MAX_STEPS

        def run(self):
            
            while self.threadActive == True:
                val = self.co2.read_concentration()
                dt={
                    'co2':val,
                    'time':timestamp()
                }
                self.updateDt.emit(dt)
                i=0
                while i< self.step and self.threadActive == True:
                    i=i+1
                    self.msleep(MAX_STEPS)
                
        def stop(self):
            self.threadActive = False
            self.co2.close_serial()
            # self.terminate()
            # self.wait()
            self.quit()
    


    class internetThread(QThread):
        updateStatus = pyqtSignal(str)
        def __init__(self,*args, **kwargs):
            super().__init__(*args, **kwargs)
            self.threadActive = True
            self.interval = INTERNET_INTERVAL
            self.step = self.interval/MAX_STEPS
            
        def run(self):
            while self.threadActive == True:
                internet_status = checkInternet()
                self.updateStatus.emit(str(internet_status))
                i=0
                while i< self.step and self.threadActive == True:
                    i=i+1
                    self.msleep(MAX_STEPS)
        def stop(self):
            self.threadActive = False
            # self.terminate()
            # self.wait()
            self.quit()


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
            self.setWindowFlags(Qt.FramelessWindowHint)
            self.showMaximized()

            self.loading = QtWaitingSpinner(parent=self)
            # self.wifi = WiFiManager()
            self.oldSsid = ''
            self.query = None
            self.queryResult = None
            self.pageResult = 0
            self.totalPage = 0
            self.numItem = 20
            self.listSensorStatus=[0]*10
            self.internetStatus='0'
            self.chargeBattery = True
            self.start = False
            
            self.event_start = None
            self.event_stop = None
            self.selectedSensor = -1
            self.dialog_show = False
            self.hdmi = False
            # self.installEventFilter(self)

            #array store sensor data
            self.maxLen=60
            self.maxRow=20
            self.time_stamp_temp=deque([])
            self.time_stamp_digital=deque([])
            self.time_stamp_co2=deque([])
            self.time_stamp_sound=deque([])
            self.time_stamp_analog=deque([])
            self.list_temp=deque([])
            self.list_humid=deque([])
            self.list_press=deque([])
            self.list_o2kk=deque([])
            self.list_o2n=deque([])
            self.list_sound=deque([])
            self.list_pH=deque([])
            self.list_ec=deque([])
            self.list_co2=deque([])

            self.list_digital_full=deque([])
            self.list_analog_full=deque([])
            self.list_co2_full=deque([])
            self.list_sound_full=deque([])
            self.list_temp_full=deque([])

            self.time_measure=5
            self.zero_weight=0
            self.cal_weight=0

            try:
                res = Setting.select()
                self.time_measure = res[0].time_measure
                self.zero_weight = res[0].zero_weight
                self.cal_weight = res[0].cal_weight
                

            except Exception as ex:
                print(ex)
                db_rollback()

            self.totalTime = self.time_measure*60


            #set button events
            self.btn_home.clicked.connect(self.goHome)
            self.btn_history.clicked.connect(self.goHistory)
            # self.btn_exit.clicked.connect(self.goClose)
            self.btn_exit.hide()

            self.btn_off.clicked.connect(self.goOff)
            self.btn_run.clicked.connect(self.startMeasure)

            self.btn_temp.clicked.connect(self.goTemp)
            self.btn_humid.clicked.connect(self.goHumid)
            self.btn_press.clicked.connect(self.goPress)
            self.btn_o2kk.clicked.connect(self.goO2kk)
            self.btn_co2.clicked.connect(self.goCo2)
            self.btn_sound.clicked.connect(self.goSound)
            self.btn_ph.clicked.connect(self.goPh)
            self.btn_o2n.clicked.connect(self.goO2n)
            self.btn_elec.clicked.connect(self.goElec)
            self.btn_force.clicked.connect(self.goForce)

            self.btn_setting.clicked.connect(self.goSetting)

            self.btn_scan_wifi.clicked.connect(self.scanWifi)

            self.btn_search.clicked.connect(self.searchData)
            self.btn_export.clicked.connect(self.sendMail)
            self.btn_next.clicked.connect(self.nextQuery)
            self.btn_prev.clicked.connect(self.prevQuery)
            # self.

            self.checkLast.stateChanged.connect(self.changeCheckbox)

            self.btn_time_save.clicked.connect(self.editTimeMeasure)
            self.cb_measure_time.setCurrentIndex(int(self.time_measure/5-1))

            

            #init qdate
            now = datetime.now()
            qdate = QDate(now.year,now.month,now.day)
            qtime = QTime(now.hour,now.minute,now.second)
            # qtime_1 = QTime(now.hour+3,now.minute,now.second)
            self.date_start.setMaximumDate(qdate)
            # self.date_start.setMaximumTime(qtime)

            self.date_end.setMaximumDate(qdate)
            # self.date_end.setMaximumTime(qtime)s
            self.date_start.setDate(qdate)
            self.date_start.setTime(qtime)
            self.date_end.setDate(qdate)
            self.date_end.setTime(qtime)

            #set up timer for showwing datetime
            self.timer=QTimer()
            self.timer.timeout.connect(self.showTime)
            self.timer.start(1000)


            #set up timer running measure
            self.runMeasure = QTimer()
            self.runMeasure.setInterval(self.time_measure*60*1000)
            self.runMeasure.timeout.connect(self.stopMeasure)

            #set up internet threadss
            self.readInternet = internetThread(self)
            self.readInternet.updateStatus.connect(self.updateInternet)
            self.readInternet.start()

            #set up battery thread
            self.readBattery = batteryThread(self)
            self.readBattery.updateBat.connect(self.updateBattery)
            self.readBattery.start()

            #set up sensor status thread
            self.sensorStatus = checkThread(self)
            self.sensorStatus.updateStatus.connect(self.updateSensorStatus)
            self.sensorStatus.start()

            #set up reading temp thread
            self.tempSensor = tempThread(self)
            self.tempSensor.updateDt.connect(self.updateTemp)
            self.tempSensor.start()

            self.digitalSensor = digitalThread(self)
            self.digitalSensor.updateDt.connect(self.updateDigital)
            self.digitalSensor.start()

            #set up reading temp thread
            self.co2Sensor = co2Thread(self)
            self.co2Sensor.updateDt.connect(self.updateCo2)
            self.co2Sensor.start()

            #set up reading analog thread
            self.adcSensor = analogThread(self)
            self.adcSensor.updateDt.connect(self.updateAnalog)
            self.adcSensor.start()

            #set up sound thread
            self.soundSensor = soundThread(self)
            self.soundSensor.updateDt.connect(self.updateSound)
            self.soundSensor.start()

            self.wifiMan = wifiThread(self)
            self.wifiMan.updateData.connect(self.updateWifiData)
            self.wifiMan.start()

            #init table
            header1= self.tableTemp.horizontalHeader()
            header1.setSectionResizeMode(0, QHeaderView.ResizeToContents)

            header2= self.tableHumid.horizontalHeader()
            header2.setSectionResizeMode(0, QHeaderView.ResizeToContents)

            header3= self.tablePress.horizontalHeader()
            header3.setSectionResizeMode(0, QHeaderView.ResizeToContents)

            header4= self.tableO2kk.horizontalHeader()
            header4.setSectionResizeMode(0, QHeaderView.ResizeToContents)

            header5= self.tableCO2.horizontalHeader()
            header5.setSectionResizeMode(0, QHeaderView.ResizeToContents)

            header6= self.tableSound.horizontalHeader()
            header6.setSectionResizeMode(0, QHeaderView.ResizeToContents)

            header7= self.tablePH.horizontalHeader()
            header7.setSectionResizeMode(0, QHeaderView.ResizeToContents)

            header8= self.tableO2N.horizontalHeader()
            header8.setSectionResizeMode(0, QHeaderView.ResizeToContents)

            header9= self.tableElec.horizontalHeader()
            header9.setSectionResizeMode(0, QHeaderView.ResizeToContents)

            header10= self.tableForce.horizontalHeader()
            header10.setSectionResizeMode(0, QHeaderView.ResizeToContents)

            header11= self.tableSensor_2.horizontalHeader()
            header11.setSectionResizeMode(0, QHeaderView.Stretch)

            header12= self.tableWifi.horizontalHeader()
            header12.setSectionResizeMode(0,QHeaderView.Stretch)
            header12.setSectionResizeMode(1,QHeaderView.Stretch)
            header12.setSectionResizeMode(2,QHeaderView.Stretch)
            header12.setSectionResizeMode(3,QHeaderView.Stretch)
            self.tableWifi.itemSelectionChanged.connect(self.onWifiSelected)
            # header12.setSectionResizeMode(0,QHeaderView.ResizeToContents)


            pg.setConfigOption('foreground', 'k')

            pen = pg.mkPen(color=(255, 0, 0))
            #page temperature
            self.graphTemp = pg.PlotWidget(title='Đồ thị nhiệt độ',axisItems={'bottom': TimeAxisItem(orientation='bottom')},left=u'Nhiệt độ(℃)')
            self.line_temp = self.graphTemp.plot(self.time_stamp_temp,self.list_temp,pen=pen,symbol='o', symbolSize=5, symbolBrush=('b'))
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
            self.gaugeTemp.update_value(0)
            self.verticalLayout_6.addWidget(self.gaugeTemp,1)
            self.verticalLayout_6.setStretch(0, 1)
            self.verticalLayout_6.setStretch(1, 1)

            #page humidity
            self.graphHumid = pg.PlotWidget(title='Đồ thị độ ẩm',axisItems={'bottom': TimeAxisItem(orientation='bottom')},left=u'Độ ẩm(%)')
            self.line_humid = self.graphHumid.plot(self.time_stamp_temp,self.list_humid,pen=pen,symbol='o', symbolSize=5, symbolBrush=('b'))
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
            self.gaugeHumid.update_value(0)
            self.verticalLayout_7.addWidget(self.gaugeHumid,1)
            self.verticalLayout_7.setStretch(0, 1)
            self.verticalLayout_7.setStretch(1, 1)

            #page press
            self.graphPress = pg.PlotWidget(title='Đồ thị áp suất',axisItems={'bottom': TimeAxisItem(orientation='bottom')},left=u'Áp suất(kPa)')
            self.line_press = self.graphPress.plot(self.time_stamp_temp,self.list_press,pen=pen,symbol='o', symbolSize=5, symbolBrush=('b'))
            self.graphPress.setMenuEnabled(False)
            self.graphPress.setBackground('w')
            self.verticalLayout_8.addWidget(self.graphPress,0)

            self.gaugePress = AnalogGaugeWidget()
            self.gaugePress.value_min =0
            self.gaugePress.enable_barGraph = True
            self.gaugePress.value_needle_snapzone = 1
            self.gaugePress.value_max =1500
            self.gaugePress.scala_main_count=15
            self.gaugePress.set_enable_CenterPoint(False)
            self.gaugePress.update_value(0)
            self.verticalLayout_8.addWidget(self.gaugePress,1)
            self.verticalLayout_8.setStretch(0, 1)
            self.verticalLayout_8.setStretch(1, 1)

            #page O2 KK
            self.graphO2kk = pg.PlotWidget(title='Đồ thị nồng độ O2 trong không khí',axisItems={'bottom': TimeAxisItem(orientation='bottom')},left=u'N.độ O2 trong không khí(%Vol)')
            self.line_o2kk = self.graphO2kk.plot(self.time_stamp_temp,self.list_o2kk,pen=pen,symbol='o', symbolSize=5, symbolBrush=('b'))
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
            self.gaugeO2kk.update_value(0)
            self.verticalLayout_9.addWidget(self.gaugeO2kk,1)
            self.verticalLayout_9.setStretch(0, 1)
            self.verticalLayout_9.setStretch(1, 1)


            #page CO2
            self.graphCO2 = pg.PlotWidget(title='Đồ thị nồng độ CO2',axisItems={'bottom': TimeAxisItem(orientation='bottom')},left=u'Nồng độ CO2(ppm)')
            self.line_co2 = self.graphCO2.plot(self.time_stamp_co2,self.list_co2,pen=pen,symbol='o', symbolSize=5, symbolBrush=('b'))
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
            self.gaugeCO2.update_value(0)
            self.verticalLayout_10.addWidget(self.gaugeCO2,1)
            self.verticalLayout_10.setStretch(0, 1)
            self.verticalLayout_10.setStretch(1, 1)


            #page sound
            self.graphSound = pg.PlotWidget(title='Đồ thị cường độ âm thanh',axisItems={'bottom': TimeAxisItem(orientation='bottom')},left=u'Cường độ âm thanh(dBA)')
            self.line_sound = self.graphSound.plot(self.time_stamp_sound,self.list_sound,pen=pen,symbol='o', symbolSize=5, symbolBrush=('b'))
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
            self.gaugeSound.update_value(0)
            self.verticalLayout_11.addWidget(self.gaugeSound,1)
            self.verticalLayout_11.setStretch(0, 1)
            self.verticalLayout_11.setStretch(1, 1)


            #page PH
            self.graphPH = pg.PlotWidget(title='Đồ thị độ PH',axisItems={'bottom': TimeAxisItem(orientation='bottom')},left=u'PH(pH)')
            self.line_ph = self.graphPH.plot(self.time_stamp_temp,self.list_pH,pen=pen,symbol='o', symbolSize=5, symbolBrush=('b'))
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
            self.gaugePH.update_value(0)
            self.verticalLayout_12.addWidget(self.gaugePH,1)
            self.verticalLayout_12.setStretch(0, 1)
            self.verticalLayout_12.setStretch(1, 1)


            #page O2 nuoc
            self.graphO2n = pg.PlotWidget(title='Đồ thị nồng độ O2 trong nước',axisItems={'bottom': TimeAxisItem(orientation='bottom')},left=u'Nồng độ O2 trong nước(mg/L)')
            self.line_o2n = self.graphO2n.plot(self.time_stamp_temp,self.list_o2n,pen=pen,symbol='o', symbolSize=5, symbolBrush=('b'))
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
            self.gaugeO2n.update_value(0)
            self.verticalLayout_13.addWidget(self.gaugeO2n,1)
            self.verticalLayout_13.setStretch(0, 1)
            self.verticalLayout_13.setStretch(1, 1)

            #page Electron
            self.graphElec = pg.PlotWidget(title='Đồ thị độ dẫn điện',axisItems={'bottom': TimeAxisItem(orientation='bottom')},left=u'Độ dẫn điện(ms/cm)')
            self.line_ec = self.graphElec.plot(self.time_stamp_temp,self.list_ec,pen=pen,symbol='o', symbolSize=5, symbolBrush=('b'))
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
            self.gaugeElec.update_value(0)
            self.verticalLayout_14.addWidget(self.gaugeElec,1)
            self.verticalLayout_14.setStretch(0, 1)
            self.verticalLayout_14.setStretch(1, 1)


            #page Force
            self.graphForce = pg.PlotWidget(title='Đồ thị lực',axisItems={'bottom': TimeAxisItem(orientation='bottom')},left=u'Lực (N)')
            # self.line_ec = self.graphElec.plot(self.time_stamp_temp,self.list_ec,pen=pen,symbol='o', symbolSize=5, symbolBrush=('b'))
            self.graphForce.setMenuEnabled(False)
            self.graphForce.setBackground('w')
            self.verticalLayout_15.addWidget(self.graphForce,0)

            self.gaugeForce = AnalogGaugeWidget()
            self.gaugeForce.value_min =0
            self.gaugeForce.enable_barGraph = True
            self.gaugeForce.value_needle_snapzone = 1
            self.gaugeForce.value_max =1000
            self.gaugeForce.scala_main_count=10
            self.gaugeForce.set_enable_CenterPoint(False)
            self.gaugeForce.update_value(0)
            self.verticalLayout_15.addWidget(self.gaugeForce,1)
            self.verticalLayout_15.setStretch(0, 1)
            self.verticalLayout_15.setStretch(1, 1)

            self.show()




            
        # def eventFilter(self, object, event):
        #     if event.type()== QEvent.FocusIn:
        #         print("widget has gained keyboard focus")
        #     elif event.type()== QEvent.FocusOut:
        #         print("widget has lost keyboard focus")


        #     return False
        def sendMail(self):
            # print(self.dialog_show)
            if self.dialog_show == True:
                return
            if self.start == True:
                return QMessageBox.warning(self, 'Thông báo', 'Vui lòng hoàn thành quá trình đo trước khi gửi mail!', QMessageBox.Ok)
            if self.query != None and len(self.query)>0:
                self.dialog_show = True
                m = Mail(self,self.query,self.selectedSensor)
                m.show()
                m.raise_()
                m.activateWindow()
                
                # m.closeEvent = self.dialogClose()
                # self.hide()
            else:
                return QMessageBox.warning(self, 'Thông báo', 'Không có dữ liệu để xuất file!', QMessageBox.Ok)   
        # def dialogClose(self):
        #     print('close dialog')
        #     self.dialog_show = False
        def searchData(self):
            if self.dialog_show == True:
                return
            self.selectedSensor = self.comboBox.currentIndex()
            if self.selectedSensor<0:
                return QMessageBox.warning(self, 'Thông báo', 'Vui lòng chọn cảm biến!', QMessageBox.Ok)
            
            startDate = self.date_start.date()
            startTime = self.date_start.time()
            endDate = self.date_end.date()
            endTime = self.date_end.time()

            startQuery = int(datetime(startDate.year(),startDate.month(),startDate.day(),startTime.hour(),startTime.minute(),startTime.second()).timestamp())
            endQuery = int(datetime(endDate.year(),endDate.month(),endDate.day(),endTime.hour(),endTime.minute(),endTime.second()).timestamp())
            
            check = endQuery - startQuery
            if check >=24*60*60:
                return QMessageBox.warning(self, 'Thông báo', 'Dữ liệu tìm kiếm quá thời gian một ngày.\nVui lòng chọn lại thời gian!', QMessageBox.Ok)
            
            # print(startQuery,endQuery)
            # self.btn_search.setEnabled(False)
            try:

                if self.selectedSensor ==0:
                    self.query= Temp.select().where(Temp.time.between(startQuery,endQuery))
                elif self.selectedSensor==1 or self.selectedSensor==2 or self.selectedSensor==3:
                    self.query = Digital.select().where(Digital.time.between(startQuery,endQuery))
                elif self.selectedSensor ==4:
                    self.query = CO2.select().where(CO2.time.between(startQuery,endQuery))
                elif self.selectedSensor ==5:
                    self.query = Sound.select().where(Sound.time.between(startQuery,endQuery))
                else:
                    self.query = Analog.select().where(Analog.time.between(startQuery,endQuery))

                numData = self.query.count()

                #detete all data from table
                model =  self.tableSensor_2.model()
                model.removeRows(0,model.rowCount())

                if numData ==0:
                    self.pageResult =0
                    self.totalPage = 0
                    self.lb_pagi.setText('0/0')
                    return QMessageBox.information(self, 'Thông báo', 'Không có dữ liệu cảm biến!', QMessageBox.Ok)
                else:
                    self.pageResult = 1
                    self.totalPage = int(numData/self.numItem)+1

                    self.lb_pagi.setText(str(self.pageResult)+"/"+str(self.totalPage))

                    if self.pageResult == self.totalPage:
                        self.btn_next.setEnabled(False)
                    else:
                        self.btn_next.setEnabled(True)
                    
                    self.queryResult = self.query.paginate(self.pageResult, self.numItem)
                    # print(self.queryResult)
                    for item in self.queryResult:
                        dt=0.0
                        if self.selectedSensor ==0:
                            dt = item.temp
                        elif self.selectedSensor==1:
                            dt = item.humid
                        elif self.selectedSensor ==2:
                            dt = item.press
                        elif self.selectedSensor ==3:
                            dt = item.air_oxy
                        elif self.selectedSensor ==4:
                            dt = item.co2
                        elif self.selectedSensor==5:
                            dt = item.sound
                        elif self.selectedSensor ==6:
                            dt = item.pH
                        elif self.selectedSensor ==7:
                            dt = item.water_oxy
                        elif self.selectedSensor ==8:
                            dt = item.ec
                        rowData= [convertTime(item.time),str(dt)]
                        self.insertRow(self.tableSensor_2,rowData)
                # self.btn_search.setEnabled(True)
            except Exception as ex:
                print(ex)
                # self.btn_search.setEnabled(True)
                db_rollback()
        
        def nextQuery(self):
            self.pageResult = self.pageResult +1
            self.btn_prev.setEnabled(True)
            if self.pageResult ==self.totalPage:
                self.btn_next.setEnabled(False)
            self.lb_pagi.setText(str(self.pageResult)+"/"+str(self.totalPage))
            try:
                self.queryResult = self.query.paginate(self.pageResult, self.numItem)
                model =  self.tableSensor_2.model()
                model.removeRows(0,model.rowCount())
                for item in self.queryResult:
                    dt=0.0
                    if self.selectedSensor ==0:
                        dt = item.temp
                    elif self.selectedSensor==1:
                        dt = item.humid
                    elif self.selectedSensor ==2:
                        dt = item.press
                    elif self.selectedSensor ==3:
                        dt = item.air_oxy
                    elif self.selectedSensor ==4:
                        dt = item.co2
                    elif self.selectedSensor==5:
                        dt = item.sound
                    elif self.selectedSensor ==6:
                        dt = item.pH
                    elif self.selectedSensor ==7:
                        dt = item.water_oxy
                    elif self.selectedSensor ==8:
                        dt = item.ec
                    rowData= [convertTime(item.time),str(dt)]
                    self.insertRow(self.tableSensor_2,rowData)
            except Exception as ex:
                db_rollback()
                print(ex)
    
        def prevQuery(self):
            self.pageResult = self.pageResult -1
            if self.pageResult==0:
                self.pageResult = 1
            self.btn_next.setEnabled(True)
            if self.pageResult ==1:
                self.btn_prev.setEnabled(False)
            self.lb_pagi.setText(str(self.pageResult)+"/"+str(self.totalPage))
            try:
                self.queryResult = self.query.paginate(self.pageResult, self.numItem)
                model =  self.tableSensor_2.model()
                model.removeRows(0,model.rowCount())
                for item in self.queryResult:
                    dt=0.0
                    if self.selectedSensor ==0:
                        dt = item.temp
                    elif self.selectedSensor==1:
                        dt = item.humid
                    elif self.selectedSensor ==2:
                        dt = item.press
                    elif self.selectedSensor ==3:
                        dt = item.air_oxy
                    elif self.selectedSensor ==4:
                        dt = item.co2
                    elif self.selectedSensor==5:
                        dt = item.sound
                    elif self.selectedSensor ==6:
                        dt = item.pH
                    elif self.selectedSensor ==7:
                        dt = item.water_oxy
                    elif self.selectedSensor ==8:
                        dt = item.ec
                    rowData= [convertTime(item.time),str(dt)]
                    self.insertRow(self.tableSensor_2,rowData)
            except Exception as ex:
                db_rollback()
                print(ex)  


        def changeCheckbox(self,dt):
            # print('checkboox:',dt)
            state = self.checkLast.isChecked()
            if state == False:
                return
            if self.event_stop == None:
                return QMessageBox.warning(self, 'Thông báo', 'Chưa có thời gian kết thúc!', QMessageBox.Ok)
            start = datetime.fromtimestamp(self.event_start)
            end = datetime.fromtimestamp(self.event_stop)

            dStart = QDate(start.year,start.month,start.day)
            dEnd = QDate(end.year,end.month,end.day)

            tStart = QTime(start.hour,start.minute,start.second)
            tEnd = QTime(end.hour,end.minute,end.second)

            self.date_start.setDate(dStart)
            self.date_start.setTime(tStart)
            self.date_end.setDate(dEnd)
            self.date_end.setTime(tEnd)

            
        def showTime(self):
            now = datetime.now().strftime("%d/%m/%Y %H:%M")
            self.lb_datetime.setText(now)
            if self.start == True:
                self.totalTime= self.totalTime-1
                if self.totalTime<0:
                    self.totalTime=0
                _min = str(int(self.totalTime/60)).rjust(2,'0')
                _sec = str(self.totalTime%60).rjust(2,'0')
                self.lb_total_time.setText('Thời gian còn lại: {min}:{sec}'.format(min=_min,sec=_sec))
                

        def editTimeMeasure(self):
            try:
                val = int(self.cb_measure_time.currentText())
                Setting.update(time_measure=val).where(Setting.id==1).execute()
                self.time_measure = val
                # self.totalTime = val*60
                # self.runMeasure.setInterval(val*60*1000)
                QMessageBox.information(self, 'Thông báo', 'Lưu thời gian đo thành công!', QMessageBox.Ok)
            except Exception as ex:
                print(ex)
                db_rollback()
                QMessageBox.warning(self, 'Thông báo', 'Lưu thời gian đo thất bại!', QMessageBox.Ok)


        def stopMeasure(self):
            
            self.runMeasure.stop()
            self.event_stop = timestamp()
            self.btn_time_save.setEnabled(True)
            self.cb_measure_time.setEnabled(True)
            self.btn_scan_wifi.setEnabled(True)
            self.start = False
            self.btn_run.setIcon(QIcon(':/img/play.svg'))
            # self.btn_run.setText('Chạy')
            QMessageBox.information(self, 'Thông báo', 'Hoàn thành việc đo cảm biến!', QMessageBox.Ok)
            self.lb_total_time.setText('Thời gian còn lại: --:--')
            try:
                # start = timestamp()
                Temp.insert_many(self.list_temp_full).execute()
                CO2.insert_many(self.list_co2_full).execute()
                Digital.insert_many(self.list_digital_full).execute()
                Analog.insert_many(self.list_analog_full).execute()
                Sound.insert_many(self.list_sound_full).execute()
                # end = timestamp()
                # print('save db spend :',end-start)
            except Exception as ex:
                print("error write data to db:",ex)
        
        def updateInternet(self,dt):
            # print('internet status:',dt)
            if self.hdmi == False:
                result = subprocess.Popen('xrandr --auto --output HDMI-2 --mode 1280x720 --same-as HDMI-1',shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE).communicate()[1].decode('utf-8')
                print("result string std",result)
                if result.find('cannot find mode 1280x720')!=-1:
                    self.hdmi = False
                else:
                    self.hdmi = True
            if self.internetStatus==dt:
                return
            self.internetStatus=dt
            if dt=='1':
                self.frameInternet.setToolTip('Đang kết nối')
                self.lb_internet.setPixmap(QPixmap(':/img/network.svg'))
            else:
                self.frameInternet.setToolTip('Mất kết nối')
                self.lb_internet.setPixmap(QPixmap(':/img/network_lost.svg'))
        

        def updateBattery(self,dt):
            # print('battery status:',dt)
            self.battery_percent.setValue(int(dt['batcap']))
            bat_status = False
            if dt['vin']=="NG":
                bat_status = False
            else:
                bat_status = True
            if self.chargeBattery == bat_status:
                return
            self.chargeBattery = bat_status

            if self.chargeBattery ==True:
                self.lb_charge.setPixmap(QPixmap(':/img/thunder.svg'))
            else:
                self.lb_charge.clear()

        def updateSensorStatus(self,dt):
            # print('sensor status:',dt)
            if self.listSensorStatus[0]!=dt[0]:
                self.listSensorStatus[0]=dt[0]
                if dt[0]==1:
                    self.lb_temp_status.setText("Đang kết nối")
                    self.lb_temp_status.setStyleSheet("background-color: white;border: 2px solid #a7da46;border-radius:10px;color: rgb(0, 170, 0);")
                else:
                    self.lb_temp.setText('0.0')
                    self.lb_temp_status.setText("Ngắt kết nối")
                    self.lb_temp_status.setStyleSheet("background-color: white;border: 2px solid #a7da46;border-radius:10px;color: rgb(255,0, 0);")
            
            if self.listSensorStatus[1]!=dt[1]:
                self.listSensorStatus[1]=dt[1]
                if dt[1]==1:
                    self.lb_humid_status.setText("Đang kết nối")
                    self.lb_humid_status.setStyleSheet("background-color: white;border: 2px solid #a7da46;border-radius:10px;color: rgb(0, 170, 0);")
                else:
                    self.lb_humid.setText('0.0')
                    self.lb_humid_status.setText("Ngắt kết nối")
                    self.lb_humid_status.setStyleSheet("background-color: white;border: 2px solid #a7da46;border-radius:10px;color: rgb(255,0, 0);")

            if self.listSensorStatus[2]!=dt[2]:
                self.listSensorStatus[2]=dt[2]
                if dt[2]==1:
                    self.lb_press_status.setText("Đang kết nối")
                    self.lb_press_status.setStyleSheet("background-color: white;border: 2px solid #a7da46;border-radius:10px;color: rgb(0, 170, 0);")
                else:
                    self.lb_press.setText('0.0')
                    self.lb_press_status.setText("Ngắt kết nối")
                    self.lb_press_status.setStyleSheet("background-color: white;border: 2px solid #a7da46;border-radius:10px;color: rgb(255,0, 0);")
            if self.listSensorStatus[3]!=dt[3]:
                self.listSensorStatus[3]=dt[3]
                if dt[3]==1:
                    self.lb_o2kk_status.setText("Đang kết nối")
                    self.lb_o2kk_status.setStyleSheet("background-color: white;border: 2px solid #a7da46;border-radius:10px;color: rgb(0, 170, 0);")
                else:
                    self.lb_o2kk.setText('0.0')
                    self.lb_o2kk_status.setText("Ngắt kết nối")
                    self.lb_o2kk_status.setStyleSheet("background-color: white;border: 2px solid #a7da46;border-radius:10px;color: rgb(255,0, 0);")
            if self.listSensorStatus[4]!=dt[4]:
                self.listSensorStatus[4]=dt[4]
                if dt[4]==1:
                    self.lb_co2_status.setText("Đang kết nối")
                    self.lb_co2_status.setStyleSheet("background-color: white;border: 2px solid #a7da46;border-radius:10px;color: rgb(0, 170, 0);")
                else:
                    self.lb_co2.setText('0.0')
                    self.lb_co2_status.setText("Ngắt kết nối")
                    self.lb_co2_status.setStyleSheet("background-color: white;border: 2px solid #a7da46;border-radius:10px;color: rgb(255,0, 0);")

            if self.listSensorStatus[5]!=dt[5]:
                self.listSensorStatus[5]=dt[5]
                if dt[5]==1:
                    self.lb_sound_status.setText("Đang kết nối")
                    self.lb_sound_status.setStyleSheet("background-color: white;border: 2px solid #a7da46;border-radius:10px;color: rgb(0, 170, 0);")
                else:
                    self.lb_sound.setText('0.0')
                    self.lb_sound_status.setText("Ngắt kết nối")
                    self.lb_sound_status.setStyleSheet("background-color: white;border: 2px solid #a7da46;border-radius:10px;color: rgb(255,0, 0);")
            
            if self.listSensorStatus[6]!=dt[6]:
                self.listSensorStatus[6]=dt[6]
                if dt[6]==1:
                    self.lb_ph_status.setText("Đang kết nối")
                    self.lb_ph_status.setStyleSheet("background-color: white;border: 2px solid #a7da46;border-radius:10px;color: rgb(0, 170, 0);")
                else:
                    self.lb_ph.setText('0.0')
                    self.lb_ph_status.setText("Ngắt kết nối")
                    self.lb_ph_status.setStyleSheet("background-color: white;border: 2px solid #a7da46;border-radius:10px;color: rgb(255,0, 0);")
            
            if self.listSensorStatus[7]!=dt[7]:
                self.listSensorStatus[7]=dt[7]
                if dt[7]==1:
                    self.lb_o2n_status.setText("Đang kết nối")
                    self.lb_o2n_status.setStyleSheet("background-color: white;border: 2px solid #a7da46;border-radius:10px;color: rgb(0, 170, 0);")
                else:
                    self.lb_o2n.setText('0.0')
                    self.lb_o2n_status.setText("Ngắt kết nối")
                    self.lb_o2n_status.setStyleSheet("background-color: white;border: 2px solid #a7da46;border-radius:10px;color: rgb(255,0, 0);")

            if self.listSensorStatus[8]!=dt[8]:
                self.listSensorStatus[8]=dt[8]
                if dt[8]==1:
                    self.lb_elec_status.setText("Đang kết nối")
                    self.lb_elec_status.setStyleSheet("background-color: white;border: 2px solid #a7da46;border-radius:10px;color: rgb(0, 170, 0);")
                else:
                    self.lb_elec.setText('0.0')
                    self.lb_elec_status.setText("Ngắt kết nối")
                    self.lb_elec_status.setStyleSheet("background-color: white;border: 2px solid #a7da46;border-radius:10px;color: rgb(255,0, 0);")

            if self.listSensorStatus[9]!=dt[9]:
                self.listSensorStatus[9]=dt[9]
                if dt[9]==1:
                    self.lb_force_status.setText("Đang kết nối")
                    self.lb_force_status.setStyleSheet("background-color: white;border: 2px solid #a7da46;border-radius:10px;color: rgb(0, 170, 0);")
                else:
                    self.lb_force.setText('0.0')
                    self.lb_force_status.setText("Ngắt kết nối")
                    self.lb_force_status.setStyleSheet("background-color: white;border: 2px solid #a7da46;border-radius:10px;color: rgb(255,0, 0);")

        def updateTemp(self,dt):
            # print('temp thread:',dt)
            if self.start == True:
                now = dt['time']
                if len(self.time_stamp_temp)>self.maxLen:
                    self.time_stamp_temp.popleft()
                    self.list_temp.popleft()
                self.time_stamp_temp.append(now)
                self.list_temp.append(dt['temp'])
                self.list_temp_full.append(dt)
                currentPage = self.stackedWidget.currentIndex()
                #page temp
                if currentPage==1:
                    self.gaugeTemp.update_value(dt['temp'])
                    self.line_temp.setData(self.time_stamp_temp,self.list_temp)
                count = self.tableTemp.rowCount()
                now_str=datetime.fromtimestamp(now).strftime("%H:%M:%S.%f")[:-5]
                if count>self.maxRow:
                    self.tableTemp.removeRow(count-1)
                self.insertFirstRow(self.tableTemp,[now_str,dt['temp']])

                if self.lb_temp.text()!= str(dt['temp']):
                    self.lb_temp.setText(str(dt['temp']))

        def updateDigital(self,dt):
            # print('data from digital thread:',dt)
            if self.start == True:
                now = dt['time']
                if len(self.time_stamp_digital)>self.maxLen:
                    self.time_stamp_digital.popleft()
                    self.list_humid.popleft()
                    self.list_press.popleft()
                    self.list_o2kk.popleft()
                self.list_digital_full.append(dt)
                self.time_stamp_digital.append(now)
                self.list_humid.append(dt['humid'])
                self.list_press.append(dt['press'])
                self.list_o2kk.append(dt['air_oxy'])


                #update graph and gauge
                currentPage = self.stackedWidget.currentIndex()
                if currentPage ==2:
                    self.gaugeHumid.update_value(dt['humid'])
                    self.line_humid.setData(self.time_stamp_digital,self.list_humid)
                elif currentPage ==3:
                    self.gaugePress.update_value(dt['press'])
                    self.line_press.setData(self.time_stamp_digital,self.list_press)
                elif currentPage ==4:
                    self.gaugeO2kk.update_value(dt['air_oxy'])
                    self.line_o2kk.setData(self.time_stamp_digital,self.list_o2kk)
                


                #update table
                count = self.tableTemp.rowCount()
                now_str=datetime.fromtimestamp(now).strftime("%H:%M:%S.%f")[:-5]
                if count>self.maxRow:
                    self.tableHumid.removeRow(count-1)
                    self.tablePress.removeRow(count-1)
                    self.tableO2kk.removeRow(count-1)
                    
                
                self.insertFirstRow(self.tableHumid,[now_str,dt['humid']])
                self.insertFirstRow(self.tablePress,[now_str,dt['press']])
                self.insertFirstRow(self.tableO2kk,[now_str,dt['air_oxy']])
                


            

                if self.lb_humid.text()!=str(dt['humid']):
                    self.lb_humid.setText(str(dt['humid']))

                if self.lb_press.text()!=str(dt['press']):
                    self.lb_press.setText(str(dt['press']))

                if self.lb_o2kk.text()!=str(dt['air_oxy']):
                    self.lb_o2kk.setText(str(dt['air_oxy']))
            
            
        def updateAnalog(self,dt):
            # print('data from analog thread:',dt)
            if self.start == True:
                now = dt['time']
                if len(self.time_stamp_analog)>self.maxLen:
                    self.time_stamp_analog.popleft()
                    self.list_o2n.popleft()
                    self.list_pH.popleft()
                    self.list_ec.popleft()
                self.list_analog_full.append(dt)
                self.time_stamp_analog.append(now)
                self.list_o2n.append(dt['water_oxy'])
                self.list_pH.append(dt['pH'])
                self.list_ec.append(dt['ec'])

                currentPage = self.stackedWidget.currentIndex()
                if currentPage ==7:
                    self.gaugePH.update_value(dt['pH'])
                    self.line_ph.setData(self.time_stamp_analog,self.list_pH)
                elif currentPage ==8:
                    self.gaugeO2n.update_value(dt['water_oxy'])
                    self.line_o2n.setData(self.time_stamp_analog,self.list_o2n)
                elif currentPage ==9:
                    self.gaugeElec.update_value(dt['ec'])
                    self.line_ec.setData(self.time_stamp_analog,self.list_ec)
                
                count = self.tableTemp.rowCount()
                now_str=datetime.fromtimestamp(now).strftime("%H:%M:%S.%f")[:-5]
                if count>self.maxRow:
                    self.tablePH.removeRow(count-1)
                    self.tableElec.removeRow(count-1)
                    self.tableO2N.removeRow(count-1)
                self.insertFirstRow(self.tablePH,[now_str,dt['pH']])
                self.insertFirstRow(self.tableO2N,[now_str,dt['water_oxy']])
                self.insertFirstRow(self.tableElec,[now_str,dt['ec']])

                if self.lb_ph.text()!=str(dt['pH']):
                    self.lb_ph.setText(str(dt['pH']))
                
                if self.lb_o2n.text()!=str(dt['water_oxy']):
                    self.lb_o2n.setText(str(dt['water_oxy']))

                if self.lb_elec.text()!=str(dt['ec']):
                    self.lb_elec.setText(str(dt['ec']))
        
        def updateCo2(self,dt):
            # print('co2:',dt)
            if self.start == True:
                now = dt['time']
                if len(self.time_stamp_co2)>self.maxLen:
                    self.time_stamp_co2.popleft()
                    self.list_co2.popleft()
                self.time_stamp_co2.append(now)
                self.list_co2.append(dt['co2'])
                self.list_co2_full.append(dt)

                currentPage = self.stackedWidget.currentIndex()
                if currentPage == 5:
                    self.gaugeCO2.update_value(dt['co2'])
                    self.line_co2.setData(self.time_stamp_co2,self.list_co2)
                
                #update table
                count = self.tableCO2.rowCount()
                now_str=datetime.fromtimestamp(now).strftime("%H:%M:%S.%f")[:-5]
                if count > self.maxRow:
                    self.tableCO2.removeRow(count-1)
                rowData = [now_str,dt['co2']]
                self.insertFirstRow(self.tableCO2,rowData)

                if self.lb_co2.text()!= str(dt['co2']):
                    self.lb_co2.setText(str(dt['co2']))

        def updateSound(self,dt):
            # print('sound:',dt)
            if self.start == True:
                now = dt['time']
                if len(self.time_stamp_sound)>self.maxLen:
                    self.time_stamp_sound.popleft()
                    self.list_sound.popleft()
                self.time_stamp_sound.append(now)
                self.list_sound.append(dt['sound'])

                self.list_sound_full.append(dt)

                currentPage = self.stackedWidget.currentIndex()
                if currentPage == 6:
                    self.gaugeSound.update_value(dt['sound'])
                    self.line_sound.setData(self.time_stamp_sound,self.list_sound)
                
                #update table
                now_str=datetime.fromtimestamp(now).strftime("%H:%M:%S.%f")[:-5]
                count = self.tableSound.rowCount()
                if count > self.maxRow:
                    self.tableSound.removeRow(count-1)
                rowData = [now_str,dt['sound']]
                self.insertFirstRow(self.tableSound,rowData)

                if self.lb_sound.text()!=str(dt['sound']):
                    self.lb_sound.setText(str(dt['sound']))


        #event clicked buttons
        def startMeasure(self):
            if self.dialog_show == True:
                return
            if self.start == False:
                self.btn_time_save.setEnabled(False)
                self.btn_scan_wifi.setEnabled(False)
                self.cb_measure_time.setEnabled(False)
                self.start = True
                self.btn_run.setIcon(QIcon(':/img/pause.svg'))
                # self.btn_run.setText('Dừng')

                #reset data
                self.time_stamp_temp=deque([])
                self.time_stamp_digital=deque([])
                self.time_stamp_co2=deque([])
                self.time_stamp_sound=deque([])
                self.time_stamp_analog=deque([])
                self.list_temp=deque([])
                self.list_humid=deque([])
                self.list_press=deque([])
                self.list_o2kk=deque([])
                self.list_o2n=deque([])
                self.list_sound=deque([])
                self.list_pH=deque([])
                self.list_ec=deque([])
                self.list_co2=deque([])

                self.list_digital_full=deque([])
                self.list_analog_full=deque([])
                self.list_co2_full=deque([])
                self.list_sound_full=deque([])
                self.list_temp_full=deque([])

                #reset gauge
                self.gaugeTemp.update_value(0)
                self.gaugeHumid.update_value(0)
                self.gaugePress.update_value(0)
                self.gaugeO2kk.update_value(0)
                self.gaugeCO2.update_value(0)
                self.gaugeSound.update_value(0)
                self.gaugePH.update_value(0)
                self.gaugeO2n.update_value(0)
                self.gaugeElec.update_value(0)

                #reset graph
                self.line_temp.setData(self.time_stamp_temp,self.list_temp)
                self.line_humid.setData(self.time_stamp_temp,self.list_temp)
                self.line_press.setData(self.time_stamp_temp,self.list_temp)
                self.line_co2.setData(self.time_stamp_temp,self.list_temp)
                self.line_o2kk.setData(self.time_stamp_temp,self.list_temp)
                self.line_sound.setData(self.time_stamp_temp,self.list_temp)
                self.line_o2n.setData(self.time_stamp_temp,self.list_temp)
                self.line_ph.setData(self.time_stamp_temp,self.list_temp)
                self.line_ec.setData(self.time_stamp_temp,self.list_temp)


                #reset table
                model =  self.tableTemp.model()
                model.removeRows(0,model.rowCount())

                model =  self.tableTemp.model()
                model.removeRows(0,model.rowCount())

                model =  self.tableTemp.model()
                model.removeRows(0,model.rowCount())

                model =  self.tableHumid.model()
                model.removeRows(0,model.rowCount())

                model =  self.tablePress.model()
                model.removeRows(0,model.rowCount())

                model =  self.tableO2kk.model()
                model.removeRows(0,model.rowCount())

                model =  self.tableCO2.model()
                model.removeRows(0,model.rowCount())

                model =  self.tableSound.model()
                model.removeRows(0,model.rowCount())

                model =  self.tablePH.model()
                model.removeRows(0,model.rowCount())

                model =  self.tableO2N.model()
                model.removeRows(0,model.rowCount())

                model =  self.tableElec.model()
                model.removeRows(0,model.rowCount())
                self.totalTime = self.time_measure*60
                self.runMeasure.setInterval(self.totalTime*1000)
                self.lb_total_time.setText('Thời gian còn lại: --:--')
                self.event_start = timestamp()
                self.event_stop = None
                self.runMeasure.start()
            else:
                # self.totalTime = TIME_MEASURE*60
                newMessBox = QMessageBox(self)
                newMessBox.setIcon(QMessageBox.Warning)
                newMessBox.setText("Bạn có chắc chắn muốn dừng đo?")
                newMessBox.setWindowTitle("Thông báo")
                newMessBox.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
                returnValue = newMessBox.exec()

                if returnValue == QMessageBox.No:
                    return
                self.start = False
                self.btn_time_save.setEnabled(True)
                self.cb_measure_time.setEnabled(True)
                self.btn_scan_wifi.setEnabled(True)
                self.btn_run.setIcon(QIcon(':/img/play.svg'))
                # self.btn_run.setText('Chạy')
                self.runMeasure.stop()
                self.event_stop = timestamp()
                try:
                    # start = timestamp()
                    Temp.insert_many(self.list_temp_full).execute()
                    CO2.insert_many(self.list_co2_full).execute()
                    Digital.insert_many(self.list_digital_full).execute()
                    Analog.insert_many(self.list_analog_full).execute()
                    Sound.insert_many(self.list_sound_full).execute()
                    # end = timestamp()
                    # print('save db spend :',end-start)
                except Exception as ex:
                    print("error write data to db:",ex)
        # go to Pages
        def goHome(self):
            if self.dialog_show == True:
                return
            self.stackedWidget.setCurrentIndex(0)  
        def goHistory(self):
            if self.dialog_show == True:
                return
            self.stackedWidget.setCurrentIndex(11)

        def closeEvent(self, QCloseEvent):
            print('close app!')
            self.readInternet.stop()
            self.sensorStatus.stop()
            self.soundSensor.stop()
            self.co2Sensor.stop()
            self.tempSensor.stop()
            self.adcSensor.stop()
            self.digitalSensor.stop()
            # self.timer.stop()
            # self.runMeasure.stop()
           
            # self.goClose()
        
        def goClose(self):
            # self.readInternet.stop()
            # self.sensorStatus.stop()
            # self.soundSensor.stop()
            # self.co2Sensor.stop()
            # self.tempSensor.stop()
            # self.adcSensor.stop()
            # self.readStatus.stop()
            # self.timer.stop()
            # self.runMeasure.stop()

            # db_close()
            if self.dialog_show == True:
                return
            newMessBox = QMessageBox(self)
            newMessBox.setIcon(QMessageBox.Warning)
            newMessBox.setText("Bạn có chắc chắn muốn thoát phần mềm?")
            newMessBox.setWindowTitle("Thông báo")
            newMessBox.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
            returnValue = newMessBox.exec()

            if returnValue == QMessageBox.No:
                return
            db_close()
            # self.readInternet.threadActive = False
            # self.sensorStatus.threadActive = False
            # self.soundSensor.threadActive = False
            # self.co2Sensor.threadActive = False
            # self.tempSensor.threadActive = False
            # self.adcSensor.threadActive = False
            # self.digitalSensor.threadActive = False
            # a=0
            # for i in range(5000):
            #     a=a+1
            self.close()
        def goOff(self):
            if self.dialog_show == True:
                return
            newMessBox = QMessageBox(self)
            newMessBox.setIcon(QMessageBox.Warning)
            newMessBox.setText("Bạn có chắc chắn muốn tắt máy?")
            newMessBox.setWindowTitle("Thông báo")
            newMessBox.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
            returnValue = newMessBox.exec()
            if returnValue == QMessageBox.No:
                return
            # db_close()
            # self.readInternet.threadActive = False
            # self.sensorStatus.threadActive = False
            # self.soundSensor.threadActive = False
            # self.co2Sensor.threadActive = False
            # self.tempSensor.threadActive = False
            # self.adcSensor.threadActive = False
            # self.digitalSensor.threadActive = False
            # delay(50)
            subprocess.Popen('sudo shutdown -h now',shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        
        def goTemp(self):
            self.stackedWidget.setCurrentIndex(1)
            if len(self.list_temp)>0:
                self.gaugeTemp.update_value(self.list_temp[-1])
                self.line_temp.setData(self.time_stamp_temp,self.list_temp) 
        def goHumid(self):
            self.stackedWidget.setCurrentIndex(2)
            if len(self.list_humid)>0:
                self.gaugeHumid.update_value(self.list_humid[-1])
                self.line_humid.setData(self.time_stamp_digital,self.list_humid)
        def goPress(self):
            self.stackedWidget.setCurrentIndex(3)
            if len(self.list_press)>0:
                self.gaugePress.update_value(self.list_press[-1])
                self.line_press.setData(self.time_stamp_digital,self.list_press)
        def goO2kk(self):
            self.stackedWidget.setCurrentIndex(4)  
            if len(self.list_o2kk)>0:
                self.gaugeO2kk.update_value(self.list_o2kk[-1])
                self.line_o2kk.setData(self.time_stamp_digital,self.list_o2kk)
        def goCo2(self):
            self.stackedWidget.setCurrentIndex(5)
            if len(self.list_co2)>0:
                self.gaugeCO2.update_value(self.list_co2[-1])
                self.line_co2.setData(self.time_stamp_co2,self.list_co2)
        def goSound(self):
            self.stackedWidget.setCurrentIndex(6)
            if len(self.list_sound)>0:
                self.gaugeSound.update_value(self.list_sound[-1])
                self.line_sound.setData(self.time_stamp_sound,self.list_sound)
        def goPh(self):
            self.stackedWidget.setCurrentIndex(7)  
            if len(self.list_pH)>0:
                self.gaugePH.update_value(self.list_pH[-1])
                self.line_ph.setData(self.time_stamp_analog,self.list_pH)
        def goO2n(self):
            self.stackedWidget.setCurrentIndex(8)
            if len(self.list_o2n)>0:
                self.gaugeO2n.update_value(self.list_o2n[-1])
                self.line_o2n.setData(self.time_stamp_analog,self.list_o2n)
        def goElec(self):
            self.stackedWidget.setCurrentIndex(9)
            if len(self.list_ec)>0:
                self.gaugeElec.update_value(self.list_ec[-1])
                self.line_ec.setData(self.time_stamp_analog,self.list_ec)
        
        def goForce(self):
            self.stackedWidget.setCurrentIndex(10)
            # if len(self.list_ec)>0:
            #     self.gaugeElec.update_value(self.list_ec[-1])
            #     self.line_ec.setData(self.time_stamp_analog,self.list_ec)
        def goSetting(self):
            self.stackedWidget.setCurrentIndex(12)

        
        def updateWifiData(self,dt):
            print('wifi data:',dt)
            
            if dt['cmd']=='scan':
                self.loading.stop()
                list_wifi,self.oldSsid=parseWifiScan(dt['result'])
                for item in list_wifi:
                    status='Chưa kết nối'
                    if item['status']=='yes':
                        status ='Đang kết nối'
                    self.insertWifiRow(self.tableWifi,[item['ssid'],item['signal'],item['security'],status])
            elif dt['cmd']=='connect':
                if dt['result'].find('successfully')>=0:
                    model =  self.tableWifi.model()
                    model.removeRows(0,model.rowCount())
                    self.wifiMan.cmd='rescan'
                else:
                    self.loading.stop()
                    self.tableWifi.clearSelection()
                    return QMessageBox.warning(self, 'Thông báo', 'Kết nối thất bại.Vui lòng thử lại!', QMessageBox.Ok)


        def scanWifi(self):
            model =  self.tableWifi.model()
            model.removeRows(0,model.rowCount())
            self.wifiMan.cmd='scan'
            
            self.loading.start()
            # for item in list_wifi:
            #     status='Chưa kết nối'
            #     if item['status']=='yes':
            #         status ='Đang kết nối'
            #     self.insertWifiRow(self.tableWifi,[item['ssid'],item['signal'],item['security'],status])

        
        def insertFirstRow(self,table,row_data):
            col=0
            row = 0
            table.insertRow(row)
            for item in row_data:
                cell = QTableWidgetItem(str(item))
                cell.setTextAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
                table.setItem(row,col,cell)
                col+=1
        
        def insertWifiRow(self,table,row_data):
            col=0
            row = 0
            table.insertRow(row)
            for i in range(len(row_data)):
                
                cell = QTableWidgetItem(str(row_data[i]))
                cell.setTextAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
                if i==3:
                    if row_data[i]=='Đang kết nối':
                        cell.setForeground(QBrush(QColor(0, 170, 0)))
                    else:
                        cell.setForeground(QBrush(QColor(255, 0, 0)))
                table.setItem(row,col,cell)
                col+=1
        def onWifiSelected(self):
            print('change table')
            try:
                selectedRows = self.tableWifi.selectionModel().selectedRows()[0]
                selectedWifi=selectedRows.sibling(selectedRows.row(),0).data()
                selectedWifiStatus = selectedRows.sibling(selectedRows.row(),3).data()
                selectedRow = selectedRows.row()
                print(selectedRow,selectedWifi)
                if selectedRow>=0:
                    if selectedWifiStatus=='Đang kết nối':
                        return QMessageBox.warning(self, 'Thông báo', 'Mạng wifi đã được kết nối!', QMessageBox.Ok)
                    else:
                        print('open dialog')
                        # password,ok = QInputDialog.getText(self,'Kết nối mạng {}'.format(selectedWifi),'Mật khẩu:')
                        inp = QInputDialog(self)

                        ##### SOME SETTINGS
                        inp.setInputMode(QInputDialog.TextInput)
                        # inp.setFixedSize(400, 200)
                        # inp.setOption(QInputDialog.UsePlainTextEditForTextInput)
                        inp.setWindowTitle('Kết nối mạng {}'.format(selectedWifi))
                        inp.setLabelText('Mật khẩu:')
                        #####
                        inp.show()
                        inp.raise_()
                        inp.activateWindow()
                        inp.finished.connect(lambda:self.closeWifiDialog(inp,selectedWifi))
            except:
                pass
        def closeWifiDialog(self,inp,ssid):
            # print(inp.result())
            if inp.result()==1:
                password=inp.textValue()
                # print('close dialog',inp.textValue())
                
                if len(password)<8:
                        self.tableWifi.clearSelection()
                        return QMessageBox.warning(self, 'Thông báo', 'Vui lòng nhập mật khẩu dài hơn 8 kí tự!', QMessageBox.Ok)
                else:
                    self.wifiMan.data['ssid']=ssid
                    self.wifiMan.data['password']=password
                    self.wifiMan.data['oldWifi']=self.oldSsid
                    self.wifiMan.cmd='connect'
                    self.loading.start()
                inp.deleteLater()
        def insertRow(self,table,row_data):
            col=0
            row = table.rowCount()
            table.insertRow(row)
            for item in row_data:
                cell = QTableWidgetItem(str(item))
                cell.setTextAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
                table.setItem(row,col,cell)
                col+=1
    
    def handleVisibleChanged():
        if not QGuiApplication.inputMethod().isVisible():
            return
        for w in QGuiApplication.allWindows():
            if w.metaObject().className() == "QtVirtualKeyboard::InputView":
                keyboard = w.findChild(QObject, "keyboard")
                if keyboard is not None:
                    r = w.geometry()
                    r.moveTop(int(keyboard.property("y")))
                    w.setMask(QRegion(r))
                    return
    if __name__ == "__main__":
        creat_table()
        os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"
        app = QApplication(sys.argv)
        QGuiApplication.inputMethod().visibleChanged.connect(handleVisibleChanged)
        # window = Home("s")
        # window.show()
        # loop = QEventLoop(app)
        # asyncio.set_event_loop(loop)
        win = Main()
        # win.show()
        sys.exit(app.exec_())
        
except Exception as ex:
    print(ex)
    # GPIO.cleanup()
    # del win.window 
finally:
    print("exit app!")
    GPIO.cleanup()
    # os.kill(mypid, signal.SIGTERM)