# T2IP server implementation
### Index
1. [T2IP server implementation](#t2ip-server-diagram)
2. [Software code explanations](#software-code-explanations)

### T2IP server diagram

The first implementation was deployed on a Raspberry Pi. The Raspberry Pi it is called DTT>IP server in the following figures. Using a yaggi terrestrial antenna, we have captured the broadcast signal, through a USB tuner plugged in our Raspberry Pi. Then for the network connection to the Wi-Fi, we have used a basic Ethernet cable, as we can see in the Figure 4.

![alt text][figure1]
[figure1]:https://github.com/ebu/dtt2ip/blob/documentation/docs/images/figure4.png

Underneath the DTT>IP server, we have a Linux environment (Rapian), on which we have installed the firmware to detect the USB tuner, the DVBlast open source software, and the developed application described in chapters 4 and 5. This will allow for our server to be detected by any SAT>IP software client, and will allow a parallel coexistence with other SAT>IP servers. 

![alt text][figure2]
[figure2]:https://github.com/ebu/dtt2ip/blob/documentation/docs/images/figure5.png

The application being developed in python and because we have used a Linux distribution, we could deploy this on any hardware that could have Debian installed for example.  Bearing this idea in mind, and having a Synology NAS, we went out and tested it. And with no surprise this worked from the beginning, like we anticipated. 

### Software code explanations

The software code directory is as follows:
```
dtt2IP/
├── docs
├── test
├── t2IP
│   ├── __init__.py
│   ├── __main__.py
│   ├── t2IP.py
│   ├── discoveryServer.py
│   ├── rtspServer.py
│   ├── rtspServerWorker.py
│   ├── scanning.py
│   ├── resources.py
│   ├── netInterfaceStatus.py
│   ├── conf/
│   │   ├── discoveryServer.conf
│   │   ├── rtspServer.conf
│   ├── dvb-t/
│   │   ├── allFrequencies.txt
│   └── logs/
│   │   ├── discoveryServer.log
│   │   ├── rtspServer.log
│   │   ├── rtspServerWorker.log
│   │   ├── scanning.log
│   │   ├── resources.log
│   │   ├── t2IP.log
├── t2IP-runner.py
├── LICENSE
├── MANIFEST.in
├── README.rst
└── setup.py
```


The “t2IP.py” file is the main script from your application. In this we will run 3 threads, the first is the discovery server, the second runs the rtsp server, and the third on is to used to scan the broadcast available channels. The code is Appendix A.

The “discoveryServer.py” file will create an SSDP server and client. The SSDP client will serve to communicate with other servers and negotiate a unique and unused device ID. Every server must have a unique device ID in order to distinguish between them, from a client perspective. The SSDP server will announce its presence on the network to other SSDP clients. Every time a server joins a network, this will send 3xNOTIFY(ssdp: alive) multicast messages to the IP address: “239.255.255.255”.
If it does receive a message from other servers on the same network, saying that device ID used it is not available, before a timeout of 6 seconds, then discovery server is well setup and will continue to send at random time 3xNOTIFY messages, at least 2 times between the interval of expiration. However, if it does receive a message from the other servers before the timeout, our server will send back an acknowledgment, followed by 3xNOTIFY(ssdp: bye:bye) messages, and will restart the whole process from the beginning with an incremented device ID. This code is Appendix B.

The “rtspServer.py” file will create the RTSP server, which will allow clients to connect to the RTSP state machine, and make requests/teardowns for the stream that they want to watch. Every client that connects will be an instance of the class rtspServerWorker, which will specify the resources need. This code is Appendix C.

The “rtspServerWorker.py” file will handle the rtspServerWorker class mentioned in the “rtspServer.py”. In this class every instance (client) will be an entry in the client’s dictionary (clientDict) that will specify for all the parameters of the stream that they are requesting. Another important dictionaries that is used and updated all the time are: frequency dictionary (freqDict), this will map the frequencies with the adapters configured with those respective frequencies; frontends dictionary (frontEndsDict), which maps the adapter to the owners, the frequencies, and the number of owners. This code is Appendix D.

The  “scanning.py” file will handle the scanning of the frequencies available. It has an interesting algorithm for keeping updated the available multiplexes, and will handle the “bad behavior” from the USB tuners that may skip sometimes some frequencies. This is also update the list of channels and parameters used by the rtspServerWorker class. This code is Appendix E.

The “resources.py” file will handle the USB tuners that are plugged into the device. These are also updated in real time, meaning that if new USB tuners become available, these are in real time detected and used at a new request for stream. This code is Appendix F.

The “netInterfaceStatus.py” file will handle the IP of the connected interfaces, so that we do not need to specify any IP of our t2IP server. However this requires an additional python package (netifaces) that needs to be installed prior our application. This code is Appendix G.


