from sensors.ds18b20 import DS18B20
import glob
from ultil.asyncSleep import delay
import os
from datetime import datetime
os.system('sudo modprobe w1-gpio')
os.system('sudo dtoverlay w1-gpio gpiopin=25 pullup=0')
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'
sensor = DS18B20(device_file)
try:
    while True:
        start= datetime.now().timestamp()
        print(sensor.readTemp())
        end= datetime.now().timestamp()
        print('time read:',end-start)
        delay(1)
finally:
    print('close file')
    # sensor.cleanUp()
