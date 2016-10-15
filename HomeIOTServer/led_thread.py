import time 
import threading
from socket import *

RSP_TIME = 6
RSP_TRY_COUNT = 5

b_table = ('Dark','Bright')
LedJarThreadLock = threading.Lock()
WaitTimer = threading.Lock()

wait_timer = list()
wait_timer_dev = list()

class LedJarThread(threading.Thread):
	class_val = 0
	def __init__(self,ID,name,delay,function, *args):
		threading.Thread.__init__(self)
		self.ID = ID
		self.name = name
		self.delay = delay
		self.function = function
		self.input_tuple = tuple(value for _, value in enumerate(args))

	def run(self):
		print "starting " + self.name
		LedJarThreadLock.acquire()
		self.function(*self.input_tuple)
		LedJarThreadLock.release()
		print "Endiing" + self.name

def print_time(threadName, delay):
	count = 5
	while count:
		time.sleep(delay)
		print threadName, ' time : ',time.strftime('%H:%M:%S')
		count -= 1

class LedJarTimer:
	kill_evt = 0
	def __init__(self, name,delay,count,fuction,*args):
		self.name = name
		self.delay = delay
		self.count = count
		self.fuction = fuction
		self.args = tuple(value for _, value in enumerate(args))
		self.thread = threading.Timer(self.delay, self.handle_function)

	def handle_function(self):
		self.fuction(*self.args)
		self.thread = threading.Timer(self.delay, self.handle_function)
		self.thread.start()
		if self.count != 0xff:
			if self.count == 0:
				self.thread.cancel()
				self.kill_evt = 1
				print 'Timer will be terminated'
				return
			self.count -= 1

	def start(self):
		print ('[%s]timer start !'%self.name)
		self.thread.start()

	def cancel(self):
		print ('[%s]timer stop !'%self.name)
		self.thread.cancel()


def asgWaitTimer(_wt,_wtd, _d_info, _lrl,_d_name):
	_wt.append(LedJarTimer(_d_name,RSP_TIME,RSP_TRY_COUNT,asgWaitResponseTimer,_d_info,int(_lrl),_d_name))
	_wt[len(wait_timer)-1].start()
	_wtd.append([_d_name, _lrl])
	_str = ('%s wiat timer set' % _d_name)
	print _str
	return _str

def killWaitTimer(_wt,_wtd,_d_name, _lrl):
	for i in range(len(_wtd)):
		if _wtd[i][0] == _d_name and _wtd[i][1] == int(_lrl):
			_wt[i].cancel()
			_wt.pop(i)
			_wtd.pop(i)
			_str = ('%s kill timer' % _d_name)
			print _str
			return _str
	return ' '

def killZombieTimer(_wt,_wtd):
	for i in range(len(_wt)):
		if _wt[i].kill_evt == 1:
			_wt.pop(i)
			dev = _wtd[i][0]
			_wtd.pop(i)
			_str = ('%s kill Zombie Timer' % dev)
			print _str
			return _str

### LEDJAR normal def function ###

def popRoomStateFromList(_device_info, _list_light,_c_light_state):
	if len(_list_light) != 0:
		print 'size of list ', len(_list_light)
		_data = _list_light.pop()
		tmp_str = lambda x:b_table[x]
		Strings = ('room light state was changed !! to %s' % tmp_str(_data[1]))
		print Strings

		_last_room_light = _data[1]
		return _last_room_light
	return 0xff
 
def sendLightStateToDevice(_device_info,state,*args):
	d_name = list()
	for _, _d_name in enumerate(args):
		d_name.append(_d_name)
	

	str_state = ('OFF', 'ON')
	for key, values in _device_info.iteritems():
		if values[0] in d_name:
			sockForSend = key
			_str = 'L'+ str(int(state))
			sockForSend.send(_str)
			_str = ('light %s time'% str_state[state])
			print _str
			return True, values[0]
	return False, ''
# args is specific device 
def sendLightNumToDevice(_device_info,num,*args):
	d_name = list()
	for _, _d_name in enumerate(args):
		d_name.append(_d_name)
	

	str_state = ('OFF', 'ON')
	for key, values in _device_info.iteritems():
		if values[0] in d_name:
			sockForSend = key
			_str = str(int(num))+'\n'
			sockForSend.send(_str)
			print _str
			return True, values[0]
	return False, ''


def checkTimeSection(t_start, t_end):
	t_clock = int(time.strftime('%H'))
	if t_clock == 0:
		t_clock = 24

	if t_start == t_end:
		print 'impossible'
		return False

	if t_start > t_end:
		if t_start <= t_clock < 24:
			return True
		elif int(time.strftime('%H')) < t_end:
			return True
		else:
			return False

	else:
		if t_start <= int(time.strftime('%H')) < t_end:
			return True
		else:
			return False

def checkTwoTimeSection(ts1,te1,ts2,te2):
	if checkTimeSection(ts1,te1) or checkTimeSection(ts2,te2):
		return True
	else:
		return False



def asgWaitResponseTimer(_device_info,_room_state,_d_name):
	WaitTimer.acquire()
	sendLightStateToDevice(_device_info,_room_state,_d_name)
	WaitTimer.release()





	


###################### fuction line ######################

if __name__ == "__main__":

	def printer(para, para2):
		print ('fuck you man [%s],%d - %d'% (time.ctime(),para,para2))

	def test(a,b):
		print a+b

	def looper(func, **kwargs):
		print kwargs
		for _, value in kwargs.iteritems():
			print 'value ', value
		func(*tuple(value for _, value in kwargs.iteritems()))

	def looper2(func, *args):
		for value in enumerate(args):
			print value
		input_tuple = tuple(value for _, value in enumerate(args))
		func(*input_tuple)
	test_list = [0]
	def _lists(_list):
		_list[0] = 1

	print test_list
	_lists(test_list)
	print test_list
	print(checkTimeSection(23,3))
	print(checkTimeSection(3,23))
	print(checkTwoTimeSection(22,5,3,4))
	if checkTwoTimeSection(4,5,23,2):
		print 'Trun ON'
	else:
		print 'Turn OFF'
#	_Device_Info = {'ss' : ['Server', 'dd']}

#	sendLightStateToDevice(_Device_Info,True,'[[Master]]', '[[Nano]]')
#	looper2(test, 45, 35)

#	t1 = LedJarThread(1,'t1',2,print_time,'t1',4)

#	t2 = LedJarThread(2,'t2',3)

	timer1 = LedJarTimer('timer_1',1,2,printer,1,2)
	timer1.start()
	
#	t1.start()
#	t2.start()

	count = 0
	while True:
		print 'hi man ~'
		count += 1
		if count == 8:
			timer1.cancel()
		time.sleep(1)