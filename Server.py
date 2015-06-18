#!/usr/bin/python

import sys, socket, signal

from ServerWorker import ServerWorker
from netInterfaceStatus import getServerIP

class Server:	
	
	def main(self):
		serverPort = 554
		# try:
		# 	SERVER_PORT = int(sys.argv[1])
		# except:
		# 	print "[Usage: Server.py Server_port]\n"
		rtspSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		ipAddrServer = getServerIP()

		rtspSocket.bind((ipAddrServer, serverPort))
		# rtspSocket.bind(('192.168.2.60', SERVER_PORT))
		# rtspSocket.bind(('10.50.216.140', SERVER_PORT))

		while (1):
			rtspSocket.listen(1)        

			# Receive client info (address,port) through RTSP/TCP session
			# while True:

			clientInfo = {}
			clientInfo['rtspSocket'], addr = rtspSocket.accept()
			clientInfo['addr_IP'] = addr[0]
			clientInfo['addr_PORT'] = addr[1]
			
			# print "ALEX 1"
			ServerWorker(clientInfo).run()
			# print "Alex 2"
			
		rtspSocket.close()

if __name__ == "__main__":
	(Server()).main()
