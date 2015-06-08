#!/usr/bin/python

from random import randint
import sys, traceback, threading, socket, signal, re

global session 
session = ''

class ServerWorker:
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
	state = INI

	OK_200 = 0
	FILE_NOT_FOUND_404 = 1
	CON_ERR_500 = 2
	CLOSING_CONNECTION = 3
	OK_200_DESCRIBE = 4
	OK_200_DESCRIBE_SESSION = 5
	OK_200_SETUP = 6
	OK_200_SETUP_PIDS = 7
	OK_200_PLAY = 8
	OK_200_TEARDOWN = 9

	SERVER_RUNNING = 1
	
	streamID = 23
	

	clientInfo = {}
	
	def __init__(self, clientInfo):
		self.clientInfo = clientInfo
		
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
				print "Data received:\n" + data
				self.processRtspRequest(data)
	
	def processRtspRequest(self, data):
		"""Process RTSP request sent from the client."""
		global session
		pidsFound = 0
		# Get the request type
		request = data.split('\n')
		line1 = request[0].split(' ')
		requestType = line1[0]
		
		# Get the media file name
		filename = line1[1]
		
		# Get the RTSP sequence number 
		for seq_find in request:
			match_seq = re.search(r'CSeq', seq_find)
			match_pids = re.search(r'pids=([\w]+)', seq_find)	
			if match_seq:
				seq = seq_find.split(':')
			if match_pids:
				pids = match_pids.group(1)
				print 'HEllo pids', pids
			else:
				pids = ''


		# Process SETUP request
		if requestType == self.SETUP:
			if self.state == self.INI:
				# Update state
				print "processing SETUP"
				
				try:
					# self.clientInfo['videoStream'] = VideoStream(filename)
					print "New State: READY\n"
					self.state = self.READY
				except IOError:
					self.replyRtsp(self.FILE_NOT_FOUND_404, seq[1])
				
				# Generate a randomized RTSP session ID
				self.clientInfo['session'] = randint(100000, 999999)
				session = 'c8d13e72c33931f'
				print "SESSION", session
				
				# Send RTSP reply
				if pids == 'none' or pids == '':
					print 'HEllo pids 2', pids
					self.replyRtsp(self.OK_200_SETUP, seq[1])
				else:
					self.replyRtsp(self.OK_200_SETUP_PIDS, seq[1])
				
				# Get the RTP/UDP port from the last line
				for seq_find in request:
					match = re.search(r'client_port', seq_find)
					if match:
						seq_find_array = seq_find.split(';')
						self.clientInfo['rtpPort']= seq_find_array[2].split('=')[1].split('-')[0]
						# print "SEQ_CLIENT_PORT", seq_find
						# print "rtpPORT", self.clientInfo['rtpPort'] 

			elif self.state == self.READY:
				# Update parameters
				print "processing SETUP"

				try:
					print "State: READY\n"
					self.state = self.READY
				except IOError:
					self.replyRtsp(self.FILE_NOT_FOUND_404, seq[1])
				
				# Generate a randomized RTSP session ID
				self.clientInfo['session'] = randint(100000, 999999)
				
				# Send RTSP reply
				self.replyRtsp(self.OK_200, seq[1])
				
				# Get the RTP/UDP port from the last line
				self.clientInfo['rtpPort'] = request[2].split(' ')[3]
			elif self.state == self.PLAYING:
				# Update parameters
				print "processing SETUP"

				try:
					print "State: PLAYING\n"
					self.state = self.PLAYING
				except IOError:
					self.replyRtsp(self.FILE_NOT_FOUND_404, seq[1])
				
				# Generate a randomized RTSP session ID
				self.clientInfo['session'] = randint(100000, 999999)
				
				# Send RTSP reply
				self.replyRtsp(self.OK_200, seq[1])
				
				# Get the RTP/UDP port from the last line
				self.clientInfo['rtpPort'] = request[2].split(' ')[3]

		# Process PLAY request 		
		elif requestType == self.PLAY:
			if self.state == self.PLAYING:
				print "processing PLAY"
				self.state = self.PLAYING
				print "State: PLAY\n"
				self.replyRtsp(self.OK_200, seq[1])
				
			if self.state == self.READY:
				print "processing PLAY"
				print "New State: PLAY\n"
				self.state = self.PLAYING
				
				self.replyRtsp(self.OK_200, seq[1])

			print "processing PLAY"	
			# self.state = self.PLAYING
			print "State: PLAY\n"
			self.replyRtsp(self.OK_200_PLAY, seq[1])	
		
		# Process TEARDOWN request
		elif requestType == self.TEARDOWN:
			print "processing TEARDOWN"
			print "New State: INI\n"
			self.state = self.INI
			session = ''

			self.replyRtsp(self.OK_200_TEARDOWN, seq[1])
			
		# Process OPTIONS request 		
		elif requestType == self.OPTIONS:
			print "processing OPTIONS\n"
			
			self.replyRtsp(self.OK_200, seq[1])

		# Process DESCRIBE request 		
		elif requestType == self.DESCRIBE:
			print "SESSION", session
			if session == '':
				print "processing DESCRIBE\n"
				self.replyRtsp(self.OK_200_DESCRIBE, seq[1])
			else:
				print "processing DESCRIBE SESSION\n"
				self.replyRtsp(self.OK_200_DESCRIBE_SESSION, seq[1])

		# Process CLOSE_CONNETION request 		
		elif requestType == self.CLOSE_CONNETION:
			print "processing CLOSE_CONNETION\n"
			self.SERVER_RUNNING = 0
			self.replyRtsp(self.CLOSING_CONNECTION, seq[1])

		
	def signal_handler(signal, frame):
		print('You pressed Ctrl+C!')
		self.SERVER_RUNNING = 0
		# sys.exit(0)

	def replyRtsp(self, code, seq):
		"""Send RTSP reply to the client."""
		print "Code" , code
		if code == self.OK_200:
			#print "200 OK"
			# try:
				# reply = 'RTSP/1.0 200 OK\nCSeq: ' + seq + '\nSession: ' + str(self.clientInfo['session'])
			# except:
			# reply = 'RTSP/1.0 200 OK\nCSeq: ' + seq
			reply = 'RTSP/1.0 200 OK\r\nPublic:OPTIONS,SETUP,PLAY,TEARDOWN,DESCRIBE\r\nCSeq:1\r\n\r\n'
			connSocket = self.clientInfo['rtspSocket']# object does not support indexing [0]
			connSocket.send(reply)
			self.SERVER_RUNNING = 0
		
		# Error messages
		elif code == self.FILE_NOT_FOUND_404:
			print "404 NOT FOUND"
		elif code == self.CON_ERR_500:
			print "500 CONNECTION ERROR"
		elif code == self.OK_200_DESCRIBE_SESSION:
			# reply = 'RTSP/1.0 404 Not Found\r\nCSeq:%s\r\n' % (seq)
			reply = 'RTSP/1.0 200 OK\r\nContent-length:228\r\nContent-type:application/sdp\r\nContent-Base:rtsp://192.168.2.61/\r\nCSeq:%s\r\nSession:c8d13e72c33931f\r\nv=0\r\no=- 534863118 534863118 IN IP4 192.168.2.61\r\ns=SatIPServer:1 4\r\nt=0 0\r\nm=video 0 RTP/AVP 33\r\nc=IN IP4 0.0.0.0\r\na=control:stream=%d\r\na=fmtp:33 ver=1.0;scr=1;tuner=1,0,0,0,12402.00,v,dvbs,qpsk,off,0.35,27500,34\r\na=inactive\r\n\r\n' % (seq,self.streamID)
			# reply = 'RTSP/1.0 200 OK\r\nContent-length:0\r\nContent-type:application/sdp\r\nContent-Base:rtsp://192.168.2.61/\r\nCSeq:%s\r\n\r\n' % (seq)
			connSocket = self.clientInfo['rtspSocket']# object does not support indexing [0]
			connSocket.send(reply)
			self.SERVER_RUNNING = 0
		elif code == self.OK_200_DESCRIBE:
			reply = 'RTSP/1.0 404 Not Found\r\nCSeq:%s\r\n\r\n' % (seq)
			# reply = 'RTSP/1.0 200 OK\r\nContent-length:228\r\nContent-type:application/sdp\r\nContent-Base:rtsp://192.168.2.61/\r\nCSeq:%s\r\nSession:c8d13e72c33931f\r\nv=0\r\no=- 534863118 534863118 IN IP4 192.168.2.61\r\ns=SatIPServer:1 4\r\nt=0 0\r\nm=video 0 RTP/AVP 33\r\nc=IN IP4 0.0.0.0\r\na=control:stream=%d\r\na=fmtp:33 ver=1.0;scr=1;tuner=1,0,0,0,12402.00,v,dvbs,qpsk,off,0.35,27500,34\r\na=inactive\r\n\r\n' % (seq,self.streamID)
			# reply = 'RTSP/1.0 200 OK\r\nContent-length:0\r\nContent-type:application/sdp\r\nContent-Base:rtsp://192.168.2.61/\r\nCSeq:%s\r\n\r\n' % (seq)
			connSocket = self.clientInfo['rtspSocket']# object does not support indexing [0]
			connSocket.send(reply)
			self.SERVER_RUNNING = 0
		elif code == self.OK_200_SETUP:
			reply = 'RTSP/1.0 200 OK\r\nSession:c8d13e72c33931f;timeout=30\r\ncom.ses.streamID:%d\r\nTransport: RTP/AVP;unicast;destination=%s;client_port=5000-5001\r\nCSeq:%s\r\n\r\n' % (self.streamID, self.clientInfo['addr_IP'], seq)
			connSocket = self.clientInfo['rtspSocket']# object does not support indexing [0]
			connSocket.send(reply)
			self.SERVER_RUNNING = 0
		elif code == self.OK_200_SETUP_PIDS:
			reply = 'RTSP/1.0 200 OK\r\nSession:c8d13e72c33931f;timeout=30\r\ncom.ses.streamID:%d\r\nTransport: RTP/AVP;unicast;destination=%s;client_port=5000-5001\r\nCSeq:%s\r\n\r\n' % (self.streamID, self.clientInfo['addr_IP'], seq)
			connSocket = self.clientInfo['rtspSocket']# object does not support indexing [0]
			connSocket.send(reply)
			self.SERVER_RUNNING = 1
		elif code == self.OK_200_PLAY:
			reply = 'RTSP/1.0 200 OK\r\nRTP-Info:url=//192.168.2.61/stream=23;seq=50230\r\nCSeq:%s\r\nSession:c8d13e72c33931f\r\n\r\n' % (seq)
			connSocket = self.clientInfo['rtspSocket']# object does not support indexing [0]
			connSocket.send(reply)
			self.SERVER_RUNNING = 0
		elif code == self.OK_200_TEARDOWN:
			reply = 'RTSP/1.0 200 OK\r\nContent-length:0\r\nCSeq:%s\r\nSession:c8d13e72c33931f\r\n\r\n'
			connSocket = self.clientInfo['rtspSocket']# object does not support indexing [0]
			connSocket.send(reply)
			self.SERVER_RUNNING = 0			

		# Closing connection
		# elif code == self.CLOSING_CONNECTION:
		# 	print "Closing Connetion. Shuting down server."
		# 	connSocket = self.clientInfo['rtspSocket']
		# 	connSocket.close()	
