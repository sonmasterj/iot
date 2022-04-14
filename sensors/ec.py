RES2=(7500.0/0.66)
ECREF=20.0
ec_value_raw = 0.0
k_value = 0.74
ec_value = 0
t_dungdich = 25
ec_temperature = 25.0
def convertEC(raw_data):
    aver_val =abs(raw_data)
    mV = aver_val*4.096/32767
    # print(aver_val)
    ec_value_raw = (1000.0*mV/RES2/ECREF)*(k_value*10.0)
    ec_value = ec_value_raw/(1.0+0.0185*(ec_temperature-25.0))
    return round(ec_value,2)