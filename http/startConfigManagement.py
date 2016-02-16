#!/usr/bin/python

import subprocess, os, threading
import commands, re, shutil
global d_tuner
global CHECKMUMUFILE_NOT_TERMINATE
global DETECTION_NOT_TERMINATE



from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from os import curdir, sep
import time, socket, urlparse, re, cgi

# TO DO create a configuration file
PORT_NUMBER = 8080
global postInc
global k
postInc = 0
k = 0
global servedXMLSize
global servedXMLSize1

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
				self.send_header('CONTENT-LENGTH', str(servedXMLSize1))
			else:
				f2 = open(curdir + sep + '/TVChannels.xml') 
				self.send_header('CONTENT-LENGTH', str(servedXMLSize))
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
				self.send_header("CONTENT-LENGTH", '1990')
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

def scanForAvailableFreq(tuner='0'):
	f = open("dvb_channel.conf", 'w')
	f.close()
	cmd = 'dvbv5-scan channelList -o dvb_channel.conf' + ' -a ' + tuner
	outtext = commands.getoutput(cmd)
	(exitstatus, outtext) = commands.getstatusoutput(cmd)
	if not exitstatus:
		f = open("dvb_channel.conf", 'r')
		lines = f.readlines()
		f.close()
		if lines:
			print "Scan finished and updated the frequencies available\n"
		else:
			print "Scan finished, but no signal from antenna detected\n"
	else:
		print "ERROR scanForAvailableFreq(): Scan did not find any tuners available.\n\tStop the application, before requesting a new scan\n"

def detectDvbTT2Tuners():
	global d_tuner
	global DETECTION_NOT_TERMINATE

	while DETECTION_NOT_TERMINATE:
		p = subprocess.Popen("ls /dev/dvb/", stdout=subprocess.PIPE, shell=True)
		try:
			(output, err) = p.communicate()
		except:
			print "detectDvbTT2Tuners: No Tuners detected"
		adapters = output.split("\n")
		# The adapters array will have an empty entry, because of the output string, and the way we split
		adapters = adapters[:-1]
		tuner_port_init = 4028
		new_entries = []
		adapter_id_array = []
		delete_array = []
		
		# Keep the d_tuner dictionary up to date with the hardware changes
		if d_tuner:
			# Check for new adapters added
			for adapter in adapters:
				id_found = False
				match_adapter = re.search(r'adapter([\d]+)', adapter)
				if match_adapter:
					adapter_id_array.append(match_adapter.group(1))
					tuner_port = int(match_adapter.group(1)) + tuner_port_init
					for tuner in d_tuner:
						if d_tuner[tuner][1] == match_adapter.group(1):
							id_found = True
							break
					if not id_found:
						d_tuner[str(tuner_port)] = (0, match_adapter.group(1))
						new_entries.append(str(tuner_port))
			# Check for adapters removed
			for tuner in d_tuner:
				id_found = False
				for adapter_id in adapter_id_array:
					if d_tuner[tuner][1] == adapter_id:
						id_found = True
						break
				if not id_found:
					delete_array.append(tuner)
			# Delete the hardware items removed 
			for item in delete_array:		
				del d_tuner[item]
			num_tuners = len(adapters)
			# return (num_tuners, d_tuner, new_entries)
		else:
			for adapter in adapters:
				match_adapter = re.search(r'adapter([\d]+)', adapter)
				if match_adapter:
					# Default tuner triplet (availabilty, frequency, adapter_id)
					tuner_port = int(match_adapter.group(1)) + tuner_port_init
					d_tuner[str(tuner_port)] = (0, match_adapter.group(1))
					new_entries.append(str(tuner_port))
			num_tuners = len(d_tuner)
			# return (num_tuners, d_tuner, new_entries)


def dictionariesSidFreq():
	f = open("dvb_channel.conf", 'r')
	lines = f.readlines()
	f.close()
	d_sid = {}
	d_freq = {}

	for line in lines:
		match_name = re.search(r'[^[]*\[([^]]*)\]', line)
		match_freq = re.search(r'FREQUENCY = ([\w]+)', line)
		match_bandwidth = re.search(r'BANDWIDTH_HZ = ([\w]+)', line)
		match_ds = re.search(r'DELIVERY_SYSTEM = ([\w]+)', line)
		match_sid = re.search(r'SERVICE_ID = ([\w]+)', line)

		try:
			if match_name:
				name = match_name.groups()[0]
			if match_sid:
				sid = match_sid.group(1)
			if match_freq:
				freq = int(match_freq.group(1))/1000
			if match_bandwidth:
				bandwidth = int(match_bandwidth.group(1))/1000000
			if match_ds:
				d_freq[str(freq)] = (str(bandwidth), match_ds.group(1))
				d_sid[name] = (str(sid), str(freq))
		except:
			print "ERROR dictionaryFreq(): The dvb_channel.conf migth has changed format."

	return d_sid, d_freq

