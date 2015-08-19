# Results and utilizations

### Index
1. [Raspberry Pi installation](#raspberrypi)
2. [Synology installation](#synology-nas)
3. [Synology installation easy[(#synology-nas-easy)

We have implemented the application to run on Raspberry Pi and Synology NAS with good results. The real-time scanning of the available frequencies was managed for multiple users, as well as tuning to different channels at the same time. The image quality was depending most of the time on the received RF signal, occupying only 4Mbps of the bandwidth. From our observations the multicasting one channel to the network was possible, however with poor playback quality, this problem being related to the concept of multicast. In order for every connected client in the network receive the multicast packets; the channel must have a low transmission rate., which does not satisfies the our minimum transmission rate per channel.
Regarding the HD channels, we can receive them as well, with some playback degradation. The only client application, being able to display HD channel is “tivizen”. Another interesting remark concerning the client software, is that “Sat>IP” does support only one server per WiFi, where as with “tivizen” you could switch between them. “Sat>IP” offers a better user experience, with more features like: EPG, subtitles, and Teletext, whereas “tivizen” can only decode the EPG. 
Depending on the platform that you want to run our application you must follow the next steps.

###### Raspberry Pi
Install Raspian image on the SD flash card, by following these steps:

1. Download the Raspian image from to your computer from [here](https://www.raspberrypi.org/downloads/raspbian/) (e.g. “2015-05-05-raspbian-wheezy.img”)
2. Insert the SD flash into your computer (Mac).
3. Open a terminal window.
4. Execute:
	- “# diskutil list” to list the available disk, and to get the name of the SD flash on which we will pe loading the image (“2015-05-05-raspbian-wheezy.img”)
	- “# diskutil unmountDisk /dev/disk<disk# from diskutil> “ to unmounts the SD flash, where <disk# from diskutil> must be replace with the number corresponding to your SD flash.
	- “# sudo dd bs=1m if=<path to place where you downloaded the image>/2015-05-05-raspbian-wheezy.img of=/dev/rdisk<disk# from diskutil>” to load the image, where <path to place where you downloaded the image> must be replaced with the path to place where you downloaded the Raspian image.
5. Done. You now have and SD flash with an Raspian image on it.

Place the SD flash into the Raspberry Pi, and boot it up with an Internet connection. The default login to the Raspberry Pi is:
-	Username: pi
-	Password: raspberry
Change to the directory you want to have the application installed; execute the following commands and login with our credential:
“$ git clone -b develop https://github.com/ebu/dtt2ip.git”
“$ cd dtt2ip/”
“$ sudo ./raspberryInstall” 

This will take care of all the packages need, and make all the necessary changes in order to have a fully working t2IP server, the next time you boot the Raspberry Pi.
Restart the Raspberry Pi and wait for 15-20 min in order for the first scan to finish, before connecting any mobile client.
“$ sudo reboot” to restart the Raspberry Pi


###### Synology NAS
Install on your Synology from the Package Center application, Debian Chroot by following the steps:
1.	Go to Package Center and in the Community tab add the following URL:
https://synocommunity.com/packages 
       2.   Select option install from different third party software 
3.	Install Debian Chroot
4.	Make sure Debian Chroot application is running after installation

Install Git from the Package Center and get the following repository and place it in the location you want to have the t2IP server installed (e.g. volume1/yourDir), by following the setps:
1.	Open a terminal window on your computer (Mac):
2.	SSH to the Synology as root:
-	“# ssh root@ip_address_synology” 
-	“> cd /volume1/yourDir/”, this will change to the directory you have placed the t2IP
server application.
-	“> git clone -b develop https://github.com/ebu/dtt2ip.git”
-	“> cd dtt2ip/”
	-     “> ./synologyInstall”,  this will run the installation script

This will take care of all the packages need, and make all the necessary changes in order to have a fully working t2IP server, the next time you start the Debian Chroot application from Synology.
Stop and Start the Debian Chroot application from the Package Center app, and wait for 15-20 min for the first scan to finish before connecting any mobile client.

###### Synology NAS easy

