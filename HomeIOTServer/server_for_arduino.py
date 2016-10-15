
from socket import *
from select import select
import sys
import sched, time
from threading import Timer, Lock
import thread
import scanLightSensor
import subLibFuc
import touch_sensor


_r_time = time.time()
terminate_flag = 0
C_TIME = 120
L_TIME = 60

turn_off_flag = 0
m_light = Lock()

light_Sensor = scanLightSensor.LightSensor()
Touch1 = touch_sensor.TouchSensor()
last_room_light = 3
old_last_room_light = 3
prevent_recall = [True, True]
listLightChange = list()
time_thread_create_flag = 0
static_light = 0
time_state = 0
SessReInfo = 'sessionResetINFO.txt'


#static
s_light_para = 0
s_light_list = list()

LJONTIME1 = (10,17)
LJONTIME2 = (2,6)

def staticLightVal(arg):
	#print ('[%s]static = %d '%(time.ctime(),s_light_para))
	global s_light_list
	global s_light_para
	global static_light
	s_light_list.append(s_light_para)
	if int(time.strftime('%M')) < 1:
		static_light = int(sum(s_light_list)/len(s_light_list))
		strings = 'static = %d '%int(sum(s_light_list)/len(s_light_list))
		write_data_to_file('static.txt', strings)
		s_light_list = list()


def scanLightState(_device_info):
	try:
		isChange = 0
		while True:
			global s_light_para
			m_light.acquire()
			isChange = light_Sensor.checkDarkBrightChange(static_light)
			isChange_list = isChange[0]
			s_light_para = isChange[1]
			#print s_light_para
			
			if isChange_list != 0:
				print 'change para 1'
				listLightChange.append(isChange_list)
				if isChange_list[1] == 0:
					print 'send light number'
					subLibFuc.sendLightNumToDevice(_device_info,2,'[[Nano]]')

			m_light.release()
			time.sleep(0.05)
	except (KeyboardInterrupt, SystemExit):
		print 'Keyboard Interrupt '

def scanTouched(_device_info):
	start_time = 0
	while True:
		click_count = 0
		t_val = Touch1.touch_time()
		click_count = Touch1.multi_click(t_val)
		if click_count > 0:
			for key, values in _device_info.iteritems():
				if values[0] == '[[Master]]' or values[0] == '[[Nano]]':
					start_time = time.time()
					if click_count == 0xf:
						key.send("0")
						start_time = 0
					else:
						key.send("%d" % click_count)
		if start_time > 0 and (time.time() - start_time) > 10:
			for key, values in _device_info.iteritems():
				if values[0] == '[[Master]]' or values[0] == '[[Nano]]':
					key.send("0")
			start_time = 0


def session_timer(sock):	
	global _r_time
	global C_TIME
	global terminate_flag
	try:
		_time = time.time() - _r_time
		if _time > C_TIME*3 + 30:
			terminate_flag = 1
			write_data_to_file(SessReInfo,'Arduino no answer Session timer Terminate !')
			return

		sock.send('OK')
		print 'send ok '
		_str = 'Send Ok, Time Past from Geting RSP = %d' % _time
		write_data_to_file(SessReInfo,_str)
	except IOError as e:
		write_data_to_file(SessReInfo, 'send error timer will be terminated ')
		print 'send error timer will be terminated '
		return
	
	Timer(C_TIME,session_timer,[sock]).start()

def print_deviceinfo(d_name):
	val_list = list()
	i = 1
	strtmp = '\n' + '-'*8 + 'Conn_info' + '-'*8 + '\n'
	for key, value in d_name.iteritems():
		strtmp += str(i) + '. ' + ',  '.join(value) + '\n'
		i += 1
	print strtmp
	return strtmp

def print_timerinfo(_wait_timer, _wait_time_de):
	i = 1
	strtmp = '\n' + '-'*8 + 'timer_info' + '-'*8 + '\n'
	for key in range(len(_wait_timer)):
		strtmp += str(i) + '. ' + _wait_timer[key].name + '\n'
		i += 1
	i = 1
	for key in range(len(_wait_time_de)):
		strtmp += ' ' + '. ' + str(_wait_time_de[key]) + '\n'
		i += 1
	
	return strtmp

