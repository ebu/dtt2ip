#!/usr/bin/python

import sys, traceback, threading, socket, signal, re, commands, os, time, string, random, uuid
from random import randint
from resources import getFrontEnds
from netInterfaceStatus import getServerIP
from scanning import getChList
from subprocess import Popen, PIPE

global session
global dvblastReload

global clientsDict
global chList
global frontEndsDict
global freqDict

global firstBootFlag
global fLog

# Init global variables
clientsDict = {}	# e.g. clientsDict = { 'ip_client_1': {'rtpPort': '', state: 0, 'satFreq': '', stream: 0, 'src': '', 'pol': '', 'ro': '', 'msys': '', 'mtype': '', 'plts': '', 'sr': '', 'fec': '', 'status': 'sendonly', 'owner': True, 'session': '' }}
freqDict = {}		# e.g. freqDict = {'freq': 'adapter0'}
frontEndsDict = {}	# e.g. frontEndsDict = {'adapter0': {'owner': '0.0.0.0', 'freq': '', 'numOwners': 0}} 
chList = {}		# e.g. chList = {'satFreq': ['freq', 'pid']}
session = ''	# For THEARDOWN reply
dvblastReload = 0   # e.g. Flag to trigger a reload
firstBootFlag = True # First bootup of the device


# Get chList 
chList = getChList()

