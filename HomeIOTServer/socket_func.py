



def disconnect_sock(sock, d_name, connection_list):
	try:
		device_name = d_name[sock]
		del d_name[sock]
	except Exception as e:
		print ('No Clinet Device name exist ')	

	connection_list.remove(sock)
	sock.close()
	print('[INFO][%s] Disconnected ' % time.ctime())

def sendDataToSocket():