#!/usr/bin/python
 
# Discovery state machine
# SSDP protocol
 
import sys, re, os, random
import threading, socket, struct, time, calendar
from netInterfaceStatus import getServerIP

from datetime import date, datetime

global SSDP_TERMINATE
global deviceId, deviceIdOk
global ssdpAddr, ssdpPort, httpPort, serverIP
global cacheControl, location, nts_alive, nts_byebye
global server, uuid, upnp, urn, NT, USN, bootId, configId, deviceId, st 

SSDP_TERMINATE = 0

deviceIdOk = False

ssdpAddr = '239.255.255.250'
ssdpPort = 1900
httpPort = 80
serverIP = getServerIP()

# To Do  make configuration file
cacheControl = 1800
location = '7f764937-d0d7-11e1-9b23-00059e9651fd.xml'
nts_alive = 'ssdp:alive'
nts_beybey = 'ssdp:byebye'
server = 'CW/1.0 UPnP/1.1 CWUpnp/1.1'
uuid = '7f764937-d0d7-11e1-9b23-00059e9651fd'
upnp = 'rootdevice'
urn = 'ses-com:device:SatIPServer:1'

nt1 = 'upnp:' + upnp
nt2 = 'uuid:' + uuid
nt3 = 'urn:' + urn
NT = [nt1, nt2, nt3]

usn1 = 'uuid:' + uuid + '::upnp:' + upnp
usn2 = 'uuid:' + uuid
usn3 = 'uuid:' + uuid + '::urn:' + urn
USN = [usn1, usn2, usn3]

bootId = 981
configId = 2212703
deviceId = 1
st = 'urn:' + urn
# To Do make configuration file

def ms_ok(toClient):
	myDate = date.today()
	currentTime = datetime.now().time()
	if myDate.day < 10:
		dateStr = calendar.day_name[myDate.weekday()] + ' ' + str(myDate.weekday()) + ' ' + calendar.month_name[myDate.month] + ' ' + str(myDate.year) + ' ' + currentTime.isoformat()[:-7] + ' ' + 'GMT'
	else:
		dateStr = calendar.day_name[myDate.weekday()] + ' 0' + str(myDate.weekday()) + ' ' + calendar.month_name[myDate.month] + ' ' + str(myDate.year) + ' ' + currentTime.isoformat()[:-7] + ' ' + 'GMT'
	if toClient:
		MS_OK = 'HTTP/1.1 200 OK\r\nCACHE-CONTROL:max-age=%d\r\nDATE:%s\nEXT:\r\nLOCATION:http://%s:%d/%s\r\nSERVER:%s\nST:%s\nUSN:%s\nBOOTID.UPNP.ORG:%d\r\nCONFIGID.UPNP.ORG:%d\n\r\n' % (cacheControl, dateStr, serverIP, httpPort, location, server, st, USN[2], bootId, configId)
	else:
		MS_OK = 'HTTP/1.1 200 OK\r\nCACHE-CONTROL:max-age=%d\r\nDATE:%s\nEXT:\r\nLOCATION:http://%s:%d/%s\r\nSERVER:%s\nST:%s\nUSN:%s\nBOOTID.UPNP.ORG:%d\r\nCONFIGID.UPNP.ORG:%d\r\nDEVICEID.SES.COM:%d\r\n\r\n' % (cacheControl, dateStr, serverIP, httpPort, location, server, st, USN[2], bootId, configId, deviceId)
	
	return MS_OK

def ms_notify_alive(nt, usn):	
	MS_NOTIFY_ALIVE = 'NOTIFY * HTTP/1.1\r\nHOST: %s:%d\r\nBOOTID.UPNP.ORG:%d\r\nCONFIGID.UPNP.ORG:%d\r\nCACHE-CONTROL: max-age=%d\r\nLOCATION:http://%s:%d/%s\r\nNT:%s\nNTS:%s\nSERVER:%s\nUSN:%s\nDEVICEID.SES.COM:%d\r\n\r\n' % (ssdpAddr, ssdpPort, bootId, configId, cacheControl, serverIP, httpPort, location, nt, nts_alive, server, usn, deviceId)
	return MS_NOTIFY_ALIVE