def createConfiXMLForTuner(tuner_id, tuner_port, d_sid):
	f = open("allFreq" + tuner_id + ".xml" , 'w')
	f.write('<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">\n')
	f.write('<s:Body><u:BrowseResponse xmlns:u="urn:schemas-upnp-org:service:ContentDirectory:1"><Result>&lt;DIDL-Lite xmlns:dc=&quot;http://purl.org/dc/elements/1.1/&quot; xmlns:upnp=&quot;urn:schemas-upnp-org:metadata-1-0/upnp/&quot; xmlns=&quot;urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/&quot; xmlns:dlna=&quot;urn:schemas-dlna-org:metadata-1-0/&quot; xmlns:pns=&quot;http://www.philips.com/streamiumns/&quot; &gt;\n')
	item_id = 10330000
	for item in d_sid:
		f.write('&lt;item id=&quot;0\TVChannels\\' + str(item_id) + 
					'&quot; parentID=&quot;TVChannels&quot; restricted=&quot;1&quot;&gt;\n')
		f.write('&lt;dc:title&gt;' + item + 
					'&lt;/dc:title&gt;&lt;upnp:class&gt;object.item.videoItem.videoBroadcast&lt;/upnp:class&gt;&lt;res protocolInfo=&quot;http-get:*:video/mpeg:DLNA.ORG_PN=MPEG_TS_SD_EU_ISO;DLNA.ORG_OP=00;DLNA.ORG_FLAGS=01700000000000000000000000000000&quot;&gt;http://192.168.1.115:' +
					tuner_port + '/bysid/' + d_sid[item][0] + '/byfreq/' + d_sid[item][1] +
					'&lt;/res&gt;\n')
		f.write('&lt;/item&gt;\n\n')
		item_id = item_id + 10000
	f.write('&lt;/DIDL-Lite&gt;</Result><NumberReturned>' + 
				str(len(d_sid)) + '</NumberReturned><TotalMatches>' +
				str(len(d_sid)) + '</TotalMatches><UpdateID>0</UpdateID></u:BrowseResponse></s:Body></s:Envelope>')
	f.close()


def createServerdXML(d_tuner, init=1, freq=0):
	global servedXMLSize
	global servedXMLSize1
	freq_used_array = []
	line_to_keep2 = "&lt;/item&gt;\n\n"
	numberOfMaches = 0
	if init:
		shutil.copy("allFreq0.xml", "TVChannels.xml")
	else: 
		f = open("TVChannels.xml", 'r')
		lines = f.readlines()
		f.close()
		f = open("TVChannels.xml", 'w')
		# print lines
		# Depending if a tuner has become available or has been occupied
		# we perform different updates in the SERVED xml
		if freq == 0:
			tuner_port_unused = -1
			for tuner in d_tuner:
				if d_tuner[tuner][0] != freq:
					freq_used_array.append(d_tuner[tuner][0])
				else:
					tuner_port_unused = tuner
			try:
				f2 = open("allFreq" + d_tuner[tuner_port_unused][1] + ".xml", 'r')
				lines_init = f2.readlines()
				f2.close()
				for line in lines_init:
					if lines_init.index(line) == len(lines_init)-1:
						f.write('&lt;/DIDL-Lite&gt;</Result><NumberReturned>' + str(numberOfMaches) + '</NumberReturned><TotalMatches>' + str(numberOfMaches) + '</TotalMatches><UpdateID>0</UpdateID></u:BrowseResponse></s:Body></s:Envelope>')
					else:
						line_found = False
						match_other_freq = re.search(r'([\w]+)/([\w]+)/([\w]+)/byfreq/',line)
						if match_other_freq:
							# Put the used frequencies into the SERVED XML
							for freq_used in freq_used_array:
								match_freq = re.search(r'([\w]+)/([\w]+)/([\w]+)/byfreq/' + str(freq_used) ,line)
								if match_freq:
									line_found = True
									line_index = line.index(match_freq.group(1))
									for tuner in d_tuner:
										if d_tuner[tuner][0] == freq_used:
											f.write(line[:line_index] + tuner + line[line_index + len(tuner):])
											numberOfMaches = numberOfMaches + 1
											break
							# Put the frequencies that have become available into the SERVED XML
							if not line_found:
								f.write(line)
								numberOfMaches = numberOfMaches + 1
						else:
							f.write(line)
			except:
				print "createServerdXML: No Tuner available found ", tuner_port_unused
		else:
			print "Freq received == ", freq
			for line in lines:
				if lines.index(line) == len(lines)-1:
						f.write('&lt;/DIDL-Lite&gt;</Result><NumberReturned>' + str(numberOfMaches) + '</NumberReturned><TotalMatches>' + str(numberOfMaches) + '</TotalMatches><UpdateID>0</UpdateID></u:BrowseResponse></s:Body></s:Envelope>')
				else:
					match_other_freq = re.search(r'([\w]+)/([\w]+)/([\w]+)/byfreq/',line)
					if match_other_freq:
						match_freq = re.search(r'([\w]+)/([\w]+)/([\w]+)/byfreq/' + str(freq) ,line)
						if match_freq:
							tuner_port = match_freq.group(1)
							line_index = line.index(tuner_port)
							f.write(line_to_keep)
							f.write(line[:line_index] + tuner_port + line[line_index + len(tuner_port):])
							# print line[:line_index] + tuner_port + line[line_index + len(tuner_port):]
							f.write(line_to_keep2)
							numberOfMaches = numberOfMaches + 1
						else:
							for tuner in d_tuner:
								if not d_tuner[tuner][0]:
									tuner_port = match_other_freq.group(1)
									line_index = line.index(tuner_port)
									f.write(line_to_keep)
									# print line[:line_index] + tuner + line[line_index + len(tuner_port):]
									f.write(line[:line_index] + tuner + line[line_index + len(tuner_port):])
									f.write(line_to_keep2)
									numberOfMaches = numberOfMaches + 1
									break
					else:
						match_tv_channels = re.search(r'TVChannels', line)
						if match_tv_channels:
							line_to_keep = line
						else:
							match_item = re.search(r'/item',line)
							if not match_item and line != "\n":
								f.write(line)
		f.close()
		servedXMLSize = os.path.getsize("TVChannels.xml")
		# Create the xml with only the first channel 
		f = open("TVChannels.xml", 'r')
		lines = f.readlines()
		f.close()
		f = open("TVChannels1.xml", 'w')
		for i in range(5):
			f.write(lines[i])
		f.write('\n&lt;/DIDL-Lite&gt;</Result><NumberReturned>1</NumberReturned><TotalMatches>' + str(numberOfMaches) +'</TotalMatches><UpdateID>0</UpdateID></u:BrowseResponse></s:Body></s:Envelope>')
		f.close()
		servedXMLSize1 = os.path.getsize("TVChannels1.xml")
		return (servedXMLSize, d_tuner)

