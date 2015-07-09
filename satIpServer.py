#!/usr/bin/python
 
# Discovery state machine
# SSDP protocol
 
import sys
from twisted.internet import reactor, task
from twisted.internet.protocol import DatagramProtocol
# from netInterfaceStatus import getNetworkInt
from netInterfaceStatus import getServerIP
import re
import os
from threading import Timer

global t
global datagramNotify
global deviceIdOk
global deviceID

deviceID = 1
datagramNotify = ''
deviceIdOk = False

ssdpAddr = '239.255.255.250'
ssdpPort = 1900

httpPort = 80

serverIP = getServerIP()

MS_OK = 'HTTP/1.1 200 OK\r\nCACHE-CONTROL:max-age=1800\r\nDATE:Mon 03 Jan 2000 11:29:31 GMT\r\nEXT:\r\nLOCATION:http://%s:%d/desc.xml\r\nSERVER:CW/1.0 UPnP/1.1 CWUpnp/1.1\r\nST:urn:ses-com:device:SatIPServer:1\r\nUSN:uuip:7f764937-d0d7-11e1-9b23-00059e9651fd::urn:ses-com:device:SatIPServer:1\r\nBOOTID.UPNP.ORG:998\r\nCONFIGID.UPNP.ORG:2212703\r\nDEVICEID.SES.COM:%d\r\n\r\n' % (serverIP, httpPort, deviceID)

MS_NOTIFY_ALIVE = 'NOTIFY * HTTP/1.1\r\nHOST: %s:%d\r\nBOOTID.UPNP.ORG:981\r\nCONFIGID.UPNP.ORG:12555367\r\nCACHE-CONTROL: max-age=1800\r\nLOCATION:http://%s/desc.xml\r\nNT:upnp:rootdevice\r\nNTS:ssdp:alive\r\nSERVER:CW/1.0 UPnP/1.1 CWUpnp/1.1\r\nUSN:uuip:7f764937-d0d7-11e1-9b23-00059e9651fd::upnp:rootdevice\r\nDEVICEID.SES.COM:%d\r\n\r\n' % (ssdpAddr, ssdpPort, serverIP, deviceID)

MS_NOTIFY_BYEBYE = 'NOTIFY * HTTP/1.1\r\nHOST: %s:%d\r\nNT:upnp:rootdevice\r\nNTS:ssdp:byebye\r\nUSN:uuip:7f764937-d0d7-11e1-9b23-00059e9651fd::upnp:rootdevice\r\nBOOTID.UPNP.ORG:981\r\nCONFIGID.UPNP.ORG:12555367\r\n\r\n' % (ssdpAddr, ssdpPort)

MS_SEARCH = 'M-SEARCH * HTTP/1.1\r\nHOST:%s:%d\r\nMAN:"ssdp-discover"ST:urn:ses-com:device:SatIPServer:1\r\nUSER-AGENT:CW/1.0 UPnP/1.1 CWUpnp/1.1\r\nDEVICEID.SES.COM:%d' % (serverIP, ssdpPort, deviceID)

def timeout():
	deviceIdOk = True


class Base(DatagramProtocol):

	def sendNOTIFY(self, msNOTIFY):
		global t
		for i in range(3):
			self.ssdp.write(msNOTIFY, (ssdpAddr, ssdpPort))
			print "msNOTIFY", msNOTIFY
		if msNOTIFY == MS_NOTIFY_ALIVE:
			t.start()

	def datagramReceived(self, datagram, address):
		global datagramNotify
		global deviceIdOk
		global deviceID

		datagram_array = datagram.rsplit('\r\n')
		datagramNotify = datagram_array
		# print "datagram_array", datagram_array
		# first_line = datagram.rsplit('\r\n')[0]
		
		try: 
			first_line = datagram_array[0]
			# second_line = datagram_array[2]

			matchNotify = re.search(r'NOTIFY',first_line)
			matchMSearch = re.search(r'M-SEARCH',first_line)

			if matchNotify:
				matchSES = re.search(r'DEVICEID.SES.COM:([\w]+)',datagram)
				if matchSES:
					if matchSES.group(1) == deviceID:
						self.ssdp.write(MS_OK, (address[0], address[1]))
						print "MS_OK"



			if matchMSearch:
				match2 = re.search(r'ssdp:discover',datagram)
				match3 = re.search(r'DEVICEID.SES.COM',datagram)
				
				if match3 and not deviceIdOk:
					t.cancel()
					self.ssdp.write(MS_OK, (address[0], address[1]))
					self.sendNOTIFY(MS_NOTIFY_BYEBYE)
					deviceID = deviceID + 1
					self.sendNOTIFY(MS_NOTIFY_ALIVE)

				elif match2:
					print 'ip', address[0], 'port', address[1]
					self.ssdp.write(MS_OK, (address[0], address[1]))

		except:
			print 'Something went wrong'

	def stop(self):
		pass
 
class Server(Base):

	def __init__(self, iface, ssdpPort, ssdpAddr):
		global t
		t = Timer(5, timeout)

		self.iface = iface
		self.ssdp = reactor.listenMulticast(ssdpPort, self, listenMultiple=True)
		self.ssdp.setLoopbackMode(1)
		self.ssdp.joinGroup(ssdpAddr, interface=iface)

		self.ssdpClient = reactor.listenUDP(1900, self, interface=self.iface)
		self.sendNOTIFY(MS_NOTIFY_ALIVE)

 
	def stop(self):
		self.ssdp.leaveGroup(ssdpAddr, interface=self.iface)
		self.ssdp.stopListening()
 
def main():

	obj = Server(serverIP, ssdpPort, ssdpAddr)
	reactor.addSystemEventTrigger('before', 'shutdown', obj.stop)
 
if __name__ == "__main__":
	reactor.callWhenRunning(main)
	reactor.run()


