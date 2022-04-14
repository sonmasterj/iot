m=(4-7.07)/(0.583-1.019)
b= 4-m*0.583
def convertPH(raw_data):
    aver_val = raw_data
    mV = aver_val*4.096/32767
    # print(mV)
    pH= (m*mV) + b
    return round(pH,1)