def ms_nofity_byebye(nt, usn):
	MS_NOTIFY_BYEBYE = 'NOTIFY * HTTP/1.1\r\nHOST: %s:%d\r\nNT:%s\nNTS:%s\nUSN:%s\nBOOTID.UPNP.ORG:%d\r\nCONFIGID.UPNP.ORG:%d\r\n\r\n' % (ssdpAddr, ssdpPort, nt, nts, usn, bootId, configId)
	return MS_NOTIFY_BYEBYE

def ms_search():
	MS_SEARCH = 'M-SEARCH * HTTP/1.1\r\nHOST:%s:%d\r\nMAN:"ssdp-discover"ST:%s\nUSER-AGENT:%s\nDEVICEID.SES.COM:%d' % (serverIP, ssdpPort, st, server, deviceId)
	return MS_SEARCH

def callServerReactor():
	global SSDP_TERMINATE

	print 'first thread : Server'
	ssdpMulticastSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	ssdpMulticastSocket.bind((ssdpAddr, ssdpPort))

	group = socket.inet_aton(ssdpAddr)
	mreq = struct.pack('4sL', group, socket.INADDR_ANY)
	ssdpMulticastSocket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
	ssdpMulticastSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	
	while (not SSDP_TERMINATE):
		datagram, address = ssdpMulticastSocket.recvfrom(1024)
		datagram_array = datagram.rsplit('\r\n')
		
		try: 
			first_line = datagram_array[0]

			matchMSearch = re.search(r'M-SEARCH',first_line)
			matchNotify = re.search(r'NOTIFY',first_line)

			if matchMSearch:
				match2 = re.search(r'ses-com',datagram)
				if match2:
					print 'ip', address[0], 'port', address[1]
					toClient = True
					ssdpMulticastSocket.sendto(ms_ok(toClient), (address[0], address[1]))

			if matchNotify:
				matchSES = re.search(r'DEVICEID.SES.COM:([\w]+)',datagram)
				if matchSES:
					if matchSES.group(1) == deviceId:
						ssdpMulticastSocket.sendto(ms_search(), (address[0], address[1]))
						print "MS_SEARCH"
		except:
			print "Something went wrong"

	ssdpMulticastSocket.close()

def callClientReactor():
	global SSDP_TERMINATE
	global deviceId, deviceIdOk

	print 'second thread : Client'
	oldDeviceId = deviceId
	ssdpUnicastSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	ssdpUnicastSocket.bind((serverIP, ssdpPort))
	ssdpUnicastSocket.settimeout(5.0)

	while (not SSDP_TERMINATE):
		while (not deviceIdOk):
			for i in range(3):
				ssdpUnicastSocket.sendto(ms_notify_alive(NT[i], USN[i]), (ssdpAddr, ssdpPort))
				print "MS_NOTIFY_ALIVE"
			try:
				oldDeviceId = deviceId	
				datagram, address = ssdpUnicastSocket.recvfrom(1024)
				datagram_array = datagram.rsplit('\r\n')

				try:
					first_line = datagram_array[0]
					matchMSearch = re.search(r'M-SEARCH',first_line)

					if matchMSearch:
						matchSES = re.search(r'DEVICEID.SES.COM:([\w]+)',datagram)
						if matchSES:
							if matchSES.group(1) == deviceId:
								toClient = False
								ssdpUnicastSocket.sendto(ms_ok(toClient), (address[0], address[1]))
								print "MS_OK"
								deviceId = deviceId + 1
								for i in range(3):
									ssdpUnicastSocket.sendto(ms_nofity_byebye(NT[i], USN[i]), (ssdpAddr, ssdpPort))
									print "MS_NOTIFY_BYEBYE"
				except:
					print 'Something went wrong'
			except:
				if oldDeviceId == deviceId:
					deviceIdOk = True

		print "Sleep and send NOTIFY later"
		time.sleep(random.randint(0, cacheControl/2))
		ssdpUnicastSocket.sendto(ms_notify_alive(NT[i], USN[i]), (ssdpAddr, ssdpPort))

	ssdpUnicastSocket.close()

def main():
	t1 = threading.Thread(target=callClientReactor)
	t1.daemon = True
	t1.start()

	while not deviceIdOk:
		a = 1
	
	# Wait for DEVICE negotiation to finish then start the Discovery protocol in order for the clients to connect to
	t2 = threading.Thread(target=callServerReactor)
	t2.daemon = True
	t2.start()

	try:
		while t1.is_alive() and t2.is_alive():
			a = 1
	except (KeyboardInterrupt, SystemExit):
		SSDP_TERMINATE = 1

 
if __name__ == "__main__":
	main()


