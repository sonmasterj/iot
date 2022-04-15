from ultil.asyncSleep import delay

# Get I2C bus


# I2C address of the device
SHT31_DEFAULT_ADDRESS				= 0x44

# SHT31 Command Set
SHT31_MEAS_REP_STRETCH_EN			= 0x2C # Clock stretching enabled
SHT31_MEAS_HIGH_REP_STRETCH_EN		= 0x06 # High repeatability measurement with clock stretching enabled
SHT31_MEAS_MED_REP_STRETCH_EN		= 0x0D # Medium repeatability measurement with clock stretching enabled
SHT31_MEAS_LOW_REP_STRETCH_EN		= 0x10 # Low repeatability measurement with clock stretching enabled
SHT31_MEAS_REP_STRETCH_DS			= 0x24 # Clock stretching disabled
SHT31_MEAS_HIGH_REP_STRETCH_DS		= 0x00 # High repeatability measurement with clock stretching disabled
SHT31_MEAS_MED_REP_STRETCH_DS		= 0x0B # Medium repeatability measurement with clock stretching disabled
SHT31_MEAS_LOW_REP_STRETCH_DS		= 0x16 # Low repeatability measurement with clock stretching disabled
SHT31_CMD_READSTATUS				= 0xF32D # Command to read out the status register
SHT31_CMD_CLEARSTATUS				= 0x3041 # Command to clear the status register
SHT31_CMD_SOFTRESET					= 0x30A2 # Soft reset command
SHT31_CMD_HEATERENABLE				= 0x306D # Heater enable command
SHT31_CMD_HEATERDISABLE				= 0x3066 # Heater disable command

class SHT31():
    def __init__(self,bus):
        self.bus =bus
    def _crc(self,data):
        crc=0xFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x80:
                    crc <<= 1
                    crc ^= 0x31
                else:
                    crc <<= 1
        return crc & 0xFF
    def read_data(self):
        """Read data back from device address, 6 bytes
        temp MSB, temp LSB, temp CRC, humidity MSB, humidity LSB, humidity CRC"""
        try:
            COMMAND = [SHT31_MEAS_HIGH_REP_STRETCH_EN]
            self.bus.write_i2c_block_data(SHT31_DEFAULT_ADDRESS, SHT31_MEAS_REP_STRETCH_EN, COMMAND)
            delay(0.05)
            data = self.bus.read_i2c_block_data(SHT31_DEFAULT_ADDRESS, 6)
            
            # temp=None
            humidity=-1
            # Convert the data
            # if data[2]!=self._crc(data[0:2]):
            #     temp=-1
            # else:
            #     val = data[0] * 256 + data[1]
            #     temp = -45 + (175 * val / 65535.0)
            if data[5]!= self._crc(data[3:5]):
                humidity=-1
            else:
                humidity = 100 * (data[3] * 256 + data[4]) / 65535.0
            
            return round(humidity,1)
        except IOError:
            return 0.0