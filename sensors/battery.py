import serial
import re
serial_port ='/dev/ttyUSB0'
class UPS2:
    def __init__(self):
        self.success=True
        try:
            self.ser  = serial.Serial(serial_port,9600)   
        except:
            self.success = False
        
    def get_data(self,nums):

        while True:
            self.count = self.ser.inWaiting()
            
            if self.count !=0:
                self.recv = self.ser.read(nums)
                return self.recv
    
    def decode_uart(self):
        if self.success==False:
            return 'NG',0
        self.uart_string = self.get_data(100)
#    print(uart_string)
        self.data = self.uart_string.decode('ascii','ignore')
#    print(data)
        self.pattern = r'\$ (.*?) \$'
        self.result = re.findall(self.pattern,self.data,re.S)
    
        self.tmp = self.result[0]
    
        # self.pattern = r'SmartUPS (.*?),'
        # self.version = re.findall(self.pattern,self.tmp)
    
        self.pattern = r',Vin (.*?),'
        self.vin = re.findall(self.pattern,self.tmp)
        
        self.pattern = r'BATCAP (.*?),'
        self.batcap = re.findall(self.pattern,self.tmp)
        
        # self.pattern = r',Vout (.*)'
        # self.vout = re.findall(self.pattern,self.tmp)

        return self.vin[0],self.batcap[0]
    def close_serial(self):
        if self.success == False:
            return
        self.ser.close()