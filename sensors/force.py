# import smbus
# import time
class Force(): 
  def __init__(self, bus, addr=0x14):
    self.__addr = addr
    self.i2cbus = bus
  def write_reg(self, reg, data):
    self.i2cbus.write_i2c_block_data(self.__addr, reg, data)
  def read_reg(self, reg, len):
    rslt = self.i2cbus.read_i2c_block_data(self.__addr, reg, len)
    return rslt
  def read_data(self):
    try:
      data = self.read_reg(0x01,7)
      check_sum=0
      for i in range(len(data)-1):
        check_sum=check_sum+data[i]
      if (check_sum&0xFF)!=data[len(data)-1]:
        return 0.0
      else:
        weight = data[2]|data[3]<<8|data[4]<<16|data[5]<<24
        return weight
    except Exception as ex:
      # print(ex)
      return 0.0
# bus=smbus.SMBus(1)
# sensor = Force(bus=bus)
# buff_send=[0x01,0x00,0x00,0x00,0x00,0x15]
# while True:
#     try:
#         data = sensor.read_reg(0x01,7)
#         print("raw data:",data)
#         check_sum=0
#         for i in range(len(data)-1):
#           check_sum=check_sum+data[i]
#         if (check_sum&0xFF)!=data[len(data)-1]:
#           print('error checksum data')
#         else:
#           weight = data[2]|data[3]<<8|data[4]<<16|data[5]<<24
#           print('weight:',weight)
        
        
#         time.sleep(1)
#     except OSError as ex:
#         print(ex)
#         time.sleep(1)
