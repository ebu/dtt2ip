# DTT2IP

## Table of content

1. [Introduction](#introduction)
2. [Goal](#goal)
3. [Sat>IP overview](sat2ip-overview.md)
4. [Discovery state machine](discovery-sm.md)
5. [RTSP state machine](rtsp-sm.md)
6. [RTP/UDP vs. HTTP/TCP](rtp_udp-http_tcp.md)
7. [DVBlast overview](dvblast-overview.md)
8. [T2IP Server implementation](t2ip.md)
9. [Results and utilization](results-utilization.md)
10. [Future work](future-work.md)
11. [Conclusion and Reference](conclusions-reference.md)


## Introduction

In this paper we try to explain the concept of broadcasting over Wi-Fi networks. We cover the basic knowledge regarding the protocols used, SSDP, RTP, RTSP and the existing technologies and solutions.  The following chapters will be dedicated to a better understanding of the necessary steps taken in our implementation.
In a nutshell we have designed a server, from two state machines: the first one handles the discovery by other clients and servers, and the other handles the RTP video streaming request. 


## Goal

The goal of the this project is to have a full working solution in order to provide terrestrial television, for any indoor Wi-Fi network, that can be access on any portable device.
In order to achieve this we have set a few requirements in order to have a standardized solution that can fulfill any demand from the user perspective.
These are the following: 
•	2 or more DVB-T tuners
•	Good image quality and response
•	Interoperability with all devices (Android, iOS, etc.)
•	Does not block your Wi-Fi for TV only
•	Plug and play and easy to use
•	Multiple user capabilities for watching different programs
•	Interoperability with other SAT>IP servers
•	EPG / Subtitles / HbbTV
•	Wireless connectivity to our network
•	Build-in storage / usb ports / network storage
•	Recording capabilities
•	Be accessible from any device that haves a browser
Before we committing to the new implementation, at the beginning we have investigated the existing ones, that a regular user can have access. Without losing objectivity, and after technical and not technical debates we have reached the conclusion that the preexisting solution does not fully convince us, and that is better to have our own EBU software. However our research, has paid of with the interesting concept of SAT>IP, that will be explained in the following chapter.

