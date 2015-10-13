# Dvblast overview

DVBlast is written to be the core of a custom IRD, CID, or ASI gateway, based on a PC with a Linux-supported card. It is very lightweight and stable, designed for 24/7 operation.
DVBlast does not do any kind of processing on the elementary streams, such as transcoding, PID remapping or remultiplexing. If you were looking for these features, switch to VLC. It does not stream from plain files (have a look at multicat instead).
DVBlast supports several input methods:
		linux-dvb-supported cards (DVB-S, DVB-S2, DVB-C, DVB-T...) with or without CI interface
		DVB-ASI cards (from Computer Modules)
		UDP or RTP, unicast or multicast, streams carrying a transport stream

It outputs one or several RTP streams carrying transport streams with:
		hardware or software PID filtering
		PID-based or service-based demultiplexing
		optional descrambling via CAM device
		optional DVB tables
##### [Back to Table of content](README.md)
