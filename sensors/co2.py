import serial
import platform
import getrpimodel
import struct
import os
import platform
# from ultil.asyncSleep import delay


pimodel        = getrpimodel.model()
pimodel_strict = getrpimodel.model_strict()
partial_serial_dev = None
if os.path.exists('/dev/serial0'):
  partial_serial_dev = 'serial0'
elif pimodel == "3 Model B" or pimodel == "4 Model B" or pimodel_strict == "Zero W":
  partial_serial_dev = 'ttyS0'
else:
  partial_serial_dev = 'ttyAMA0'

serial_dev = '/dev/%s' % partial_serial_dev
p_ver = platform.python_version_tuple()[0]
# print(serial_dev,p_ver)
def checksum(array):
  if p_ver == '2' and isinstance(array, str):
    array = [ord(c) for c in array]
  csum = sum(array) % 0x100
  if csum == 0:
    return struct.pack('B', 0)
  else:
    return struct.pack('B', 0xff - csum + 1)
class MHZ19():
    def __init__(self):
        self._serial = serial.Serial(serial_dev,baudrate=9600,timeout=1)
    
    def read_concentration(self):
        self._serial.write(b"\xff\x01\x86\x00\x00\x00\x00\x00\x79")
        s=self._serial.read(9)
        # print(s)
        if p_ver == '2':
            if len(s) >= 4 and s[0] == "\xff" and s[1] == "\x86" and checksum(s[1:-1]) == s[-1]:
                return ord(s[2])*256 + ord(s[3])
        else:
            if len(s) >= 4 and s[0] == 0xff and s[1] == 0x86 and ord(checksum(s[1:-1])) == s[-1]:
                return s[2]*256 + s[3]
        return 0.0
    def close_serial(self):
        self._serial.close()