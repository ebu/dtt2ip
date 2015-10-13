# RTSP state machine

Control provides the functionality necessary for SAT>IP clients to request the delivery of media streams from SAT>IP servers. Device Control in SAT>IP can be handled through the use of RTSP or HTTP protocol mechanisms. 
SAT>IP servers shall fully implement all protocol mechanisms specified in the current specification. Clients only need to implement those SAT>IP protocols important to their own proper operation. 

RTSP
SAT>IP clients use RTSP over TCP to setup RTSP sessions, with a SAT>IP server. An RTSP session starts with a RTSP SETUP request and ends with an RTSP TEARDOWN message. A number assigned by the server uniquely identifies a session. 
When setting up an RTSP session, clients define the transport mode, which will be used for delivering the actual media stream. In the SETUP message they also define or start defining through a URI query the media stream object that they want to be delivered. SAT>IP media stream objects are identified through a streamID. A media stream object is only modified through URI queries and no modification shall occur from any associated RTSP method used to invoke these queries. 
Actual stream play-out is started in a session by invoking a PLAY message containing the streamID. During the course of the session, clients can change channels by invoking further PLAY messages with the URI query parameters corresponding to different requested channels. 
In order to keep sessions with a server alive, clients need to issue regular RTSP messages within the timeout period (announced by the server in the original reply to the SETUP message). In SAT>IP RTSP OPTIONS messages shall be used as the default keep alive messages. 

![alt text][figure1]
[figure1]:https://github.com/ebu/dtt2ip/blob/master/docs/images/figure3.png

Clients and servers shall support RTSP version 1.0 as described by Appendix D of RFC 2326 [6]. 
RTSP is a text-based protocol and uses the ISO 10646 character set in UTF-8 encoding. Header field names are case-insensitive and header field values are case-sensitive in RTSP. Lines are terminated by CRLF. 
SAT>IP uses the standard RTSP server port number 554. 
##### [Back to Table of content](README.md)
