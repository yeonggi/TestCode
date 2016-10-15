import Adafruit_BBIO.GPIO as GPIO

GPIO.setup("P9_12", GPIO.IN)
old_val = 0
val = 0
while True:
	val = GPIO.input("P9_12")
	if(old_val != val):	
		if val:
			print "HIGH"
		else:
			print "LOW"
	old_val = val
	
GPIO.cleanup()
