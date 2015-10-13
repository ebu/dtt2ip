# Sat>IP overview

SAT>IP is a protocol standardized by ETSI, and was developed by SES S.A, British Sky Broadcasting Ltd and Craftwork ApS on the 8th of January 2015, and the version we have used is 1.2.2. In this chapter will cover the importance of this standard in our project, together with a small description.
In order to have a standardized communication protocol between clients and server, we have chose SAT>IP protocol, which provided satellite broadcasting to IP through the local Wi-Fi networks. This gives the advantage of leveraging preexisting client applications, and completes the offer of live broadcasting  (DVB-S and DVB-T).

SAT>IP specifies a communication protocol. SAT>IP is not a device specification. The SAT>IP protocol may be applied in different devices. Industry is left to come up with new and innovative devices using the SAT>IP protocol. 
The SAT>IP protocol distinguishes between SAT>IP clients and SAT>IP servers. Actual devices may be clients or servers or both depending on their feature set. 

![alt text][figure1]
[figure1]:https://github.com/ebu/dtt2ip/blob/master/docs/images/figure1.png

SAT>IP Clients 
SAT>IP clients provide the possibility of selecting and receiving live television programs. SAT>IP clients may be – DVB compliant Set-Top-Boxes (STBs) with an IP interface or – Software applications running on programmable hardware such as Tablets, PCs, Smartphones, Connected Televisions, NAS, Routers, etc. 
SAT>IP Servers 
SAT>IP servers will answer requests from SAT>IP clients and forward live television programs to these clients. Servers may take various forms from simple in-home IP Adapters / Multiswitches, Master STBs to ultimately IP LNBs and large MDU headends covering whole buildings or cities. 

SAT>IP Concept
Unlike in today’s satellite distribution schemes, the SAT>IP architecture allows the reception of satellite television programs also on devices which do not have a satellite tuner directly built-in. Satellite tuners and demodulators are moved or “remoted” into SAT>IP server devices. Clients control SAT>IP servers via the SAT>IP protocol. SAT>IP is a remote tuner control protocol which provides the possibility of remotely controlling tuning devices. 
This means that the reception of satellite delivered programming can be dealt with by clients purely in software, provided a SAT>IP server is available on a network. Satellite programs become available on devices, which would never be capable of, supporting satellite TV otherwise e.g. Tablets. 
From the distribution point of view, satellite distribution becomes physical layer agnostic and satellite services can be forwarded over all the latest types of IP wired or wireless technologies such as Powerline (PLC), Wireless LANs, Optical Fiber Distribution, etc. 
The SAT>IP protocol makes use of: 
		-  UPnP for Addressing, Discovery and Description,  
		-  RTSP or HTTP for Control,  
		-  RTP or HTTP for Media Transport.  

SAT>IP uses a subset of the UPnP/DLNA architecture and protocols [1] [2] and SAT>IP devices can be extended to also become DLNA devices. As an example a SAT>IP client could access live media streams through the SAT>IP protocol and access recorded media streams through DLNA. 

![alt text][figure2]
[figure2]:https://github.com/ebu/dtt2ip/blob/master/docs/images/figure2.png

SAT>IP devices successively go through the following phases: Addressing, Discovery, Description, Control and finally Media Transport. 
[Back to Table of content](README.md)
