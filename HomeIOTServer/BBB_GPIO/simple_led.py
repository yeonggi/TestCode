import Adafruit_BBIO.GPIO as GPIO
import time 

GPIO.setup("P9_11",GPIO.OUT)

while True:
	GPIO.output("P9_11",GPIO.HIGH)
	time.sleep(1)
	GPIO.output("P9_11",GPIO.LOW)
	time.sleep(1)

