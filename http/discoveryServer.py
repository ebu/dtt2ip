#!/usr/bin/python
 
# Discovery state machine
# SSDP protocol
 
import sys, re, os, random
import threading, socket, struct, time, calendar
from netInterfaceStatus import getServerIP

from datetime import date, datetime

global SSDP_TERMINATE
global deviceIdOk
global ssdpAddr, ssdpPort, serverIP
global paramDict
global NT, USN, st
global fLog


# paramDict = {}
# f = open("discoveryServer.config", 'r')
# lines = f.readlines()
# for i in range(5, len(lines)):
# 	line = lines[i]
# 	lineArray = line.split('=')
# 	lineArray[0] = lineArray[0][:-1]
# 	lineArray[1] = lineArray[1][1:-1]
# 	paramDict[lineArray[0]] = lineArray[1]
# f.close()
SSDP_TERMINATE = 0

deviceIdOk = False

ssdpAddr = '239.255.255.250'
ssdpPort = 1900

serverIP = getServerIP()
httpPort = 8080

# nt1 = 'upnp:' + paramDict['upnp']
# nt2 = 'uuid:' + paramDict['uuid']
# nt3 = 'urn:' + paramDict['urn']
# NT = [nt1, nt2, nt3]

# usn1 = 'uuid:' + paramDict['uuid'] + '::upnp:' + paramDict['upnp']
# usn2 = 'uuid:' + paramDict['uuid']
# usn3 = 'uuid:' + paramDict['uuid'] + '::urn:' + paramDict['urn']
# USN = [usn1, usn2, usn3]

# st = 'urn:' + paramDict['urn']
# To Do make configuration file

def ms_ok(counter):
	# MS_OK message is used to inform the client about the presents of the DTT2IP / SAT>IP server on the network
	# or to inform the other DTT2IP / SAT>IP servers that M-SEARCH message has been correctly received

	# This one works
	# MS_OK = 'HTTP/1.1 200 OK\r\nLOCATION: http://192.168.1.115:8080/alexDescription.xml\r\nCACHE-CONTROL: max-age=1800\r\nServer: UPnp/1.0 DLNADOC/1.50 Platinum/1.0.4.11\r\nEXT:\r\nUSN: uuid:b7531642-0123-3210-bbbb-0016406436F6::urn:schemas-upnp-org:device:MediaServer:1\r\nST: urn:schemas-upnp-org:device:MediaServer:1\r\nDate: Sat, 01 Jan 2000 00:03:17 GMT\r\n\r\n'

	if counter == 0:
		MS_OK = 'HTTP/1.1 200 OK\r\nCACHE-CONTROL: max-age=90\r\nDATE: Wed, 06 Jan 2016 13:45:21 GMT\r\nEXT:\r\nLOCATION: http://' + serverIP + ':' + str(httpPort) + '/alexDescription.xml\r\nServer: BaseHTTP/0.3 Python/2.7.10\r\nX-User-Agent: redsonic\r\nST: upnp:rootdevice\r\nUSN: uuid:C0A80173-0000-5687-83E3-00000000001F::upnp:rootdevice\r\nCONTENT-LENGTH: 0\r\n\r\n'
	if counter == 1:
		MS_OK = 'HTTP/1.1 200 OK\r\nCACHE-CONTROL: max-age=90\r\nDATE: Wed, 06 Jan 2016 13:45:21 GMT\r\nEXT:\r\nLOCATION: http://' + serverIP + ':' + str(httpPort) + '/alexDescription.xml\r\nServer: BaseHTTP/0.3 Python/2.7.10\r\nX-User-Agent: redsonic\r\nST: uuid:C0A80173-0000-5687-83E3-00000000001F\r\nUSN: uuid:C0A80173-0000-5687-83E3-00000000001F\r\nCONTENT-LENGTH: 0\r\n\r\n'
	if counter == 2:
		MS_OK = 'HTTP/1.1 200 OK\r\nCACHE-CONTROL: max-age=90\r\nDATE: Wed, 06 Jan 2016 13:45:21 GMT\r\nEXT:\r\nLOCATION: http://' + serverIP + ':' + str(httpPort) + '/alexDescription.xml\r\nServer: BaseHTTP/0.3 Python/2.7.10\r\nX-User-Agent: redsonic\r\nST: urn:schemas-upnp-org:device:MediaServer:1\r\nUSN: uuid:C0A80173-0000-5687-83E3-00000000001F::urn:schemas-upnp-org:device:MediaServer:1\r\nCONTENT-LENGTH: 0\r\n\r\n'
	if counter == 3:
		MS_OK = 'HTTP/1.1 200 OK\r\nCACHE-CONTROL: max-age=90\r\nDATE: Wed, 06 Jan 2016 13:45:21 GMT\r\nEXT:\r\nLOCATION: http://' + serverIP + ':' + str(httpPort) + '/alexDescription.xml\r\nServer: BaseHTTP/0.3 Python/2.7.10\r\nX-User-Agent: redsonic\r\nST: urn:schemas-upnp-org:service:ContentDirectory:1\r\nUSN: uuid:C0A80173-0000-5687-83E3-00000000001F::urn:schemas-upnp-org:service:ContentDirectory:1\r\nCONTENT-LENGTH: 0\r\n\r\n'
	if counter == 4:
		MS_OK = 'HTTP/1.1 200 OK\r\nCACHE-CONTROL: max-age=90\r\nDATE: Wed, 06 Jan 2016 13:45:21 GMT\r\nEXT:\r\nLOCATION: http://' + serverIP + ':' + str(httpPort) + '/alexDescription.xml\r\nServer: BaseHTTP/0.3 Python/2.7.10\r\nX-User-Agent: redsonic\r\nST: urn:schemas-upnp-org:service:ConnectionManager:1\r\nUSN: uuid:C0A80173-0000-5687-83E3-00000000001F::urn:schemas-upnp-org:service:ConnectionManager:1\r\nCONTENT-LENGTH: 0\r\n\r\n'
	if counter == 5:
		MS_OK = 'HTTP/1.1 200 OK\r\nCACHE-CONTROL: max-age=90\r\nDATE: Wed, 06 Jan 2016 13:45:22 GMT\r\nEXT:\r\nLOCATION: http://' + serverIP + ':' + str(httpPort) + '/alexDescription.xml\r\nServer: BaseHTTP/0.3 Python/2.7.10\r\nX-User-Agent: redsonic\r\nST: urn:schemas-upnp-org:device:MediaServer:1\r\nUSN: uuid:C0A80173-0000-5687-83E3-00000000001F::urn:schemas-upnp-org:device:MediaServer:1\r\nCONTENT-LENGTH: 0\r\n\r\n'
	return MS_OK

