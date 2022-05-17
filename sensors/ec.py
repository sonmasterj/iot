RES2=820.0
ECREF=200.0
ec_value_raw = 0.0
k_value =1.52
ec_value = 0
t_dungdich = 25
ec_temperature = 25.0
def convertEC(raw_data):
    aver_val =abs(raw_data)
    mV = aver_val*4096/32767
    # print(aver_val)
    ec_value_raw = (1000.0*mV/RES2/ECREF)*(k_value)
    ec_value = ec_value_raw/(1.0+0.0185*(ec_temperature-25.0))
    return round(ec_value,2)