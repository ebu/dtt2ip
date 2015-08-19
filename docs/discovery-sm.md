# Discovery state machine

During the discovery phase SAT>IP servers advertise their presence to other SAT>IP servers and clients. When joining a network, SAT>IP clients search the network for available SAT>IP servers.
Discovery in SAT>IP relies on the Simple Service Description Protocol (SSDP) [11] as specified in the UPnP Device Architecture 1.1 [1]. 
As a minimum: 
		-  a SAT>IP server is a UPnP Device and a UPnP Control Point,  
		-  a SAT>IP client is a UPnP Control Point.  

SAT>IP servers joining a network multicast three different NOTIFY ssdp:alive messages to the SSDP address 239.255.255.250 port 1900. This is a requirement for UPnP root devices according to the UPnP Device Architecture 1.1 [1]. 

A SAT>IP server present on the network has to re-announce itself on a regular basis as described under CACHE-CONTROL above. 
A SAT>IP server leaving the network needs to signal its departure by sending three different NOTIFY messages with the NTS value ssdp:byebye. 
Please note that the ssdp:byebye messages should not include the CACHE-CONTROL, LOCATION, SERVER and DEVICEID.SES.COM headers. An example of such ssdp:byebye messages is shown in Section 3.3.3. 
A SAT>IP server changing the network e.g. when passing from an Auto-IP network to a network with a DHCP assigned address shall signal its departure from one network by sending three NOTIFY messages with the NTS value ssdp:byebye on that network and shall announce its presence on the new network by sending three NOTIFY ssdp:alive messages. 
SAT>IP clients (being at a minimum only UPnP Control Points) do not announce their presence. For this reason, a client leaving the network is not detectable at this level. The SAT>IP protocol however implements RTSP and IGMP which permit to detect the presence or absence of a client (RTSP session timeout, IGMP membership queries). 
