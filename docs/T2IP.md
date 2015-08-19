#T2IP server implementation

The first implementation was deployed on a Raspberry Pi. The Raspberry Pi it is called DTT>IP server in the following figures. Using a yaggi terrestrial antenna, we have captured the broadcast signal, through a USB tuner plugged in our Raspberry Pi. Then for the network connection to the Wi-Fi, we have used a basic Ethernet cable, as we can see in the Figure 4.

![alt text][figure1]
[figure1]:https://github.com/ebu/dtt2ip/blob/documentation/docs/images/figure4.png

Underneath the DTT>IP server, we have a Linux environment (Rapian), on which we have installed the firmware to detect the USB tuner, the DVBlast open source software, and the developed application described in chapters 4 and 5. This will allow for our server to be detected by any SAT>IP software client, and will allow a parallel coexistence with other SAT>IP servers. 

![alt text][figure2]
[figure2]:https://github.com/ebu/dtt2ip/blob/documentation/docs/images/figure5.png

The application being developed in python and because we have used a Linux distribution, we could deploy this on any hardware that could have Debian installed for example.  Bearing this idea in mind, and having a Synology NAS, we went out and tested it. And with no surprise this worked from the beginning, like we anticipated. 
