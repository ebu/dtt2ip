#!/usr/bin/python

from random import randint
import sys, traceback, threading, socket, signal, re, commands, os, time
from subprocess import Popen
from resources import getFrontEnds

global session
global state
global clientsDict
global chList
global streamID
global dvblastReload
global frontEndsDict

dvblastReload = 0
clientsDict = {}
chList = {}

frontEndsDict = getFrontEnds()

f = open('conf/rtspServer.config', 'r')
lines = f.readlines()
for i in range(5, len(lines)):
	line = lines[i]
	lineArray = line.split(' ')
	if lineArray[0] != '#':
		chList[lineArray[0]] = lineArray[1:-1]
f.close()

session = ''
state = 0 # INI = 0
streamID = 0


class rtspServerWorker:
	# Events
	SETUP = 'SETUP'
	PLAY = 'PLAY'
	TEARDOWN = 'TEARDOWN'
	OPTIONS = 'OPTIONS'
	DESCRIBE = 'DESCRIBE'
	CLOSE_CONNETION = 'CLOSE_CONNETION'
	
	# State
	INI = 0
	READY = 1
	PLAYING = 2

	OK_200_OPTIONS = 0
	FILE_NOT_FOUND_404 = 1
	CON_ERR_500 = 2
	CLOSING_CONNECTION = 3
	OK_404_DESCRIBE = 4
	OK_200_DESCRIBE = 5
	OK_200_DESCRIBE_NOSIGNAL = 6
	OK_200_SETUP = 7
	OK_200_SETUP_PIDS = 8
	OK_200_PLAY = 9
	OK_200_TEARDOWN = 10

	SERVER_RUNNING = 1

	clientInfo = {}
	
	def __init__(self, clientInfo):
		global clientsDict

		rtpPort = ''
		state = 0
		stream = 0
		src = ''
		freq = ''
		pol = ''
		ro = ''
		msys = ''
		mtype = ''
		plts = ''
		sr = ''
		fec = ''
		status = 'inactive'

		self.clientInfo = clientInfo
	
		if self.clientInfo['addr_IP'] not in clientsDict:
			clientsDict[self.clientInfo['addr_IP']] = {}
			clientsDict[self.clientInfo['addr_IP']]['rtpPort'] = rtpPort
			clientsDict[self.clientInfo['addr_IP']]['state'] = state
			clientsDict[self.clientInfo['addr_IP']]['stream'] = stream
			clientsDict[self.clientInfo['addr_IP']]['src'] = src
			clientsDict[self.clientInfo['addr_IP']]['freq'] = freq
			clientsDict[self.clientInfo['addr_IP']]['pol'] = pol
			clientsDict[self.clientInfo['addr_IP']]['ro'] = ro
			clientsDict[self.clientInfo['addr_IP']]['msys'] = msys
			clientsDict[self.clientInfo['addr_IP']]['mtype'] = mtype
			clientsDict[self.clientInfo['addr_IP']]['plts'] = plts
			clientsDict[self.clientInfo['addr_IP']]['sr'] = sr
			clientsDict[self.clientInfo['addr_IP']]['fec'] = fec
			clientsDict[self.clientInfo['addr_IP']]['status'] = status

		
	def run(self):
		t = threading.Thread(target=self.recvRtspRequest)
		t.daemon = True
		t.start()

		try:
			while t.is_alive():
				t.join(timeout=1.0)
		except (KeyboardInterrupt, SystemExit):
			# shutdown_event.set()
			self.SERVER_RUNNING = 0
	
	def recvRtspRequest(self):
		"""Receive RTSP request from the client."""
		connSocket = self.clientInfo['rtspSocket']#[0]
		while self.SERVER_RUNNING:            
			data = connSocket.recv(1024)
			if data:
				# print "Data received:\n" + data
				self.processRtspRequest(data)
	
	def processRtspRequest(self, data):
		"""Process RTSP request sent from the client."""
		global session
		global state
		global streamID
		global dvblastReload
		global chList	
		global clientsDict  # clientsDict = { 'ip_client_1': {'rtpPort': '', state: 0, 'freq': '', stream: 0, 'src': '', 'pol': '', 'ro': '', 'msys': '', 'mtype': '', 'plts': '', 'sr': '', 'fec': '', 'status': 'sendonly'}}
		global frontEndsDict

		# Initialize local variables
		freq = ''
		pids = ''
		delPids = 0
		delPid = 0

		# Get the request type
		request = data.split('\n')
		line1 = request[0].split(' ')
		requestType = line1[0]
		
		# Get the last part of the URI
		uriLastPart = line1[1]
		
		# Get the RTSP sequence number 
		for seq_find in request[1:]:
			# Word parsing for general URI request seq/client_port
			match_seq = re.search(r'CSeq', seq_find)
			if match_seq:
				# To do check the output
				seq = seq_find.split(':')
			match_client_port = re.search(r'client_port', seq_find)
			if match_client_port:
				seq_find_array = seq_find.split(';')
				self.clientInfo['rtpPort']= seq_find_array[2].split('=')[1].split('-')[0]	
				clientsDict[self.clientInfo['addr_IP']]['rtpPort'] = self.clientInfo['rtpPort']
				# print "clientsDict", clientsDict

		# Word parsing for SETUP/PLAY URI request
		if requestType == self.SETUP or requestType == self.PLAY:
			match_pids = re.search(r'pids=([\w]+)', uriLastPart)
			if match_pids:
				pids = match_pids.group(1)
			match_delpids = re.search(r'delpids=([\w]+)', uriLastPart)
			if match_delpids:
				delPids = 1
				delPid = int(match_delpids.group(1))

		# Process SETUP request
		if requestType == self.SETUP:
			# Word parsing for SETUP URI request
			match_src = re.search(r'src=([\w]+)', uriLastPart)
			if match_src:
				clientsDict[self.clientInfo['addr_IP']]['src'] = match_src.group(1)
			match_freq = re.search(r'freq=([\w]+)', uriLastPart)
			if match_freq:
				freq = match_freq.group(1)
				clientsDict[self.clientInfo['addr_IP']]['freq'] = freq
			match_pol = re.search(r'pol=([\w]+)', uriLastPart)
			if match_pol:
				clientsDict[self.clientInfo['addr_IP']]['pol'] = match_pol.group(1)
			match_ro = re.search(r'ro=([\w]+...)', uriLastPart)
			if match_ro:
				clientsDict[self.clientInfo['addr_IP']]['ro'] = match_ro.group(1)
			match_msys = re.search(r'msys=([\w]+)', uriLastPart)
			if match_msys:
				clientsDict[self.clientInfo['addr_IP']]['msys'] = match_msys.group(1)
			match_mtype = re.search(r'mtype=([\w]+)', uriLastPart)
			if match_mtype:
				clientsDict[self.clientInfo['addr_IP']]['mtype'] = match_mtype.group(1)
			match_plts = re.search(r'plts=([\w]+)', uriLastPart)
			if match_plts:
				clientsDict[self.clientInfo['addr_IP']]['plts'] = match_plts.group(1)
			match_sr = re.search(r'sr=([\w]+)', uriLastPart)
			if match_sr:
				clientsDict[self.clientInfo['addr_IP']]['sr'] = match_sr.group(1)
			match_fec = re.search(r'fec=([\w]+)', uriLastPart)
			if match_fec:
				clientsDict[self.clientInfo['addr_IP']]['fec'] = match_fec.group(1)

			clientsDict[self.clientInfo['addr_IP']]['status'] = 'sendonly'

			# Process SETUP request If STATE is INI
			if clientsDict[self.clientInfo['addr_IP']]['state'] == self.INI: 
				print "processing SETUP, New State: READY\n"
				clientsDict[self.clientInfo['addr_IP']]['state'] = self.READY

				# # Generate a randomized RTSP session ID
				# self.clientInfo['session'] = randint(100000, 999999)
				session = 'c8d13e72c33931f'
				# print "SESSION", session
				clientsDict[self.clientInfo['addr_IP']]['stream'] = (clientsDict[self.clientInfo['addr_IP']]['stream'] + 1) % 65536
	
				# Send RTSP reply
				if freq in chList:
					f = open('dvb-t/pid' + chList[freq][0] + 'adapter0' + '.cfg', 'a')
					f.write(self.clientInfo['addr_IP'] + ':' + clientsDict[self.clientInfo['addr_IP']]['rtpPort'] + '\t1\t' + chList[freq][3] + '\n')
					f.close()
					dvblastReload = 1
					# print "ALEX ----------", clientsDict[self.clientInfo['addr_IP']]

				if pids == 'none' or pids == '':
					self.replyRtsp(self.OK_200_SETUP, seq[1])
					if pids == 'none':
						clientsDict[self.clientInfo['addr_IP']]['status'] = 'inactive'
				else:
					self.replyRtsp(self.OK_200_SETUP_PIDS, seq[1])

			# Process SETUP request If STATE is READY
			elif clientsDict[self.clientInfo['addr_IP']]['state'] == self.READY: 
				print "processing SETUP, State: READY\n"
				print ""

				# Send RTSP reply
				self.replyRtsp(self.OK_200_SETUP, seq[1])

			# Process SETUP request If STATE is PLAYING
			elif clientsDict[self.clientInfo['addr_IP']]['state'] == self.PLAYING:
				print "processing SETUP, State: PLAYING\n"
				
				if freq in chList:
					f = open('dvb-t/pid' + chList[freq][0] + 'adapter0' + '.cfg', 'r')
					lines = f.readlines()
					f.close()

					f = open('dvb-t/pid' + chList[freq][0] + 'adapter0' +  '.cfg', 'w')
					lineToCompare = self.clientInfo['addr_IP']

					for line in lines:
						print "line ", line
						match_line = re.search(lineToCompare, line)
						print "line to compare ", lineToCompare
						if not match_line:
							f.write(line)
					
					f.write(self.clientInfo['addr_IP'] + ':' + clientsDict[self.clientInfo['addr_IP']]['rtpPort'] + '\t1\t' + chList[freq][3] + '\n')
					f.close()
					dvblastReload = 1
					# print "ALEX ----------", clientsDict[self.clientInfo['addr_IP']]
				self.replyRtsp(self.OK_200_SETUP, seq[1])
				
		# Process PLAY request 		
		elif requestType == self.PLAY:

			if clientsDict[self.clientInfo['addr_IP']]['state'] == self.PLAYING or clientsDict[self.clientInfo['addr_IP']]['state'] == self.READY: 
				if clientsDict[self.clientInfo['addr_IP']]['state'] == self.READY:
					print "processing PLAY, New State: PLAYING\n"
					clientsDict[self.clientInfo['addr_IP']]['state'] = self.PLAYING
				else:
					print "processing PLAY, State: PLAYING\n"
				self.replyRtsp(self.OK_200_PLAY, seq[1])

				# START/RELOAD configuration for dvblast only if we have a streamID, the configuration file has been update and the PLAY URI is not a delete pid
				if clientsDict[self.clientInfo['addr_IP']]['stream'] and dvblastReload and delPids == 0:
					# Search for any configured tuner with the frequency that we want to tune to
					for frontEnd in frontEndsDict:
						print "frontEndsDict", frontEndsDict
						print "freq", chList[clientsDict[self.clientInfo['addr_IP']]['freq']][0]
						if frontEndsDict[frontEnd]['freq'] == chList[clientsDict[self.clientInfo['addr_IP']]['freq']][0]:
							cmd = 'dvblastctl -r /tmp/dvblast' + chList[clientsDict[self.clientInfo['addr_IP']]['freq']][0] + frontEnd + '.sock reload'
							# print 'about to run: ', cmd
							os.system(cmd)
							dvblastReload = 0
							if  frontEndsDict[frontEnd]['owner'] != self.clientInfo['addr_IP']:
								frontEndsDict[frontEnd]['owner'] = '255.255.255.255'  # '255.255.255.255' the IP address for specifying multiple owners
					# If we did not find any tuner that has that frequency configured then, search for any available tuner
					if dvblastReload:
						for frontEnd in frontEndsDict:
							if frontEndsDict[frontEnd]['freq'] == '':
								cmd = 'dvblast -a ' + frontEnd[-1] + ' -c dvb-t/pid' + chList[clientsDict[self.clientInfo['addr_IP']]['freq']][0] + frontEnd + '.cfg -f ' + chList[clientsDict[self.clientInfo['addr_IP']]['freq']][0] + ' -b 8 -C -u -r /tmp/dvblast' + chList[clientsDict[self.clientInfo['addr_IP']]['freq']][0] + frontEnd + '.sock'
								dvblastReload = 0
								frontEndsDict[frontEnd]['freq'] = chList[clientsDict[self.clientInfo['addr_IP']]['freq']][0]
								frontEndsDict[frontEnd]['owner'] = self.clientInfo['addr_IP']
								# Start dvblast in a separate thread	
								t2 = threading.Thread(target=self.run_dvblast, args=[cmd])
								t2.daemon = True
								t2.start()

					if dvblastReload:
						for frontEnd in frontEndsDict:
							if frontEndsDict[frontEnd]['owner'] == self.clientInfo['addr_IP']:
								cmd = 'dvblastctl -r /tmp/dvblast' + frontEndsDict[frontEnd]['freq'] + frontEnd + '.sock shutdown'
								print "ABOUT TO DO: ", cmd
								os.system(cmd)
								# os.SystemExittem(cmd)
								cmd = 'dvblast -a ' + frontEnd[-1] + ' -c dvb-t/pid' + chList[clientsDict[self.clientInfo['addr_IP']]['freq']][0] + frontEnd + '.cfg -f ' + chList[clientsDict[self.clientInfo['addr_IP']]['freq']][0] + ' -b 8 -C -u -r /tmp/dvblast' + chList[clientsDict[self.clientInfo['addr_IP']]['freq']][0] + frontEnd + '.sock'
								dvblastReload = 0
								frontEndsDict[frontEnd]['freq'] = chList[clientsDict[self.clientInfo['addr_IP']]['freq']][0]
								frontEndsDict[frontEnd]['owner'] = self.clientInfo['addr_IP']
								# Start dvblast in a separate thread
								t3 = threading.Thread(target=self.run_dvblast, args=[cmd])
								t3.daemon = True
								t3.start()

				# Remove corresponding pid from config file and reload for sat>ip app
				if clientsDict[self.clientInfo['addr_IP']]['stream'] and delPids and delPid:
					try:
						f = open('dvb-t/pid' + chList[clientsDict[self.clientInfo['addr_IP']]['freq']][0] + 'adapter0' +  '.cfg', 'r')
						lines = f.readlines()
						f.close()
						f = open('dvb-t/pid' + chList[clientsDict[self.clientInfo['addr_IP']]['freq']][0] + 'adapter0' +  '.cfg', 'w')
						lineToCompare = self.clientInfo['addr_IP']

						for line in lines:
							print "line ", line
							match_line = re.search(lineToCompare, line)
							print "line to compare ", lineToCompare
							if not match_line:
								f.write(line)
								print 'not match'
							else:
								print 'match'
						f.close()

						cmd = 'dvblastctl -r /tmp/dvblast' + chList[clientsDict[self.clientInfo['addr_IP']]['freq']][0] + 'adapter0' + '.sock reload'
						# print  'about to run: ', cmd
						os.system(cmd)
					except:
						print "processing PLAY DELETE PIDS"
		
		# Process TEARDOWN request
		elif requestType == self.TEARDOWN:
			print "processing TEARDOWN, New State: INI\n"
			# clientsDict[self.clientInfo['addr_IP']]['state'] = self.INI
			session = ''
			try:
				f = open('dvb-t/pid' + chList[clientsDict[self.clientInfo['addr_IP']]['freq']][0] + 'adapter0' +  '.cfg', 'r')
				lines = f.readlines()
				f.close()
				f = open('dvb-t/pid' + chList[clientsDict[self.clientInfo['addr_IP']]['freq']][0] + 'adapter0' +  '.cfg', 'w')
				lineToCompare = self.clientInfo['addr_IP']

				for line in lines:
					print "line ", line
					match_line = re.search(lineToCompare, line)
					print "line to compare ", lineToCompare
					if not match_line:
						f.write(line)
						print 'not match'
					else:
						print 'match'
				f.close()

				cmd = 'dvblastctl -r /tmp/dvblast' + chList[clientsDict[self.clientInfo['addr_IP']]['freq']][0] + 'adapter0' + '.sock reload'
				# print  'about to run: ', cmd
				os.system(cmd)
			except:
				print "processing TEARDOWN NONE"
			del clientsDict[self.clientInfo['addr_IP']]
			self.replyRtsp(self.OK_200_TEARDOWN, seq[1])
			
		# Process OPTIONS request 		
		elif requestType == self.OPTIONS:
			print "processing OPTIONS\n"
			self.replyRtsp(self.OK_200_OPTIONS, seq[1])

		# Process DESCRIBE request 		
		elif requestType == self.DESCRIBE:
			# print "SESSION", session
			if session == '':
				print "processing DESCRIBE NONE\n"
				self.replyRtsp(self.OK_404_DESCRIBE, seq[1])
			else:
				print "dvblastReload", dvblastReload
				if dvblastReload:
					print "processing DESCRIBE SIGNAL\n"
					self.replyRtsp(self.OK_200_DESCRIBE, seq[1])
				else:
					print "processing DESCRIBE NO SIGNAL\n"
					self.replyRtsp(self.OK_200_DESCRIBE_NOSIGNAL, seq[1])



		# Process CLOSE_CONNETION request 		
		elif requestType == self.CLOSE_CONNETION:
			# print "processing CLOSE_CONNETION\n"
			self.SERVER_RUNNING = 0
			self.replyRtsp(self.CLOSING_CONNECTION, seq[1])

		
	def run_dvblast(self, cmd):
		# print 'ABOUT TO RUN', cmd
		# cmd = 'sudo dvblast -a 0 -c dvb-t/pid666000000adapter0.cfg -f 666000000 -b 8 -C -u -r /tmp/dvblast666000000adapter0.sock'
		print 'ABOUT TO DO: ', cmd
		os.system(cmd)
		# outtext = commands.getoutput(cmd)
		# print "outtext", outtext
		# (exitstatus, outtext) = commands.getstatusoutput(cmd)
		# print "exitstatus", exitstatus
		# if not exitstatus:
			# print "outtext", outtext

	def replyRtsp(self, code, seq):
		"""Send RTSP reply to the client."""
		if code == self.OK_200_OPTIONS:
			reply = 'RTSP/1.0 200 OK\r\nPublic:OPTIONS,SETUP,PLAY,TEARDOWN,DESCRIBE\r\nCSeq:1\r\n\r\n'
			connSocket = self.clientInfo['rtspSocket']# object does not support indexing [0]
			connSocket.send(reply)
			self.SERVER_RUNNING = 0
		
		# Error messages
		elif code == self.FILE_NOT_FOUND_404:
			print "404 NOT FOUND"
		elif code == self.CON_ERR_500:
			print "500 CONNECTION ERROR"
		elif code == self.OK_200_DESCRIBE:
			ipServer = '192.168.2.61'
			unicastIp = '0.0.0.0'
			serverID = 1
			serverTunerNr = 4
			tunerValues = '1,123,1,3,'
			tunerValues2 = ',' + clientsDict[self.clientInfo['addr_IP']]['pol'] + ',' + clientsDict[self.clientInfo['addr_IP']]['msys'] + ',' + clientsDict[self.clientInfo['addr_IP']]['mtype'] + ',' + clientsDict[self.clientInfo['addr_IP']]['plts'] + ',' + clientsDict[self.clientInfo['addr_IP']]['ro'] + ',' + clientsDict[self.clientInfo['addr_IP']]['sr'] + ',' + clientsDict[self.clientInfo['addr_IP']]['fec']
			sdpString = 'v=0\r\no=- 534863118 534863118 IN IP4 %s\ns=SatIPServer:%d %d\r\nt=0 0\r\nm=video 0 RTP/AVP 33\r\nc=IN IP4 %s\na=control:stream=%d\na=fmtp:33 ver=1.0;scr=1;tuner=%s%s.00%s\na=%s\n' % (ipServer, serverID, serverTunerNr, unicastIp, clientsDict[self.clientInfo['addr_IP']]['stream'], tunerValues, clientsDict[self.clientInfo['addr_IP']]['freq'], tunerValues2, clientsDict[self.clientInfo['addr_IP']]['status'])
			sdpLen = len(sdpString)
			rtspString = 'RTSP/1.0 200 OK\r\nContent-length:%d\r\nContent-type:application/sdp\r\nContent-Base:rtsp://192.168.2.61/\r\nCSeq:%s\nSession:c8d13e72c33931f\r\n\r\n' % (sdpLen ,seq)
			
			reply = rtspString + sdpString

			connSocket = self.clientInfo['rtspSocket']
			connSocket.send(reply)
			self.SERVER_RUNNING = 0
		elif code == self.OK_200_DESCRIBE_NOSIGNAL:
			ipServer = '192.168.2.61'
			unicastIp = '0.0.0.0'
			serverID = 1
			serverTunerNr = 4
			tunerValues = '1,0,0,0,'
			tunerValues2 = ',' + clientsDict[self.clientInfo['addr_IP']]['pol'] + ',' + clientsDict[self.clientInfo['addr_IP']]['msys'] + ',' + clientsDict[self.clientInfo['addr_IP']]['mtype'] + ',' + clientsDict[self.clientInfo['addr_IP']]['plts'] + ',' + clientsDict[self.clientInfo['addr_IP']]['ro'] + ',' + clientsDict[self.clientInfo['addr_IP']]['sr'] + ',' + clientsDict[self.clientInfo['addr_IP']]['fec']
			sdpString = 'v=0\r\no=- 534863118 534863118 IN IP4 %s\ns=SatIPServer:%d %d\r\nt=0 0\r\nm=video 0 RTP/AVP 33\r\nc=IN IP4 %s\na=control:stream=%d\na=fmtp:33 ver=1.0;scr=1;tuner=%s%s.00%s\na=%s\n' % (ipServer, serverID, serverTunerNr, unicastIp, clientsDict[self.clientInfo['addr_IP']]['stream'], tunerValues, clientsDict[self.clientInfo['addr_IP']]['freq'], tunerValues2, clientsDict[self.clientInfo['addr_IP']]['status'])
			sdpLen = len(sdpString)
			rtspString = 'RTSP/1.0 200 OK\r\nContent-length:%d\r\nContent-type:application/sdp\r\nContent-Base:rtsp://192.168.2.61/\r\nCSeq:%s\nSession:c8d13e72c33931f\r\n\r\n' % (sdpLen ,seq)
			
			reply = rtspString + sdpString

			connSocket = self.clientInfo['rtspSocket']
			connSocket.send(reply)
			self.SERVER_RUNNING = 0
		elif code == self.OK_404_DESCRIBE:
			reply = 'RTSP/1.0 404 Not Found\r\nCSeq:%s\n\r\n' % (seq)
			connSocket = self.clientInfo['rtspSocket']
			connSocket.send(reply)
			self.SERVER_RUNNING = 0
		elif code == self.OK_200_SETUP:
			reply = 'RTSP/1.0 200 OK\r\nSession:c8d13e72c33931f;timeout=30\r\ncom.ses.streamID:%d\r\nTransport: RTP/AVP;unicast;destination=%s;client_port=5000-5001\r\nCSeq:%s\n\r\n' % (clientsDict[self.clientInfo['addr_IP']]['stream'], self.clientInfo['addr_IP'], seq)
			connSocket = self.clientInfo['rtspSocket']
			connSocket.send(reply)
			self.SERVER_RUNNING = 0
		elif code == self.OK_200_SETUP_PIDS:
			reply = 'RTSP/1.0 200 OK\r\nSession:c8d13e72c33931f;timeout=30\r\ncom.ses.streamID:%d\r\nTransport: RTP/AVP;unicast;destination=%s;client_port=5000-5001\r\nCSeq:%s\r\n\r\n' % (clientsDict[self.clientInfo['addr_IP']]['stream'], self.clientInfo['addr_IP'], seq)
			connSocket = self.clientInfo['rtspSocket']
			connSocket.send(reply)
			self.SERVER_RUNNING = 1
		elif code == self.OK_200_PLAY:
			reply = 'RTSP/1.0 200 OK\r\nRTP-Info:url=//192.168.2.61/stream=%d;seq=50230\r\nCSeq:%s\nSession:c8d13e72c33931f\r\n\r\n' % (clientsDict[self.clientInfo['addr_IP']]['stream'], seq)
			connSocket = self.clientInfo['rtspSocket']
			connSocket.send(reply)
			self.SERVER_RUNNING = 0
		elif code == self.OK_200_TEARDOWN:
			reply = 'RTSP/1.0 200 OK\r\nContent-length:0\r\nCSeq:%s\nSession:c8d13e72c33931f\r\n\r\n' % (seq)
			connSocket = self.clientInfo['rtspSocket']
			connSocket.send(reply)
			self.SERVER_RUNNING = 0			