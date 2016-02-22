#!/usr/bin/python

import netifaces
# import Error


def getServerIP():
	ipAddrServer = '127.0.0.1'
	ipAddrArray = getNetworkInt()
	for ipAddr in ipAddrArray:
		if ipAddr["name"] != "lo" and ipAddr["status"] == "up" and ipAddr["ip"][:3] != "169":
			ipAddrServer = ipAddr["ip"]

	# print "Info netInterfaceStatus: ipAddrServer = " + ipAddrServer + '\n'
	return ipAddrServer

def getNetworkInt():
	'''
		getNetworkInt() function that checks the all network interfaces on the machine.
		This will return array vector with all the available interfaces.
		If not available interface (all interfaces are down) will return,
		The last interface found with loop ip address (127.0.0.1) with status "down".

		e.g. :

		if ok : 
			[{'status': 'up', 'ip': '10.50.219.250', 'mac': '3c:15:c2:e2:97:a0', 'name': 'en0'}]
		else :
			[{'status': 'down', 'ip': '127.0.0.1', 'mac': '42:01:38:ad:79:a2', 'name': 'awdl0'}] 
	'''
	networkServer = []
	netInts = netifaces.interfaces()
	for netInt in netInts:
		netIntDesc = netifaces.ifaddresses(netInt)
		# print "netIntName", netInt
		networkServerDic = {}

		#Description for each number
		# better use the netifaces.AF_LINK instead of 18, it may change over time
		# 18 --- is the AF_LINK (which means the link layer interface, e.g. Ethernet)
		#  2 --- is the AF_INET (normal internet address)
		# 30 --- is the AF_INET6 (IPv6)
		try:
			networkServerDic["name"] = netInt
			networkServerDic["mac"] = netIntDesc[netifaces.AF_LINK][0]["addr"]
			networkServerDic["ip"] = netIntDesc[netifaces.AF_INET][0]["addr"]
			networkServerDic["status"] = "up" 
			networkServer.append(networkServerDic)
		except Exception as err:
			if int(str(err)) == netifaces.AF_INET:
				networkServerDic["name"] = netInt
				networkServerDic["mac"] = netIntDesc[netifaces.AF_LINK][0]["addr"]
				networkServerDic["ip"] = "127.0.0.1"
				networkServerDic["status"] = "down"
	
	if networkServer == []:
		networkServer.append(networkServerDic)

	# print networkServer
	return networkServer

if __name__ == '__main__':
	getNetworkInt()