def checkMumuFile():
	global CHECKMUMUFILE_NOT_TERMINATE
	global d_tuner

	while CHECKMUMUFILE_NOT_TERMINATE:
		f = open("test_mumu.txt", 'r')
		freq = f.readlines()
		f.close()
		# Check if we have receive a tuning request
		if freq:
			print "freq == ", freq
			if int(freq[0]) > 100000:
				# Assign freq to tuner 0
				# Occupy the tuner, by making it unavailble and specify the frequency
				d_tuner['4028']= (freq, d_tuner['4028'][1])
				filesize, d_tuner = createServerdXML(d_tuner, 0, int(freq[0]))
				# print "filesize ", filesize
				# print  d_tuner
				f = open("test_mumu.txt", 'w')
				f.close()
			# Check if we have receive a freeing of resources
			elif int(freq[0]) == 0:
				#Remove the freq from tuner 0
				d_tuner['4028'] = (0, '0')
				filesize, d_tuner = createServerdXML(d_tuner, 0, int(freq[0]))
				# print "filesize ", filesize
				# print  d_tuner
				f = open("test_mumu.txt", 'w')
				f.close()


def main():
	global d_tuner
	global CHECKMUMUFILE_NOT_TERMINATE
	global DETECTION_NOT_TERMINATE 
	global servedXMLSize
	global servedXMLSize1

	servedXMLSize = os.path.getsize("TVChannels.xml")
	servedXMLSize1 = os.path.getsize("TVChannels1.xml")
	d_tuner = {}
	CHECKMUMUFILE_NOT_TERMINATE = True
	DETECTION_NOT_TERMINATE = True

	t1 = threading.Thread(target=detectDvbTT2Tuners)
	t1.daemon = True
	t1.start()

	# Wait for d_tuner to be created
	while not d_tuner:
		continue

	d_sid, d_freq = dictionariesSidFreq()
	# createConfiXMLForTuner('0', '4028', d_sid)
	# checkMumuFile()
	t2 = threading.Thread(target=checkMumuFile)
	t2.daemon = True
	t2.start()

	#Create a web server and define the handler to manage the
	#incoming request
	server = HTTPServer(('', PORT_NUMBER), myHandler)
	print 'Started httpserver on port ' , PORT_NUMBER
	# #Wait forever for incoming htto requests
	t3 = threading.Thread(target=server.serve_forever())
	t3.daemon = True
	t3.start()

	try:
		while t1.is_alive() and t2.is_alive() and t3.is_alive:
			t1.join(timeout=1.0)
			t2.join(timeout=1.0)
			t3.join(timeout=1.0)
	except(KeyboardInterrupt, SystemExit):
		CHECKMUMUFILE_NOT_TERMINATE = False
		server.socket.close()

	# num_tuners, d_tuner, new_entries = detectDvbTT2Tuners(d_tuner)
	# print num_tuners
	# print d_tuner
	# print new_entries
	# scanForAvailableFreq()
	# Just for on tuner now
	# print createServerdXML()
	# createServerdXML(0, '522000', 2) 



if __name__ == '__main__':
	main()