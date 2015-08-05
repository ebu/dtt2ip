#!/usr/bin/python

from discoveryServer import discoveryServer
from rtspServer import rtspServer
from scanning import scanning
import threading

def main():
	# Make sure that t2IP.log file is clean
	fLog = open('logs/t2IP.log', 'w')

	# Thread 1 discoveryServer 
	t1 = threading.Thread(target=discoveryServer)
	t1.daemon = True
	t1.start()
	fLog.write('Info: discoveryServer started\n')
	fLog.close()

	# Thread 2 rtspServer
	fLog = open('logs/t2IP.log', 'a')
	t2 = threading.Thread(target=rtspServer)
	t2.daemon = True
	t2.start()
	fLog.write('Info: rtspServer started\n')
	fLog.close()

	# Thread 3 scanning (w_scan)
	# Default period for new scan is 3600 seconds.
	# periodNewScan = 3600 
	# scanningFlag = 0
	# t3 = threading.Thread(target=scanning, args=[periodNewScan, scanningFlag])
	# t3.daemon = True
	# t3.start()
	# fLog.write('Info: scanning started\n')
	# fLog.write('Info: period for new scan is ' + str(periodNewScan) + ' and scanningFlag is ' + str(scanningFlag))
	# fLog.close()

	# Keep threads alive until KeyboardInterrupt
	try:
		while t1.is_alive() and t2.is_alive():
			pass
	except (KeyboardInterrupt, SystemExit):
		print "Info: t2IP server stoped"

if __name__ == '__main__':
	main()