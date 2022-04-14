CAL1_V = 1600
CAL1_T = 25
CAL2_V = 1300
CAL2_T = 15
oxygen_temperature = 25
# DO=None
V_saturation = CAL1_V + 35.0*oxygen_temperature - CAL1_T*35.0
DO_Table=[14460, 14220, 13820, 13440, 13090, 12740, 12420, 12110, 11810, 11530,11260, 11010, 10770, 10530, 10300, 10080, 9860, 9660, 9460, 9270, 9080, 8900, 8730, 8570, 8410, 8250, 8110, 7960, 7820, 7690,7560, 7430, 7300, 7180, 7070, 6950, 6840, 6730, 6630, 6530, 6410]

def convertWaterOxygen(raw_data):
	aver_val = raw_data
	mV = aver_val*4.096*1000/32767
	# print(mV)
	DO = mV*DO_Table[oxygen_temperature]/(1000.0*V_saturation)
	return round(DO,2)