def ms_notify_alive(counter):	
	# MS_NOTIFY_ALIVE is use to inform other DTT2IP / SAT>IP servers about our presents in the network. Used in the DEVICE ID negotiation
	# This is the old NOTIFY for SAT>IP
	# MS_NOTIFY_ALIVE = 'NOTIFY * HTTP/1.1\r\nHOST: %s:%d\r\nBOOTID.UPNP.ORG:%d\r\nCONFIGID.UPNP.ORG:%d\r\nCACHE-CONTROL: max-age=%d\r\nLOCATION:http://%s:%d/%s\r\nNT:%s\nNTS:%s\nSERVER:%s\nUSN:%s\nDEVICEID.SES.COM:%d\r\n\r\n' % (ssdpAddr, ssdpPort, int(paramDict['bootId']), int(paramDict['configId']), int(paramDict['cacheControl']), serverIP, int(paramDict['httpPort']), paramDict['location'], nt, 'ssdp:alive', paramDict['server'], usn, int(paramDict['deviceId']))
	
	# MS_NOTIFY_ALIVE = 'NOTIFY * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\nCACHE-CONTROL: max-age=90\r\nLOCATION: http://192.168.1.115:80/nmsDescription.xml\r\nNT: upnp:rootdevice\r\n NTS: ssdp:alive\r\n Server: BaseHTTP/0.3 Python/2.7.10\r\nX-User-Agent: redsonic\r\nUSN: uuid:5AFEF00D-BABE-DADA-FA5A-0023549E9B13::upnp:rootdevice\r\nCONTENT-LENGTH: 0\r\n\r\n'
	if counter == 0:
		MS_NOTIFY_ALIVE = 'NOTIFY * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\nCACHE-CONTROL: max-age=90\r\nLOCATION: http://' + serverIP + ':' + str(httpPort) + '/alexDescription.xml\r\nNT: upnp:rootdevice\r\n NTS: ssdp:alive\r\n Server: BaseHTTP/0.3 Python/2.7.10\r\nX-User-Agent: redsonic\r\nUSN: uuid:C0A80173-0000-5687-83E3-00000000001F::upnp:rootdevice\r\nCONTENT-LENGTH: 0\r\n\r\n'
	if counter == 1:
		MS_NOTIFY_ALIVE = 'NOTIFY * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\nCACHE-CONTROL: max-age=90\r\nLOCATION: http://' + serverIP + ':' + str(httpPort) + '/alexDescription.xml\r\nNT: uuid:C0A80173-0000-5687-83E3-00000000001F\r\nNTS: ssdp:alive\r\nServer: BaseHTTP/0.3 Python/2.7.10\r\nX-User-Agent: redsonic\r\nUSN: uuid:C0A80173-0000-5687-83E3-00000000001F\r\nCONTENT-LENGTH: 0\r\n\r\n'
	if counter == 2:
		MS_NOTIFY_ALIVE = 'NOTIFY * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\nCACHE-CONTROL: max-age=90\r\nLOCATION: http://' + serverIP + ':' + str(httpPort) + '/alexDescription.xml\r\nNT: urn:schemas-upnp-org:device:MediaServer:1\r\nNTS: ssdp:alive\r\nServer: BaseHTTP/0.3 Python/2.7.10\r\nX-User-Agent: redsonic\r\nUSN: uuid:C0A80173-0000-5687-83E3-00000000001F::urn:schemas-upnp-org:device:MediaServer:1\r\nCONTENT-LENGTH: 0\r\n\r\n'
	return MS_NOTIFY_ALIVE

