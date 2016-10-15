import socket
import threading
import sys

BUFFSIZE = 1024
def sendingMsg():
	global conn
	while True:
		try:
			data = raw_input()
		except KeyboardInterrupt:
			conn.close()
			exit()

		#data = bytes(data,"utf-8")
		conn.send(data)

	conn.close()

#need mutex
def gettingMsg():
	global conn
	while True:
		data = conn.recv(BUFFSIZE)
		if not data: 
			break
		else:
			#data = str(data).split("b'", 1)[1].rsplit("'",1)[0]
			print(data)
	conn.close()


if __name__=="__main__":
	HOST = ''                
	PORT = 9898
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((HOST, PORT))
	s.listen(1)
	conn, addr = s.accept()
	print('Connected by', addr)

	threading._start_new_thread(sendingMsg,())
	threading._start_new_thread(gettingMsg,())

	while True:
		pass