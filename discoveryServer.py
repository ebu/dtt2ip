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


paramDict = {}
f = open("conf/discoveryServer.config", 'r')
lines = f.readlines()
for i in range(5, len(lines)):
	line = lines[i]
	lineArray = line.split('=')
	lineArray[0] = lineArray[0][:-1]
	lineArray[1] = lineArray[1][1:-1]
	paramDict[lineArray[0]] = lineArray[1]
f.close()
SSDP_TERMINATE = 0

deviceIdOk = False

ssdpAddr = '239.255.255.250'
ssdpPort = 1900

serverIP = getServerIP()
# Make sure that rtspServer.log file is clean
fLog = open('logs/discoveryServer.log', 'w')
fLog.write("Info discoveryServer: ipAddrServer = " + serverIP + '\n')

nt1 = 'upnp:' + paramDict['upnp']
nt2 = 'uuid:' + paramDict['uuid']
nt3 = 'urn:' + paramDict['urn']
NT = [nt1, nt2, nt3]

usn1 = 'uuid:' + paramDict['uuid'] + '::upnp:' + paramDict['upnp']
usn2 = 'uuid:' + paramDict['uuid']
usn3 = 'uuid:' + paramDict['uuid'] + '::urn:' + paramDict['urn']
USN = [usn1, usn2, usn3]

# bootId = 981
# configId = 2212703
# deviceId = 1
st = 'urn:' + paramDict['urn']
# To Do make configuration file

def ms_ok(toClient):
	# MS_OK message is used to inform the client about the presents of the DTT2IP / SAT>IP server on the network
	# or to inform the other DTT2IP / SAT>IP servers that M-SEARCH message has been correctly received
	myDate = date.today()
	currentTime = datetime.now().time()
	if myDate.day < 10:
		dateStr = calendar.day_name[myDate.weekday()] + ' ' + str(myDate.weekday()) + ' ' + calendar.month_name[myDate.month] + ' ' + str(myDate.year) + ' ' + currentTime.isoformat()[:-7] + ' ' + 'GMT'
	else:
		dateStr = calendar.day_name[myDate.weekday()] + ' 0' + str(myDate.weekday()) + ' ' + calendar.month_name[myDate.month] + ' ' + str(myDate.year) + ' ' + currentTime.isoformat()[:-7] + ' ' + 'GMT'
	if toClient:
		MS_OK = 'HTTP/1.1 200 OK\r\nCACHE-CONTROL:max-age=%d\r\nDATE:%s\nEXT:\r\nLOCATION:http://%s:%d/%s\r\nSERVER:%s\nST:%s\nUSN:%s\nBOOTID.UPNP.ORG:%d\r\nCONFIGID.UPNP.ORG:%d\n\r\n' % (int(paramDict['cacheControl']), dateStr, serverIP, int(paramDict['httpPort']), paramDict['location'], paramDict['server'], st, USN[2], int(paramDict['bootId']), int(paramDict['configId']))
	else:
		MS_OK = 'HTTP/1.1 200 OK\r\nCACHE-CONTROL:max-age=%d\r\nDATE:%s\nEXT:\r\nLOCATION:http://%s:%d/%s\r\nSERVER:%s\nST:%s\nUSN:%s\nBOOTID.UPNP.ORG:%d\r\nCONFIGID.UPNP.ORG:%d\r\nDEVICEID.SES.COM:%d\r\n\r\n' % (int(paramDict['cacheControl']), dateStr, serverIP, int(paramDict['httpPort']), paramDict['location'], paramDict['server'], st, USN[2], int(paramDict['bootId']), int(paramDict['configId']), int(paramDict['deviceId']))
	
	return MS_OK

def ms_notify_alive(nt, usn):	
	# MS_NOTIFY_ALIVE is use to inform other DTT2IP / SAT>IP servers about our presents in the network. Used in the DEVICE ID negotiation
	MS_NOTIFY_ALIVE = 'NOTIFY * HTTP/1.1\r\nHOST: %s:%d\r\nBOOTID.UPNP.ORG:%d\r\nCONFIGID.UPNP.ORG:%d\r\nCACHE-CONTROL: max-age=%d\r\nLOCATION:http://%s:%d/%s\r\nNT:%s\nNTS:%s\nSERVER:%s\nUSN:%s\nDEVICEID.SES.COM:%d\r\n\r\n' % (ssdpAddr, ssdpPort, int(paramDict['bootId']), int(paramDict['configId']), int(paramDict['cacheControl']), serverIP, int(paramDict['httpPort']), paramDict['location'], nt, 'ssdp:alive', paramDict['server'], usn, int(paramDict['deviceId']))
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
	global fLog

	# Open a multicast socket
	fLog.write('Info: Discovery server started\n')

	ssdpMulticastSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	ssdpMulticastSocket.bind((ssdpAddr, ssdpPort))

	group = socket.inet_aton(ssdpAddr)
	mreq = struct.pack('4sL', group, socket.INADDR_ANY)
	ssdpMulticastSocket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
	ssdpMulticastSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	
	# While look until script is terminated
	while (not SSDP_TERMINATE):
		# Wait to receive multicast messages either from client or from new servers that have joined the network
		datagram, address = ssdpMulticastSocket.recvfrom(1024)
		datagram_array = datagram.rsplit('\r\n')
		
		try: 
			first_line = datagram_array[0]
			# See if the multicast messages are from the clients/servers
			matchMSearch = re.search(r'M-SEARCH',first_line)
			matchNotify = re.search(r'NOTIFY',first_line)

			if matchMSearch:
				# If M-SEARCH message from client, then process it and respond to it with a unicast message
				match2 = re.search(r'ses-com',datagram)
				if match2:
					# fLog.write("Info: client = ip " + address[0] + ", port " + address[1] + "\n")
					fLog.write("Info: client \n")
					toClient = True
					ssdpMulticastSocket.sendto(ms_ok(toClient), (address[0], address[1]))

			if matchNotify:
				# If NOTIFY message from server, then process it and see it is another DTT2IP / SAT>IP server
				matchSES = re.search(r'DEVICEID.SES.COM:([\w]+)',datagram)
				if matchSES:
					# If new DTT2IP / SAT>IP server that has join the network then respond to it with a unicast message
					# informing it that DEVICE ID is ours, else if this is an old DTT2IP / SAT>IP server do not do anything
					if int(matchSES.group(1)) == int(paramDict['deviceId']):
						ssdpMulticastSocket.sendto(ms_search(), (address[0], address[1]))
						fLog.write("Info: MS_SEARCH\n")
		except:
			fLog.write("Info: Something went wrong\n")
	ssdpMulticastSocket.close()

