#!/usr/bin/python

from discoveryServer import discoveryServer
from rtspServer import rtspServer
from scanning import scanning
import threading

def main():
	# Make sure that t2IP.log file is clean
	fLog = open('logs/t2IP.log', 'w')

	t1 = threading.Thread(target=discoveryServer)
	t1.daemon = True
	t1.start()
	fLog.write('Info: discoveryServer started\n')

	t2 = threading.Thread(target=rtspServer)
	t2.daemon = True
	t2.start()
	fLog.write('Info: rtspServer started\n')

	# Default period for new scan is 3600 seconds.
	# periodNewScan = 3600 
	# scanningFlag = 0
	# t3 = threading.Thread(target=scanning, args=[periodNewScan, scanningFlag])
	# t3.daemon = True
	# t3.start()
	# fLog.write('Info: scanning started\n')
	# fLog.write('Info: period for new scan is ' + str(periodNewScan) + ' and scanningFlag is ' + str(scanningFlag))

	# Keep threads alive until KeyboardInterrupt
	try:
		while t1.is_alive() and t2.is_alive():
			pass
	except (KeyboardInterrupt, SystemExit):
		fLog.close()
		SSDP_TERMINATE = 1

if __name__ == '__main__':
	main()