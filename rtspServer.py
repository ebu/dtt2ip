#!/usr/bin/python

import sys, socket, signal, commands, re

from rtspServerWorker import rtspServerWorker
from netInterfaceStatus import getServerIP

# class rtspServer:
def clean():
	# Make sure that rtspServer.log file is clean
	fLog = open('logs/rtspServer.log', 'w')
	# Make sure that all dvblast sockets are deleted before you start the rtsp state machine
	cmd = 'rm -rf /tmp/dvblast*'
	fLog.write('Info rtspServer: Cleaning dvblast sockets before starting\n')
	outtext = commands.getoutput(cmd)
	(exitstatus, outtext) = commands.getstatusoutput(cmd)
	# if not exitstatus:
		# fLog.write('Info rtspServer: Dvblast sockets clean\n')
	
	# Make sure that all the pidCfgFiles are clean before you start the rtsp state machine
	cmd = 'ls -l dvb-t/pid*'
	fLog.write('Info rtspServer: Cleaning all pidCfgFiles\n')
	outtext = commands.getoutput(cmd)
	(exitstatus, outtext) = commands.getstatusoutput(cmd)
	if not exitstatus:
		linesArray = outtext.split('\n')
		for line in linesArray:
			matchPidCfgFile = re.search(r'pid([\w]+)', line)
			if matchPidCfgFile:
				f = open('dvb-t/pid' + matchPidCfgFile.group(1) + '.cfg', 'w')
				f.close()
		fLog.write('Info rtspServer: pidCfgFiles clean\n')
	fLog.close()

	# def main(self):
def rtspServer():
	# Cleaning everything
	clean()

	# Make sure you have root privileges to run this script
	# it is necesary that we can open the "554" port
	serverPort = 554
	rtspSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	ipAddrServer = getServerIP()
	rtspSocket.bind((ipAddrServer, serverPort))
	while (1):
		# Listen for incoming connections
		rtspSocket.listen(1)

		# Create the client profile and store necesary information
		clientInfo = {}
		clientInfo['rtspSocket'], addr = rtspSocket.accept()
		clientInfo['addr_IP'] = addr[0]
		clientInfo['addr_PORT'] = addr[1]

		# Run the rtspServerWorker for that specific client
		rtspServerWorker(clientInfo).run()
		
	rtspSocket.close()

if __name__ == "__main__":
	# (rtspServer()).main()
	rtspServer()