def callClientReactor():
	global SSDP_TERMINATE
	global deviceIdOk
	global fLog

	# Open a unicast socket
	fLog.write('Info: Device ID negotion started\n')

	ssdpUnicastSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	ssdpUnicastSocket.bind((serverIP, ssdpPort))
	ssdpUnicastSocket.settimeout(5.0)

	# While look until script is terminated
	while (not SSDP_TERMINATE):
		# DEVICE ID negotiation loop, escape only when we have valid DEVICE ID
		while (not deviceIdOk):
			# Send the first 3 SSDP NOTIFY messages
			for i in range(3):
				paramDict['bootId'] = int(paramDict['bootId']) + 1
				ssdpUnicastSocket.sendto(ms_notify_alive(NT[i], USN[i]), (ssdpAddr, ssdpPort))
				fLog.write("Info: MS_NOTIFY_ALIVE\n")
			try:
				# See if DEVICE ID is free, by waiting for a message or a timeout of 5 seconds
				datagram, address = ssdpUnicastSocket.recvfrom(1024)
				datagram_array = datagram.rsplit('\r\n')

				try:
					# Process the message received
					first_line = datagram_array[0]
					matchMSearch = re.search(r'M-SEARCH',first_line)

					if matchMSearch:
						# See if somebody else is using this ID
						matchSES = re.search(r'DEVICEID.SES.COM:([\w]+)',datagram)
						if matchSES:
							if int(matchSES.group(1)) == int(paramDict['deviceId']):
								# This DEVICE ID is used an we have to annouce that we are letting it go
								# by sending a MS_OK message to the other server (i.e toClient = False)
								# and to the hole network MS_NOTIFY_BYEBYE mesasge. 
								toClient = False
								ssdpUnicastSocket.sendto(ms_ok(toClient), (address[0], address[1]))
								fLog.write("Info: MS_OK\n")

								for i in range(3):
									ssdpUnicastSocket.sendto(ms_nofity_byebye(NT[i], USN[i]), (ssdpAddr, ssdpPort))
									fLog.write("Info: MS_NOTIFY_BYEBYE\n")
								# We have to increase the DEVICE ID	
								paramDict['deviceId'] = int(paramDict['deviceId']) + 1
				except:
					fLog.write('Info: Something went wrong\n')

			except:
				# Change deviceIdOk to True only when we timeout (5.0 seconds)
				fLog.write("Info: DEVICE ID\n")
				deviceIdOk = True
		# We have obtain out valid DEVICE ID, we have to maintain it valid on the network by sending 
		# at pseudo random periods 3 MS_NOTIFY_ALIVE messages. The pseudo random interval is between [0, cacheControl/2].
		# This guarantees that announcement set is repeated at least twice before it expires.
		fLog.write("Info: Device ID negotiation done. Sleep and send NOTIFY later\n")
		time.sleep(random.randint(0, int(paramDict['cacheControl'])/2))

		for i in range(3):
			paramDict['bootId'] = int(paramDict['bootId']) + 1
			ssdpUnicastSocket.sendto(ms_notify_alive(NT[i], USN[i]), (ssdpAddr, ssdpPort))
			fLog.write("Info: MS_NOTIFY_ALIVE\n")
	ssdpUnicastSocket.close()

def discoveryServer():
	global fLog
	global deviceIdOk

	# DEVICE ID negotiation thread ( server <---> server communications )
	t1 = threading.Thread(target=callClientReactor)
	t1.daemon = True
	t1.start()
	# Wait for DEVICE negotiation to finish then start the Discovery protocol in order for the clients to connect to
	while not deviceIdOk:
		time.sleep(1)
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
		fLog.close()
		SSDP_TERMINATE = 1

 
if __name__ == "__main__":
	discoveryServer()


