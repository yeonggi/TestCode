import os
import sys
import Adafruit_BBIO.ADC as ADC
import time 


def writeDataToFile(f_name,str_to_write):
        try:
                f = open(f_name, 'r+')
        except IOError as e:
                print f_name, '  Created '
                f=open(f_name,'w+')

        f.read()
        pos = f.tell()
        f.seek(pos)
        string = ('[INFO][%s]  ' % time.ctime() + str_to_write + '\n')
        f.write(string)
        f.close()

class LightSensor:
	str_state = ['dark', 'bright']
	state = 0
	old_state = 0
	
	def __init__(self):
		ADC.setup()

	def checkDarkBrightChange(self):
		value = ADC.read("P9_40")	
		value = ADC.read_raw("P9_40")
		if value < 80:
			self.state = 0
		else:
			self.state = 1
		print value
		if self.old_state != self.state:
			strings = ('state has changed %s to %s ' % (self.str_state[self.old_state], self.str_state[self.state]))
			print ('state has changed %s to %s ' % (self.str_state[self.old_state], self.str_state[self.state]))
			writeDataToFile('light_state.txt',strings)
		self.old_state = self.state
				


if __name__ == "__main__":
	light_check = LightSensor()
	while True:
		light_check.checkDarkBrightChange()
		time.sleep(0.05)
