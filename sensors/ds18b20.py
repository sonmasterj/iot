import os
# import glob
from ultil.asyncSleep import delay
# base_dir = '/sys/bus/w1/devices/'
os.system('sudo modprobe w1-gpio')
os.system('sudo dtoverlay w1-gpio gpiopin=25 pullup=0')
class DS18B20():
    def __init__(self,device_file):
        self.device_file=device_file
    def read_temp_raw(self):
        f = open(self.device_file, 'r')
        lines = f.readlines()
        f.close()
        return lines
    def readTemp(self):
        try:
            lines = self.read_temp_raw()
            while lines[0].strip()[-3:] != 'YES':
                delay(0.01)
                lines = self.read_temp_raw()
            equals_pos = lines[1].find('t=')
            if equals_pos != -1:
                temp_string = lines[1][equals_pos+2:]
                temp_c =round(float(temp_string) / 1000.0,1)
                return temp_c
            else:
                return 0
        except:
            return -1
