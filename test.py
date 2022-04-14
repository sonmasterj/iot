from sensors.ds18b20 import DS18B20
import glob
from ultil.asyncSleep import delay
import os
os.system('sudo modprobe w1-gpio')
os.system('sudo dtoverlay w1-gpio gpiopin=25 pullup=0')
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'
sensor = DS18B20(device_file)
while True:
    print(sensor.readTemp())
    delay(1)