def ms_nofity_byebye(nt, usn):
	# MS_NOTIFY_BYEBYE is use to infrom other servers that we are leaving the network
	MS_NOTIFY_BYEBYE = 'NOTIFY * HTTP/1.1\r\nHOST: %s:%d\r\nNT:%s\nNTS:%s\nUSN:%s\nBOOTID.UPNP.ORG:%d\r\nCONFIGID.UPNP.ORG:%d\r\n\r\n' % (ssdpAddr, ssdpPort, nt, 'ssdp:byebye', usn, int(paramDict['bootId']), int(paramDict['configId']))
	return MS_NOTIFY_BYEBYE

def ms_search():
	# MS_SEARCH is used to inform other DTT2IP / SAT>IP servers that the DEVICE ID that they want to use belongs to us. Used in the DEVICE ID negotiation
	MS_SEARCH = 'M-SEARCH * HTTP/1.1\r\nHOST:%s:%d\r\nMAN:"ssdp-discover"ST:%s\nUSER-AGENT:%s\nDEVICEID.SES.COM:%d' % (serverIP, ssdpPort, st, paramDict['server'], int(paramDict['deviceId']))
	return MS_SEARCH

def callServerReactor():
	global SSDP_TERMINATE
	# global fLog

	# Open a multicast socket
	# fLog.write('Info: Discovery server started\n')

	ssdpMulticastSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	ssdpMulticastSocket.bind((ssdpAddr, ssdpPort))

	group = socket.inet_aton(ssdpAddr)
	mreq = struct.pack('4sL', group, socket.INADDR_ANY)
	ssdpMulticastSocket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
	ssdpMulticastSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	
	# While look until script is terminated
	while (not SSDP_TERMINATE):
		ssdpUnicastSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		# ssdpUnicastSocket.bind((serverIP, ssdpPort))
		ssdpUnicastSocket.settimeout(5.0)

		# Wait to receive multicast messages either from client or from new servers that have joined the network
		datagram, address = ssdpMulticastSocket.recvfrom(1024)
		datagram_array = datagram.rsplit('\r\n')
		try: 
			first_line = datagram_array[0]
			# See if the multicast messages are from the clients/servers
			matchMSearch = re.search(r'M-SEARCH',first_line)
			# matchNotify = re.search(r'NOTIFY',first_line)

			if matchMSearch:
				print 'Recv: M-SEARCH'
				for i in range(6):
					ssdpUnicastSocket.sendto(ms_ok(i), (address[0], address[1]))
				ssdpUnicastSocket.close()
		except:
			# fLog.write("Info: Something went wrong\n")
			print 'Info: Something went wrong\n'
	ssdpMulticastSocket.close()

def callClientReactor():
	global SSDP_TERMINATE
	global deviceIdOk

	ssdpUnicastSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	ssdpUnicastSocket.bind((serverIP, ssdpPort))
	ssdpUnicastSocket.settimeout(5.0)

	# While look until script is terminated
	while (not SSDP_TERMINATE):
		print 'Info: Device ID negotiation done. Sleep and send NOTIFY later\n'
		time.sleep(random.randint(0, int(90)/2))

		for i in range(3):
			ssdpUnicastSocket.sendto(ms_notify_alive(i), (ssdpAddr,ssdpPort))
			print 'Info: MS_NOTIFY_ALIVE\n'

	ssdpUnicastSocket.close()

def discoveryServer():
	global deviceIdOk

	# DEVICE ID negotiation thread ( server <---> server communications )
	t1 = threading.Thread(target=callClientReactor)
	t1.daemon = True
	t1.start()
	# Wait for DEVICE negotiation to finish then start the Discovery protocol in order for the clients to connect to
	# while not deviceIdOk:
	# 	time.sleep(1)
	# DISCOVERY thread for the client applications ( server <---> client communications)
	t2 = threading.Thread(target=callServerReactor)
	t2.daemon = True
	t2.start()

	# Keep threads alive until KeyboardInterrupt
	try:
		while t1.is_alive() and t2.is_alive():
			t1.join(timeout=1.0)
			t2.join(timeout=1.0)
	except (KeyboardInterrupt, SystemExit):
		# fLog.close()
		SSDP_TERMINATE = 1

 
if __name__ == "__main__":
	discoveryServer()


