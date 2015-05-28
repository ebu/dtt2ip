#!/usr/bin/python
 
# Python program that can send out M-SEARCH messages using SSDP (in server
# mode), or listen for SSDP messages (in client mode).
 
import sys
from twisted.internet import reactor, task
from twisted.internet.protocol import DatagramProtocol
# from netInterfaceStatus import getNetworkInt
from netInterfaceStatus import getServerIP
import re
import os

ssdpAddr = '239.255.255.250'
ssdpPort = 1900

httpPort = 80

serverIP = getServerIP()

MSOK = 'HTTP/1.1 200 OK\r\nCACHE-CONTROL:max-age=1800\r\nDATE:Mon 03 Jan 2000 11:29:31 GMT\r\nEXT:\r\nLOCATION:http://%s:%d/desc.xml\r\nSERVER:CW/1.0 UPnP/1.1 CWUpnp/1.1\r\nST:urn:ses-com:device:SatIPServer:1\r\nUSN:uuip:7f764937-d0d7-11e1-9b23-00059e9651fd::urn:ses-com:device:SatIPServer:1\r\nBOOTID.UPNP.ORG:998\r\nCONFIGID.UPNP.ORG:2212703\r\nDEVICEID.SES.COM:0\r\n\r\n' % (serverIP, httpPort)


# SSDP_ADDR = '239.255.255.250'
# # SSDP_ADDR = '192.168.1.38'
# # SSDP_ADDR2 = '192.168.1.101'
# SSDP_PORT = 1900
# HTTP_PORT = 80
# SERVER_IP = getServerIP()
 
# MS = 'M-SEARCH * HTTP/1.1\r\nHOST: %s:%d\r\nMAN: "ssdp:discover"\r\nMX: 2\r\nST: ssdp:all\r\n\r\n' % (SSDP_ADDR, SSDP_PORT)
# NO =[]
# a = 'NOTIFY * HTTP/1.1\r\nHOST: %s:%d\r\nBOOTID.UPNP.ORG:981\r\nCONFIGID.UPNP.ORG:12555367\r\nCACHE-CONTROL: max-age=1800\r\nLOCATION:http://192.168.1.60/desc.xml\r\nNT:upnp:rootdevice\r\nNTS:ssdp:alive\r\nSERVER:CW/1.0 UPnP/1.1 CWUpnp/1.1\r\nUSN:uuip:7f764937-d0d7-11e1-9b23-00059e9651fd::upnp:rootdevice\r\nDEVICEID.SES.COM:0\r\n\r\n' % (SSDP_ADDR, SSDP_PORT)
# b = 'NOTIFY * HTTP/1.1\r\nHOST: %s:%d\r\nBOOTID.UPNP.ORG:981\r\nCONFIGID.UPNP.ORG:12555367\r\nCACHE-CONTROL: max-age=1800\r\nLOCATION:http://192.168.1.60/desc.xml\r\nNT:uuid:7f764937-d0d7-11e1-9b23-00059e9651fd\r\nNTS:ssdp:alive\r\nSERVER:CW/1.0 UPnP/1.1 CWUpnp/1.1\r\nUSN:uuip:7f764937-d0d7-11e1-9b23-00059e9651fd\r\nDEVICEID.SES.COM:0\r\n\r\n' % (SSDP_ADDR, SSDP_PORT)
# c = 'NOTIFY * HTTP/1.1\r\nHOST: %s:%d\r\nBOOTID.UPNP.ORG:981\r\nCONFIGID.UPNP.ORG:12555367\r\nCACHE-CONTROL: max-age=1800\r\nLOCATION:http://192.168.1.60/desc.xml\r\nNT:urn:ses-com:device:SatIPServer:1\r\nNTS:ssdp:alive\r\nSERVER:CW/1.0 UPnP/1.1 CWUpnp/1.1\r\nUSN:uuip:7f764937-d0d7-11e1-9b23-00059e9651fd::urn:ses-com:device:SatIPServer:1\r\nDEVICEID.SES.COM:0\r\n\r\n' % (SSDP_ADDR, SSDP_PORT)
# MSOK = 'HTTP/1.1 200 OK\r\nCACHE-CONTROL:max-age=1800\r\nDATE:Mon 03 Jan 2000 11:29:31 GMT\r\nEXT:\r\nLOCATION:http://%s:%d/desc.xml\r\nSERVER:CW/1.0 UPnP/1.1 CWUpnp/1.1\r\nST:urn:ses-com:device:SatIPServer:1\r\nUSN:uuip:7f764937-d0d7-11e1-9b23-00059e9651fd::urn:ses-com:device:SatIPServer:1\r\nBOOTID.UPNP.ORG:998\r\nCONFIGID.UPNP.ORG:2212703\r\nDEVICEID.SES.COM:0\r\n\r\n' % (SERVER_IP, HTTP_PORT)
# NO.append(a)
# NO.append(b)
# NO.append(c)
# counter = 0

class Base(DatagramProtocol):
	def datagramReceived(self, datagram, address):
		datagram_array = datagram.rsplit('\r\n')
		print "datagram_array", datagram_array
		# first_line = datagram.rsplit('\r\n')[0]

		try: 
			first_line = datagram_array[0]
			second_line = datagram_array[2]

			match = re.search(r'M-SEARCH',first_line)
			if match:
				match2 = re.search(r'ssdp:discover',datagram)
				if match2:
					print 'received M-SEARCH from SAT>IP clients'
					print 'sending replay'
					print 'ip', address[0], 'port', address[1]
					self.ssdp.write(MSOK, (address[0], address[1]))

					# Run server RTSP
					# os.spawnl(os.P_DETACH, 'python Server.py 8005')
					# os.system('python Server.py 8005')
					# os.system('python ClientLauncher.py 127.0.0.1 8005 127.0.0.1 12001 video.ts')
		except:
			print 'Something went wrong'

	def stop(self):
		pass
 
class Server(Base):
	def __init__(self, iface, ssdpPort, ssdpAddr):
		self.iface = iface
		self.ssdp = reactor.listenMulticast(ssdpPort, self, listenMultiple=True)
		self.ssdp.setLoopbackMode(1)
		self.ssdp.joinGroup(ssdpAddr, interface=iface)
 
	def stop(self):
		self.ssdp.leaveGroup(ssdpPAddr, interface=self.iface)
		self.ssdp.stopListening()
 
def main():

	obj = Server(serverIP, ssdpPort, ssdpAddr)
	reactor.addSystemEventTrigger('before', 'shutdown', obj.stop)
 
if __name__ == "__main__":
	#testing the getNetworkInt() function
	# a = getNetworkInt()
	# print a
	# if len(sys.argv) != 3:
	# 	print "Usage: %s <server> <IP of interface>" % (sys.argv[0], )
	# 	sys.exit(1)
	# mode, iface = sys.argv[1:]
	reactor.callWhenRunning(main)
	reactor.run()


