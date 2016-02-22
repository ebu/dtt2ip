#!/usr/bin/python
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from os import curdir, sep
import time, socket, urlparse, re, cgi

# TO DO create a configuration file
PORT_NUMBER = 8080
global postInc
global k
postInc = 0
k = 0

#This class will handle any incoming request from
#the browser 
class myHandler(BaseHTTPRequestHandler):

	def ms_notify_callback(self, counter):
		MS_NOTIFY_EVENT = 'NOTIFY /Event HTTP/1.0\r\nHOST: 192.168.1.228:52809\r\nCONTENT-TYPE: text/xml; charset="utf-8"\r\nCONTENT-LENGTH: 267\r\nNT: upnp:event\r\nNTS: upnp:propchange\r\nSID: uuid:C0A80173-0000-5687-83E3-00000000001F\r\nSEQ: 0\r\n\r\n<e:propertyset xmlns:e="urn:schemas-upnp-org:event-1-0">\n<e:property>\n<TransferIDs> </TransferIDs>\n</e:property>\n\n<e:property>\n<SystemUpdateID>0</SystemUpdateID>\n</e:property>\n\n<e:property>\n<ContainerUpdateIDs> </ContainerUpdateIDs>\n</e:property>\n\n</e:propertyset>\n\n\r\n\r\n'
		return MS_NOTIFY_EVENT

	def do_UNSUBSCRIVE(self):
		# TO DO
		self.send_response(200)

	#Handler for the SUBSCRIBE requests
	def do_SUBSCRIBE(self):
		parsed_path = urlparse.urlparse(self.path)
		message_parts = []

		for name, value in sorted(self.headers.items()):
			message_parts.append('%s=%s' % (name.lower(), value.rstrip()))

		self.send_response(200)
		self.send_header('SID','uuid:C0A80173-0000-5687-83E3-00000000001F')
		self.send_header('TIMEOUT', 'Second-1800')
		self.send_header('Content-Length', '0')
		self.end_headers()
		print 'Alex SUBSCRIBE'

		# Send the NOTIFY /Event for iOS
		print 'Alex TCP'
		# TO DO get dynamicaly the clients IP address and port (callback socket)
		for message_part in message_parts:
			match1 = re.search(r'callback', message_part)
			if match1:
				print "Alex -------------------------------------"
				match2 = re.search(r':([\w]+)', message_part)
				if match2:
					clientPort = int(match2.group(1))


		clientIP = self.address_string()
		tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		tcpSocket.connect((clientIP, clientPort))
		tcpSocket.send(self.ms_notify_callback(0))
		tcpSocket.close()

	#Handler for the POST requests
	def do_POST(self):
		global postInc
		global k

		# Parse the form data posted
		form = cgi.FieldStorage(
			fp=self.rfile, 
			headers=self.headers,
			environ={'REQUEST_METHOD':'POST',
			'CONTENT_TYPE':self.headers['Content-Type'],
		})
		form = str(form)
		print form
		match1 = re.search(r'ObjectID.0', form)
		match2 = re.search(r'TVChannels', form)

		if match1:
			postInc = 0
			print 'ALEX ------------------- 0 1'
		elif match2:
				postInc = 1
				print 'ALEX ------------------- 1 0'
		else:
			postInc = 2
			print 'ALEX -------------------  UPnPError'

		if postInc == 0:
			self.send_response(200)
			print "-----0-----"
			#Open the static file requested and send it
			f1 = open(curdir + sep + '/alex-MAC.xml') 
			self.send_header('CONTENT-LENGTH', '891')
			self.send_header('CONTENT-TYPE', 'text/xml; charset="utf-8"')
			self.send_header('EXT', '')
			self.send_header('Connection', 'close')
			self.send_header('X-User-Agent:', 'redsonic')
			self.end_headers()
			self.wfile.write(f1.read())
			f1.close()
		if postInc == 1:
			self.send_response(200)
			print "TVChannels"
			# time.sleep(1)
			#Open the static file requested and send it
			if k == 0:
				f2 = open(curdir + sep + '/TVChannels1.xml') 
				self.send_header('CONTENT-LENGTH', '1142')
			else:
				f2 = open(curdir + sep + '/TVChannels.xml') 
				self.send_header('CONTENT-LENGTH', '20856')
			k = (k + 1) % 2
			self.send_header('CONTENT-TYPE', 'text/xml; charset="utf-8"')
			self.send_header('EXT', '')
			self.send_header('Connection', 'close')
			self.send_header('X-User-Agent:', 'redsonic')
			self.end_headers()
			self.wfile.write(f2.read())
			f2.close()
		if postInc == 2:
			self.send_response(500)
			print "UPnPError"
			# time.sleep(1)
			#Open the static file requested and send it
			f2 = open(curdir + sep + '/UPnPError.xml') 
			self.send_header('CONTENT-LENGTH', '399')
			self.send_header('CONTENT-TYPE', 'text/xml; charset="utf-8"')
			self.send_header('EXT', '')
			self.end_headers()
			self.wfile.write(f2.read())
			f2.close()

		print 'Alex POST'
	
	#Handler for the GET requests
	def do_GET(self):
		if self.path=="/":
			self.path="/index_example2.html"
			print "TO DO .html"

		try:
			#Check the file extension required and
			#set the right mime type
			sendReply = False
			if self.path.endswith(".jpg"):
				mimetype='image/jpg'
				sendReply = True

			if self.path.endswith(".ts"):
				sendReply = True
				print "TO DO .ts"

			if self.path.endswith("alexDescription.xml"):
				#Open the static file requested and send it
				f = open(curdir + sep + '/alexDescription.xml') 
				self.send_response(200)
				self.send_header("CONTENT-LENGTH", '1989')
				self.send_header('CONTENT-TYPE', 'text/xml; charset="utf-8"')
				self.send_header("LAST-MODIFIED", "Tue, 22 Dec 2015 15:25:23 GMT")
				self.send_header("X-User-Agent", "redsonic")
				self.send_header("CONNECTION", "close")
				self.send_header("CONTENT-LANGUAGE", "en-us")
				self.end_headers()
				self.wfile.write(f.read())
				f.close()

			if self.path.endswith("alexContentDirectorySCPD.xml"):
				#Open the static file requested and send it
				f4 = open(curdir + sep + '/alexContentDirectorySCPD.xml') 
				self.send_response(200)
				self.send_header("CONTENT-LENGTH", '14159')
				self.send_header('CONTENT-TYPE', 'text/xml; charset="utf-8"')
				self.send_header("LAST-MODIFIED", "Tue, 22 Dec 2015 15:25:23 GMT")
				self.send_header("X-User-Agent", "redsonic")
				self.send_header("CONNECTION", "close")
				self.send_header("CONTENT-LANGUAGE", "en-us")
				self.end_headers()
				self.wfile.write(f4.read())
				f4.close()

			if self.path.endswith("alexConnectionManagerSCPD.xml"):
				#Open the static file requested and send it
				f5 = open(curdir + sep + '/alexConnectionManagerSCPD.xml') 
				self.send_response(200)
				self.send_header("CONTENT-LENGTH", '3509')
				self.send_header('CONTENT-TYPE', 'text/xml; charset="utf-8"')
				self.send_header("LAST-MODIFIED", "Tue, 22 Dec 2015 15:25:23 GMT")
				self.send_header("X-User-Agent", "redsonic")
				self.send_header("CONNECTION", "close")
				self.send_header("CONTENT-LANGUAGE", "en-US")
				self.end_headers()
				self.wfile.write(f5.read())
				f5.close()

			# Handler different picture format
			if self.path.endswith("/EBU-logo120x120.jpeg"):
				f6 = open(curdir + sep + '/EBU-logo120x120.jpeg') 
				self.send_response(200)
				self.send_header("LAST-MODIFIED", "Tue, 22 Dec 2015 15:25:23 GMT")
				self.send_header("ETag", '"1d77-5193eaf674240"')
				self.send_header("Accept-Ranges", 'bytes')
				self.send_header("Content-Length", '4326')
				self.send_header("Keep-Alive", 'timeout=5, max=100')
				self.send_header("Connection", "Keep-Alive")
				self.send_header('Content-Type', 'image/jpeg')
				self.end_headers()
				self.wfile.write(f6.read())
				f6.close()
			if self.path.endswith("/EBU-logo120x120.png"):
				f7 = open(curdir + sep + '/EBU-logo120x120.png') 
				self.send_response(200)
				self.send_header("Connection", "close")
				self.send_header("EXT", '')
				self.send_header("realTimeInfo.dlna.org", 'DLNA.ORG_TLAG=*')
				self.send_header("transferMode.dlna.org", 'Interactive')
				self.send_header('Content-Type', 'image/png')
				self.send_header("Content-Length", '8336')
				self.end_headers()
				self.wfile.write(f7.read())
				f7.close()
			if self.path.endswith("/EBU-logo48x48.jpeg"):
				f8 = open(curdir + sep + '/EBU-logo48x48.jpeg') 
				self.send_response(200)
				self.send_header("LAST-MODIFIED", "Tue, 22 Dec 2015 15:25:23 GMT")
				self.send_header("ETag", '"1d77-5193eaf674240"')
				self.send_header("Accept-Ranges", 'bytes')
				self.send_header("Content-Length", '2050')
				self.send_header("Keep-Alive", 'timeout=5, max=100')
				self.send_header("Connection", "Keep-Alive")
				self.send_header('Content-Type', 'image/jpeg')
				self.end_headers()
				self.wfile.write(f8.read())
				f8.close()
			if self.path.endswith("/EBU-logo48x48.png"):
				f9 = open(curdir + sep + '/EBU-logo48x48.png') 
				self.send_response(200)
				self.send_header("Connection", "close")
				self.send_header("EXT", '')
				self.send_header("realTimeInfo.dlna.org", 'DLNA.ORG_TLAG=*')
				self.send_header("transferMode.dlna.org", 'Interactive')
				self.send_header('Content-Type', 'image/png')
				self.send_header("Content-Length", '2767')
				self.end_headers()
				self.wfile.write(f9.read())
				f9.close()

			return
		except IOError:
			self.send_error(404,'File Not Found: %s' % self.path)

try:
	#Create a web server and define the handler to manage the
	#incoming request
	server = HTTPServer(('', PORT_NUMBER), myHandler)
	print 'Started httpserver on port ' , PORT_NUMBER
	
	#Wait forever for incoming htto requests
	server.serve_forever()

except KeyboardInterrupt:
	print '^C received, shutting down the web server'
	server.socket.close()
	