def print_lightinfo(_DI,_sl,_slp,_lrl, _ts):

	strtmp = '\n' + '-'*8 + 'light_info' + '-'*8 + '\n'
	strtmp += 'Static Light Val(1h) 		: %d \n' % _sl
	strtmp += 'Moment Light Val 			: %d \n' % _slp
	_state = ['Dark','Bright']
	strtmp += 'Last Light Val of Room 	: %s \n' % _state[_lrl]
	_state = ['LEDJar Turn On time','LedJar Turn OFF time']
	strtmp += 'LEDJar Operate time 		: %s \n' % _state[_ts]
	
	device_exist = 0
	for key, values in _DI.iteritems():
		if values[0] == '[[Nano]]':
			device_exist = 1
	
	if _lrl == 0 and _ts == 0 and device_exist == 1:
		operate = 1
	else:
		operate = 0

	_state = ['NO','YES']
	strtmp += 'LedJar Operation? 		: %s \n' % _state[operate]
	return strtmp

	

HOST = ''
PORT = 9898
BUFSIZE = 1024
ADDR = (HOST, PORT)
SESSION_RESET_TIME=0

serv_sock = socket(AF_INET, SOCK_STREAM)
sock_opt = 1;
serv_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, sock_opt);
serv_sock.bind(ADDR)
serv_sock.listen(10)
connection_list = [serv_sock]
#need ip 
Device_Info = {serv_sock : ['Server', HOST]}
print 30*'='
print('Start Chating')
print 30*'='


thread.start_new_thread(scanLightState,(Device_Info,))
thread.start_new_thread(scanTouched,(Device_Info,))

lightTimer = subLibFuc.LedJarTimer('lightSensor',L_TIME,0xff,staticLightVal,s_light_para)
lightTimer.start()