# Make sure that rtspServerWorker.log file is clean
f = open('logs/rtspServerWorker.log', 'w')
f.close()

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
		session = ''

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
			clientsDict[self.clientInfo['addr_IP']]['owner'] = True
			clientsDict[self.clientInfo['addr_IP']]['session'] = session			
	
	def run(self):		
		t = threading.Thread(target=self.recvRtspRequest)
		t.daemon = True
		t.start()

		try:
			while t.is_alive():
				t.join(timeout=1.0)
		except (KeyboardInterrupt, SystemExit):
			# fLog.close()
			self.SERVER_RUNNING = 0

	
	def recvRtspRequest(self):
		"""Receive RTSP request from the client."""
		connSocket = self.clientInfo['rtspSocket']
		while self.SERVER_RUNNING:            
			data = connSocket.recv(1024)
			if data:
				self.processRtspRequest(data)
	
	def processRtspRequest(self, data):
		"""Process RTSP request sent from the client."""
		global session
		global dvblastReload

		global chList	
		global clientsDict  
		global frontEndsDict
		global freqDict

		global firstBootFlag
		global fLog

		# Initialize local variables
		freq = ''
		pids = ''
		delPids = 0
		delPid = 0
		fLog = open('logs/rtspServerWorker.log', 'a')
		
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
				fLog.write("Info rtspServerWorker: Processing SETUP, New State: READY\n") 
				clientsDict[self.clientInfo['addr_IP']]['state'] = self.READY

				# Generate a randomized RTSP session ID
				clientsDict[self.clientInfo['addr_IP']]['session'] = uuid.uuid4().hex[:16]
				# Increment streamID for every new session
				clientsDict[self.clientInfo['addr_IP']]['stream'] = (clientsDict[self.clientInfo['addr_IP']]['stream'] + 1) % 65536
	
				# Send RTSP reply
				if freq in chList:
					f = open('dvb-t/pid' + chList[freq][0] + '.cfg', 'a')
					f.write(self.clientInfo['addr_IP'] + ':' + clientsDict[self.clientInfo['addr_IP']]['rtpPort'] + '\t1\t' + chList[freq][1] + '\n')
					f.close()
					dvblastReload = 1

				if pids == 'none' or pids == '':
					self.replyRtsp(self.OK_200_SETUP, seq[1])
					if pids == 'none':
						clientsDict[self.clientInfo['addr_IP']]['status'] = 'inactive'
				else:
					self.replyRtsp(self.OK_200_SETUP_PIDS, seq[1])

			# Process SETUP request If STATE is READY
			elif clientsDict[self.clientInfo['addr_IP']]['state'] == self.READY:
				fLog.write("Info rtspServerWorker: Processing SETUP, State: READY\n") 

				# Send RTSP reply
				self.replyRtsp(self.OK_200_SETUP, seq[1])

			# Process SETUP request If STATE is PLAYING
			elif clientsDict[self.clientInfo['addr_IP']]['state'] == self.PLAYING:
				fLog.write("Info rtspServerWorker: Processing SETUP, State: PLAYING\n")
				
				if freq in chList:
					f = open('dvb-t/pid' + chList[freq][0] + '.cfg', 'r')
					lines = f.readlines()
					f.close()

					f = open('dvb-t/pid' + chList[freq][0] + '.cfg', 'w')
					lineToCompare = self.clientInfo['addr_IP']

					for line in lines:
						match_line = re.search(lineToCompare, line)
						if not match_line:
							f.write(line)
					
					f.write(self.clientInfo['addr_IP'] + ':' + clientsDict[self.clientInfo['addr_IP']]['rtpPort'] + '\t1\t' + chList[freq][1] + '\n')
					f.close()
					dvblastReload = 1
				self.replyRtsp(self.OK_200_SETUP, seq[1])
				
		# Process PLAY request 		
		elif requestType == self.PLAY:
			# Get available frontends
			frontEndsDict = getFrontEnds(frontEndsDict)
			if clientsDict[self.clientInfo['addr_IP']]['state'] == self.PLAYING or clientsDict[self.clientInfo['addr_IP']]['state'] == self.READY: 
				# Send response after processing and starting dvblast
				if clientsDict[self.clientInfo['addr_IP']]['state'] == self.READY:
					fLog.write("Info rtspServerWorker: Processing PLAY, New State: PLAYING\n")
					clientsDict[self.clientInfo['addr_IP']]['state'] = self.PLAYING
				else:
					# print "Info rtspServerWorker: Processing PLAY, State: PLAYING\n"
					fLog.write("Info rtspServerWorker: Processing PLAY, State: PLAYING\n")
				self.replyRtsp(self.OK_200_PLAY, seq[1])

				# START/RELOAD configuration for dvblast only if we have a streamID, the configuration file has been update and the PLAY URI is not a delete pid
				if clientsDict[self.clientInfo['addr_IP']]['stream'] and dvblastReload and delPids == 0:				
					# If firstBootFlag is true this means that no frontend has been configured, so stop wasting time with searching for particular frontends
					if firstBootFlag:
						firstBootFlag = False
						for frontEnd in frontEndsDict:
							if frontEndsDict[frontEnd]['freq'] == '':
								# Start dvblast on specified freq
								print 'ALEX --- 1'
								cmd = 'dvblast -a ' + frontEnd[-1] + ' -c dvb-t/pid' + chList[clientsDict[self.clientInfo['addr_IP']]['freq']][0] + '.cfg -f ' + chList[clientsDict[self.clientInfo['addr_IP']]['freq']][0] + ' -b 8 -C -u -r /tmp/dvblast' + chList[clientsDict[self.clientInfo['addr_IP']]['freq']][0] + frontEnd + '.sock'
								fLog.write('Info rtspServerWorker: Starting dvblast 1\n')
								self.run_dvblast(cmd)
								dvblastReload = 0

								frontEndsDict[frontEnd]['freq'] = chList[clientsDict[self.clientInfo['addr_IP']]['freq']][0]
								frontEndsDict[frontEnd]['owner'] = self.clientInfo['addr_IP']
								frontEndsDict[frontEnd]['numOwners'] = frontEndsDict[frontEnd]['numOwners'] + 1	# increase the number of owners
								freqDict[frontEndsDict[frontEnd]['freq']] = frontEnd
								clientsDict[self.clientInfo['addr_IP']]['owner'] = True
								print 'ALEX --- 2'
								print " frontEndsDict0", frontEndsDict
								break
					# No more first boot, the search for available and preconfigured/unconfigured frontends
					else:
						print " frontEndsDict1", frontEndsDict
						# Search for any configured tuner with the frequency that we want to tune to
						for frontEnd in frontEndsDict:
							if frontEndsDict[frontEnd]['freq'] == chList[clientsDict[self.clientInfo['addr_IP']]['freq']][0]:
								print 'ALEX --- 3'
								cmd = 'dvblastctl -r /tmp/dvblast' + chList[clientsDict[self.clientInfo['addr_IP']]['freq']][0] + frontEnd + '.sock reload'
								fLog.write('Info rtspServerWorker: Reloading dvblast configuration 1\n')
								os.system(cmd)
								dvblastReload = 0

								# Check if this was an abandoned tuner ('0.0.0.0' abandonded IP address) and take ownership if it was
								if frontEndsDict[frontEnd]['owner'] == '0.0.0.0':
									frontEndsDict[frontEnd]['owner'] = self.clientInfo['addr_IP']
									frontEndsDict[frontEnd]['numOwners'] = frontEndsDict[frontEnd]['numOwners'] + 1	# increase the number of owner
									clientsDict[self.clientInfo['addr_IP']]['owner'] = True
								# Check if multiple owners ('255.255.255.255' broadcast IP address) and increase the number of owners by one
								if frontEndsDict[frontEnd]['owner'] == '255.255.255.255' and clientsDict[self.clientInfo['addr_IP']]['owner']:
									frontEndsDict[frontEnd]['numOwners'] = frontEndsDict[frontEnd]['numOwners'] + 1	# increase the number of owner
									clientsDict[self.clientInfo['addr_IP']]['owner'] = False	# remove the ownership capability from the client
								# Check if somebody else owne's it, then make the tuner for multiple owners, increase the number of owners and remove your ownership capabilities
								elif frontEndsDict[frontEnd]['owner'] != self.clientInfo['addr_IP'] and clientsDict[self.clientInfo['addr_IP']]['owner']:
									clientsDict[frontEndsDict[frontEnd]['owner']]['owner'] = False # Remove the ownership capabilities of the previous owner
									frontEndsDict[frontEnd]['owner'] = '255.255.255.255'  # '255.255.255.255' the IP address for specifying multiple owners
									frontEndsDict[frontEnd]['numOwners'] = frontEndsDict[frontEnd]['numOwners'] + 1	# increase the number of owner
									clientsDict[self.clientInfo['addr_IP']]['owner'] = False # Remove the ownership capabilties of yourself
								print 'ALEX --- 4'
								print " frontEndsDict2", frontEndsDict
								break
						# If we did not find any tuner that has that frequency configured,then search for any owned tuners
						if dvblastReload:
							for frontEnd in frontEndsDict:
								if frontEndsDict[frontEnd]['owner'] == self.clientInfo['addr_IP'] or frontEndsDict[frontEnd]['owner'] == '0.0.0.0':
									# Shutdown socket 
									print 'ALEX --- 5'
									cmd = 'dvblastctl -r /tmp/dvblast' + frontEndsDict[frontEnd]['freq'] + frontEnd + '.sock shutdown'
									fLog.write("Info rtspServerWorker: Reloading dvblast configuration 2\n")
									os.system(cmd)
									print 'ALEX --- 6'
									# ALEX : ----- To be checked 
									time.sleep(1)
									# Alex : -----

									# Clean dvblast sockets before creating any other
									print 'ALEX --- 7'
									try:
										cmdClean = 'rm -rf /tmp/dvblast' + frontEndsDict[frontEnd]['freq'] + frontEnd + '.sock'
										fLog.write("Info rtspServerWorker: Cleaning dvblast sockets, before restarting\n")
										os.system(cmdClean)
									except:
										fLog.write("Info rtspServerWorker: No Cleaning for dvblast sockets, before restarting\n")
									print 'ALEX --- 8'
									
									# Start dvblast on specified freq
									cmd = 'dvblast -a ' + frontEnd[-1] + ' -c dvb-t/pid' + chList[clientsDict[self.clientInfo['addr_IP']]['freq']][0] + '.cfg -f ' + chList[clientsDict[self.clientInfo['addr_IP']]['freq']][0] + ' -b 8 -C -u -r /tmp/dvblast' + chList[clientsDict[self.clientInfo['addr_IP']]['freq']][0] + frontEnd + '.sock'
									fLog.write('Info rtspServerWorker: Starting dvblast 2\n')
									self.run_dvblast(cmd)
									dvblastReload = 0
									
									# Assume ownership
									if frontEndsDict[frontEnd]['owner'] == '0.0.0.0':
										frontEndsDict[frontEnd]['owner'] = self.clientInfo['addr_IP']
										frontEndsDict[frontEnd]['numOwners'] = frontEndsDict[frontEnd]['numOwners'] + 1	# increase the number of owners
									frontEndsDict[frontEnd]['freq'] = chList[clientsDict[self.clientInfo['addr_IP']]['freq']][0]	
									freqDict[frontEndsDict[frontEnd]['freq']] = frontEnd
									clientsDict[self.clientInfo['addr_IP']]['owner'] = True
									print 'ALEX --- 9'
									print " frontEndsDict3", frontEndsDict
									break
						# If we did not fine any owned tuners, then give it one more search before giving up. Search for nonused available tuners. 
						if dvblastReload:
							for frontEnd in frontEndsDict:
								if frontEndsDict[frontEnd]['freq'] == '':
									# Start dvblast on specified freq
									print 'ALEX --- 10'
									cmd = 'dvblast -a ' + frontEnd[-1] + ' -c dvb-t/pid' + chList[clientsDict[self.clientInfo['addr_IP']]['freq']][0] + '.cfg -f ' + chList[clientsDict[self.clientInfo['addr_IP']]['freq']][0] + ' -b 8 -C -u -r /tmp/dvblast' + chList[clientsDict[self.clientInfo['addr_IP']]['freq']][0] + frontEnd + '.sock'
									dvblastReload = 0
									fLog.write('Info rtspServerWorker: Starting dvblast 3\n')
									self.run_dvblast(cmd)

									frontEndsDict[frontEnd]['freq'] = chList[clientsDict[self.clientInfo['addr_IP']]['freq']][0]
									frontEndsDict[frontEnd]['owner'] = self.clientInfo['addr_IP']
									frontEndsDict[frontEnd]['numOwners'] = frontEndsDict[frontEnd]['numOwners'] + 1	# increase the number of owner
									freqDict[frontEndsDict[frontEnd]['freq']] = frontEnd
									clientsDict[self.clientInfo['addr_IP']]['owner'] = True	
									print 'ALEX --- 11'
									print " frontEndsDict4", frontEndsDict
									break

				# Remove corresponding pid from config file and reload for sat>ip app
				if clientsDict[self.clientInfo['addr_IP']]['stream'] and delPids and delPid:
					try:
						f = open('dvb-t/pid' + chList[clientsDict[self.clientInfo['addr_IP']]['freq']][0] + '.cfg', 'r')
						lines = f.readlines()
						f.close()
						f = open('dvb-t/pid' + chList[clientsDict[self.clientInfo['addr_IP']]['freq']][0] + '.cfg', 'w')
						lineToCompare = self.clientInfo['addr_IP']

						for line in lines:
							match_line = re.search(lineToCompare, line)
							if not match_line:
								f.write(line)
						f.close()

						print 'ALEX --- 12'
						cmd = 'dvblastctl -r /tmp/dvblast' + chList[clientsDict[self.clientInfo['addr_IP']]['freq']][0] + freqDict[chList[clientsDict[self.clientInfo['addr_IP']]['freq']][0]] + '.sock reload'
						fLog.write('Info rtspServerWorker: Reloading dvblast configuration 3\n')
						os.system(cmd)
						print 'ALEX --- 13'
						print " frontEndsDict5", frontEndsDict
					except:
						print "Info rtspServerWorker: Processing PLAY DELETE PIDS\n"
						fLog.write("Info rtspServerWorker: Processing PLAY DELETE PIDS\n")
		
		# Process TEARDOWN request
		elif requestType == self.TEARDOWN:
			global session

			fLog.write("Info rtspServerWorker: Processing TEARDOWN, New State: INI\n")
			try:
				f = open('dvb-t/pid' + chList[clientsDict[self.clientInfo['addr_IP']]['freq']][0] + '.cfg', 'r')
				lines = f.readlines()
				f.close()
				f = open('dvb-t/pid' + chList[clientsDict[self.clientInfo['addr_IP']]['freq']][0] + '.cfg', 'w')
				lineToCompare = self.clientInfo['addr_IP']

				for line in lines:
					match_line = re.search(lineToCompare, line)
					if not match_line:
						f.write(line)
				f.close()

				cmd = 'dvblastctl -r /tmp/dvblast' + chList[clientsDict[self.clientInfo['addr_IP']]['freq']][0] + freqDict[chList[clientsDict[self.clientInfo['addr_IP']]['freq']][0]] + '.sock reload'
				fLog.write('Info rtspServerWorker: Reloading dvblast configuration 4\n')
				os.system(cmd)
			except:
				# print "Info rtspServerWorker: processing TEARDOWN NONE\n"
				print " frontEndsDict7", frontEndsDict
				fLog.write("Info rtspServerWorker: processing TEARDOWN NONE\n")

			try:
				# Update the number of owners of frontEnd
				frontEndsDict[freqDict[chList[clientsDict[self.clientInfo['addr_IP']]['freq']][0]]]['numOwners'] = frontEndsDict[freqDict[chList[clientsDict[self.clientInfo['addr_IP']]['freq']][0]]]['numOwners'] - 1
			except:
				print "Info rtspServerWorker: No adapters configured 1 "
			try:
				# If new have only one client connected left, then the last client takes the ownership of the tuner 
				if frontEndsDict[freqDict[chList[clientsDict[self.clientInfo['addr_IP']]['freq']][0]]]['numOwners'] == 1:
					if clientsDict.keys()[0] == self.clientInfo['addr_IP']:
						frontEndsDict[freqDict[chList[clientsDict[self.clientInfo['addr_IP']]['freq']][0]]]['owner'] = clientsDict.keys()[1] # The last client that will remain in the clientsDict has to take ownership
					else:
						frontEndsDict[freqDict[chList[clientsDict[self.clientInfo['addr_IP']]['freq']][0]]]['owner'] = clientsDict.keys()[0] # The last client that will remain in the clientsDict has to take ownership
				print " frontEndsDict6", frontEndsDict
			except:
				print "Info rtspServerWorker: No adapters configured 2 "
			# Get the session value before deleting the client entry
			session = clientsDict[self.clientInfo['addr_IP']]['session']
			# Remove client from dictinary
			del clientsDict[self.clientInfo['addr_IP']]
			self.replyRtsp(self.OK_200_TEARDOWN, seq[1])
			
		# Process OPTIONS request 		
		elif requestType == self.OPTIONS:
			fLog.write("Info rtspServerWorker: Processing OPTIONS\n")
			self.replyRtsp(self.OK_200_OPTIONS, seq[1])

		# Process DESCRIBE request 		
		elif requestType == self.DESCRIBE:
			if clientsDict[self.clientInfo['addr_IP']]['session'] == '':
				fLog.write("Info rtspServerWorker: Processing DESCRIBE NONE\n")
				self.replyRtsp(self.OK_404_DESCRIBE, seq[1])
			else:
				if dvblastReload:
					fLog.write("Info rtspServerWorker: Processing DESCRIBE SIGNAL\n")
					self.replyRtsp(self.OK_200_DESCRIBE, seq[1])
				else:
					fLog.write("Info rtspServerWorker: Processing DESCRIBE NO SIGNAL\n")
					self.replyRtsp(self.OK_200_DESCRIBE_NOSIGNAL, seq[1])

		# Process CLOSE_CONNETION request 		
		elif requestType == self.CLOSE_CONNETION:
			fLog.write("Info rtspServerWorker: Processing CLOSE_CONNETION\n")
			self.SERVER_RUNNING = 0
			self.replyRtsp(self.CLOSING_CONNECTION, seq[1])

		fLog.close()

	def run_dvblast(self, cmd):
		global fLog
		proc = Popen([cmd], stdout=fLog, stderr=fLog, shell=True)

	def updateChList():
		global chList
		# Get chList 
		chList = getChList()
		
	def replyRtsp(self, code, seq):
		"""Send RTSP reply to the client."""
		global session
		global fLog

		if code == self.OK_200_OPTIONS:
			reply = 'RTSP/1.0 200 OK\r\nPublic:OPTIONS,SETUP,PLAY,TEARDOWN,DESCRIBE\r\nCSeq:1\r\n\r\n'
			connSocket = self.clientInfo['rtspSocket']
			connSocket.send(reply)
			self.SERVER_RUNNING = 0
		
		# Error messages
		elif code == self.FILE_NOT_FOUND_404:
			print "Info rtspServerWorker: 404 NOT FOUND\n"
			fLog.write("Info rtspServerWorker: 404 NOT FOUND\n")
		elif code == self.CON_ERR_500:
			print "Info rtspServerWorker: 500 CONNECTION ERROR\n"
			fLog.write("Info rtspServerWorker: 500 CONNECTION ERROR\n")
		elif code == self.OK_200_DESCRIBE:
			ipServer = getServerIP()
			unicastIp = '0.0.0.0'
			serverID = 1
			serverTunerNr = len(frontEndsDict)
			tunerValues = '1,123,1,3,'
			tunerValues2 = ',' + clientsDict[self.clientInfo['addr_IP']]['pol'] + ',' + clientsDict[self.clientInfo['addr_IP']]['msys'] + ',' + clientsDict[self.clientInfo['addr_IP']]['mtype'] + ',' + clientsDict[self.clientInfo['addr_IP']]['plts'] + ',' + clientsDict[self.clientInfo['addr_IP']]['ro'] + ',' + clientsDict[self.clientInfo['addr_IP']]['sr'] + ',' + clientsDict[self.clientInfo['addr_IP']]['fec']
			sdpString = 'v=0\r\no=- 534863118 534863118 IN IP4 %s\ns=SatIPServer:%d %d\r\nt=0 0\r\nm=video 0 RTP/AVP 33\r\nc=IN IP4 %s\na=control:stream=%d\na=fmtp:33 ver=1.0;scr=1;tuner=%s%s.00%s\na=%s\n' % (ipServer, serverID, serverTunerNr, unicastIp, clientsDict[self.clientInfo['addr_IP']]['stream'], tunerValues, clientsDict[self.clientInfo['addr_IP']]['freq'], tunerValues2, clientsDict[self.clientInfo['addr_IP']]['status'])
			sdpLen = len(sdpString)
			rtspString = 'RTSP/1.0 200 OK\r\nContent-length:%d\r\nContent-type:application/sdp\r\nContent-Base:rtsp://192.168.2.61/\r\nCSeq:%s\nSession:%s\r\n\r\n' % (sdpLen ,seq, clientsDict[self.clientInfo['addr_IP']]['session'])	
			
			# Make the reply from the two parts: rtspString and sdpString
			reply = rtspString + sdpString
			connSocket = self.clientInfo['rtspSocket']
			connSocket.send(reply)
			self.SERVER_RUNNING = 0
			fLog.write("Info rtspServerWorker: 200 DESCRIBE\n")
		elif code == self.OK_200_DESCRIBE_NOSIGNAL:
			ipServer = getServerIP()
			unicastIp = '0.0.0.0'
			serverID = 1
			serverTunerNr = len(frontEndsDict)
			tunerValues = '1,0,0,0,'
			tunerValues2 = ',' + clientsDict[self.clientInfo['addr_IP']]['pol'] + ',' + clientsDict[self.clientInfo['addr_IP']]['msys'] + ',' + clientsDict[self.clientInfo['addr_IP']]['mtype'] + ',' + clientsDict[self.clientInfo['addr_IP']]['plts'] + ',' + clientsDict[self.clientInfo['addr_IP']]['ro'] + ',' + clientsDict[self.clientInfo['addr_IP']]['sr'] + ',' + clientsDict[self.clientInfo['addr_IP']]['fec']
			sdpString = 'v=0\r\no=- 534863118 534863118 IN IP4 %s\ns=SatIPServer:%d %d\r\nt=0 0\r\nm=video 0 RTP/AVP 33\r\nc=IN IP4 %s\na=control:stream=%d\na=fmtp:33 ver=1.0;scr=1;tuner=%s%s.00%s\na=%s\n' % (ipServer, serverID, serverTunerNr, unicastIp, clientsDict[self.clientInfo['addr_IP']]['stream'], tunerValues, clientsDict[self.clientInfo['addr_IP']]['freq'], tunerValues2, clientsDict[self.clientInfo['addr_IP']]['status'])
			sdpLen = len(sdpString)
			rtspString = 'RTSP/1.0 200 OK\r\nContent-length:%d\r\nContent-type:application/sdp\r\nContent-Base:rtsp://192.168.2.61/\r\nCSeq:%s\nSession:%s\r\n\r\n' % (sdpLen ,seq, clientsDict[self.clientInfo['addr_IP']]['session'])
			
			# Make the reply from the two parts: rtspString and sdpString
			reply = rtspString + sdpString
			connSocket = self.clientInfo['rtspSocket']
			connSocket.send(reply)
			fLog.write("Info rtspServerWorker: 200 DESCRIBE NOSIGNAL\n")
			self.SERVER_RUNNING = 0
		elif code == self.OK_404_DESCRIBE:
			reply = 'RTSP/1.0 404 Not Found\r\nCSeq:%s\n\r\n' % (seq)
			connSocket = self.clientInfo['rtspSocket']
			connSocket.send(reply)
			fLog.write("Info rtspServerWorker: 404 DESCRIBE\n")
			self.SERVER_RUNNING = 0
		elif code == self.OK_200_SETUP:
			reply = 'RTSP/1.0 200 OK\r\nSession:%s;timeout=30\r\ncom.ses.streamID:%d\r\nTransport: RTP/AVP;unicast;destination=%s;client_port=5000-5001\r\nCSeq:%s\n\r\n' % (clientsDict[self.clientInfo['addr_IP']]['session'], clientsDict[self.clientInfo['addr_IP']]['stream'], self.clientInfo['addr_IP'], seq)
			connSocket = self.clientInfo['rtspSocket']
			connSocket.send(reply)
			fLog.write("Info rtspServerWorker: 200 SETUP\n")
			self.SERVER_RUNNING = 0
		elif code == self.OK_200_SETUP_PIDS:
			reply = 'RTSP/1.0 200 OK\r\nSession:%s;timeout=30\r\ncom.ses.streamID:%d\r\nTransport: RTP/AVP;unicast;destination=%s;client_port=5000-5001\r\nCSeq:%s\r\n\r\n' % (clientsDict[self.clientInfo['addr_IP']]['session'], clientsDict[self.clientInfo['addr_IP']]['stream'], self.clientInfo['addr_IP'], seq)
			connSocket = self.clientInfo['rtspSocket']
			connSocket.send(reply)
			fLog.write("Info rtspServerWorker: 200 SETUP PID\n")
			self.SERVER_RUNNING = 1
		elif code == self.OK_200_PLAY:
			reply = 'RTSP/1.0 200 OK\r\nRTP-Info:url=//192.168.2.61/stream=%d;seq=50230\r\nCSeq:%s\nSession:%s\r\n\r\n' % (clientsDict[self.clientInfo['addr_IP']]['stream'], seq, clientsDict[self.clientInfo['addr_IP']]['session'])
			connSocket = self.clientInfo['rtspSocket']
			connSocket.send(reply)
			fLog.write("Info rtspServerWorker: 200 PLAY\n")
			self.SERVER_RUNNING = 0
		elif code == self.OK_200_TEARDOWN:
			reply = 'RTSP/1.0 200 OK\r\nContent-length:0\r\nCSeq:%s\nSession:%s\r\n\r\n' % (seq, session)
			connSocket = self.clientInfo['rtspSocket']
			connSocket.send(reply)
			fLog.write("Info rtspServerWorker: 200 TEARDOWN\n")	
			self.SERVER_RUNNING = 0	