while connection_list:

	m_light.acquire()	
	subLibFuc.killZombieTimer(subLibFuc.wait_timer,subLibFuc.wait_timer_dev)
	_last_room_light = subLibFuc.popRoomStateFromList(Device_Info, listLightChange,last_room_light)
	if _last_room_light != 0xff:
		last_room_light = _last_room_light
		print 'last room light = ', last_room_light
	listLightChange = list()

	if subLibFuc.checkTwoTimeSection(LJONTIME1[0],LJONTIME1[1],LJONTIME2[0],LJONTIME2[1]):
		if prevent_recall[0]:
			prevent_recall[1] = True
			prevent_recall[0] = not prevent_recall[0]
			write_data_to_file('LightOffTimeLog.txt', 'Light ON')
		last_room_light = 1
		time_state = 1
		#Don't change room state even light sensor detect dark 
		#because it's time for Stoping LEDJAR
	else:
		if prevent_recall[1]:
			prevent_recall[0] = True
			prevent_recall[1] = not prevent_recall[1]	
			#last_room_light = 0
			write_data_to_file('LightOffTimeLog.txt', 'Light OFF')
		time_state = 0
		#change the room state if light sensor detect change 
		
	# important L1(light room) means LEDJAR OFF L0(dark room) means LEDJAR ON

	if old_last_room_light != last_room_light:
		res = subLibFuc.sendLightStateToDevice(Device_Info,int(last_room_light),'[[Master]]', '[[Nano]]')
		if res[0] == True:
			_str = subLibFuc.asgWaitTimer(subLibFuc.wait_timer,subLibFuc.wait_timer_dev,Device_Info,last_room_light,'[[Nano]]')
			write_data_to_file('INFO.txt',_str)

	old_last_room_light = last_room_light

	m_light.release()
	
	try:

		rd_sock, wr_sock, error_sock = select(connection_list, [], [], 10)

		for sock in rd_sock:
			if sock == serv_sock:
				clnt_sock, addr_info = serv_sock.accept()
				connection_list.append(clnt_sock)
				Device_Info[clnt_sock] = ['', addr_info[0]]

				print('[INFO][%s] Client(%s) Connected brand new ' % (time.ctime(), addr_info[0]))


				for sock_in_list in connection_list:
					if sock_in_list != serv_sock and sock_in_list != sock:
						try:
							sock_in_list.send('New member ')
						except Exception as e:
							sock_in_list.close()
							connection_list.remove(sock_in_list)

			else:
				try:
					data = sock.recv(BUFSIZE)
				except Exception as e:
					print 'reset error '
					pass
				if data:
					D_NAME = Device_Info[sock][0]
					print ('%s[%s] Data Recieved from client !!' % (D_NAME,time.ctime()))
					print 'Recieved data : ' + data
					#device name add routine 
					if data[0:2] == '[[' and ']]' in data:
						chtmp = data.find(']]')
						if chtmp != -1:
							device_name = data[:chtmp+2] 
							if len(device_name) == len(data):
								if Device_Info[sock][0] == '':
									Device_Info[sock][0] = data[:chtmp+2]

									_str_data = 'L' + str(last_room_light)
									sock.send(_str_data)	
									

									_str = subLibFuc.asgWaitTimer(subLibFuc.wait_timer,subLibFuc.wait_timer_dev,Device_Info,last_room_light,data[:chtmp+2])
									write_data_to_file('INFO.txt',_str)

									if data[0:len('[[Nano]]')] == '[[Nano]]':
										_r_time = time.time()
										print 'Thread will be registered'
										thread.start_new_thread(session_timer,(sock,))

									string = ('%s New DEVICE Connected ' %  Device_Info[sock][0])
									write_data_to_file('INFO.txt',string)
								else:
				 					sock.send('Duplicate name Change Name')
								 	disconnect_sock(sock,Device_Info,connection_list)
								 	print('%s[%s] Duplicate Device Disconnect ' % (data,time.ctime()))
									string = ('%sDuplicate Device Disconnect' %  Device_Info[sock][0])
									write_data_to_file('INFO.txt',string)

							else:
							 	strtmp = data.find('connect')
							 	if strtmp != -1:
							 		_r_time = time.time()
							 		index = data.find('(')

							 		_str = 'link check ! arduino time %s' % data[index:]
							 		print ('Got Connected')
							 		write_data_to_file(SessReInfo,_str)

						else:
							print ('Device ID format was wrong')
							
						continue


					elif 'r_time' in data:
						r_time = data[len('r_time='):]
						SESSION_RESET_TIME = int(r_time)
						print ('%sSESSION_RESET_TIME = %d' % (D_NAME,SESSION_RESET_TIME))
						string = ('%sSESSION_RESET_TIME = %d' % (D_NAME,SESSION_RESET_TIME))
						write_data_to_file('INFO.txt',string)
					
					elif 'ShutDown' in data:
						index = data.find('(')
						write_data_to_file(SessReInfo, data[index:])		
					
					#print Device info 
					elif data[0:1] == 'P' and Device_Info[sock][0] == '[[Master]]':
						_str = print_deviceinfo(Device_Info)
						_str += print_timerinfo(subLibFuc.wait_timer,subLibFuc.wait_timer_dev)
						_str += print_lightinfo(Device_Info,static_light,s_light_para,last_room_light,time_state)
						sock.send(_str)
						continue

					elif data[0:3] == 'RSP' and (Device_Info[sock][0] == '[[Nano]]' or Device_Info[sock][0] == '[[Master]]'):
						_str=subLibFuc.killWaitTimer(subLibFuc.wait_timer,subLibFuc.wait_timer_dev,Device_Info[sock][0],data[3])
						write_data_to_file('INFO.txt',_str)
						continue


					#force disconnect 
					elif data[:1] == 'D' and Device_Info[sock][0] == '[[Master]]':
						if data[1:].isspace() == False:
							index = int(data[1:])
							if index > 0 and index <= len(Device_Info):
								dis_sock = Device_Info.keys()[index - 1]
								if dis_sock != serv_sock and Device_Info.values()[index - 1][0] != '[[Master]]':
									disconnect_sock(dis_sock, Device_Info, connection_list)
								else:
									print ('Can not disconnect server sock and Master Clinet !!!!!')
									sock.send('Can not disconnect server sock and Master Clinet !!!!!')
							else:
								print ('index should be 1 ~ %d' % len(Device_Info))
								sock.send('index should be 1 ~ %d' % len(Device_Info))
						else:
							print ('please input index like "D1" ... ')
							sock.send('please input index like "D1" ... ')

						continue
					elif 'motion' in data:

						if 'detected' in data[len('motion'):]:
							write_data_to_file('INFO.txt','Motion detected')
						elif 'ended' in data[len('motion'):]:
							write_data_to_file('INFO.txt','Motion Ended')

					if Device_Info[sock][0] == '[[Master]]':
						for sock_in_list in connection_list:
							if sock_in_list != serv_sock and sock_in_list != sock:
								try:
									sock_in_list.send('%s' % data)
								except Exception as e:
									print(e.message)
									sock_in_list.close()
									connection_list.remove(sock_in_list)
									continue

				else:
					disconnect_sock(sock, Device_Info,connection_list)

		if terminate_flag == 1:
			terminate_flag = 0
			_r_time = time.time();
			print 'disconnected time out '
			write_data_to_file(SessReInfo,'TimeOut Disconnect')
			for key, values in Device_Info.iteritems():
				if values[0] == '[[Nano]]':
					dis_sock = key

			disconnect_sock(dis_sock, Device_Info,connection_list)
			
	
	except KeyboardInterrupt:
	# smooth close
		serv_sock.close()
		sys.exit()





