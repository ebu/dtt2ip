#!/usr/bin/python

import commands, re, os.path
global numIter
global totalNumOfLines
global valTimer
global valTimerCheck

# Initialize global variables
numIter = 0
totalNumOfLines = 0
valTimer = 3
valTimerCheck = 4

def getChList():
	# Open that scaning.log file
	fLog = open('logs/scanning.log', 'w')

	# Get chList 
	chList = {}
	f = open('conf/rtspServer2.config', 'r')
	lines = f.readlines()
	for i in range(5, len(lines)):
		line = lines[i]
		lineArray = line.split(' ')
		if lineArray[0] != '#':
			chList[lineArray[0]] = lineArray[1:-1]
	f.close()
	fLog.write('Info: Available channels obtained\n')
	fLog.close()
	return chList

def scanning(periodNewScan):
	global numIter
	global totalNumOfLines

	# Increment number of iteration for scanning
	numIter = numIter + 1
	# Statically asigned frequencies from 19.2 degrees E satelite
	# First value signifies that freq is free "0" or occupied "1"
	# Second value signifies the timer that the freq is still available. 
	# Starts from valTimer and gets decremented everytime and gets incremented mod valTimer 
	# if freq is found on polls different from valTimerCheck, except the first time.
	# If timer gets to "0", then remove that frequency from the rtspServer2.config file and
	# make the corresponding satFreq available and reinitialize valTimer.
	satFreq = { '10729':[0,valTimer], '10743':[0,valTimer], '10773':[0,valTimer], '10788':[0,valTimer], '10818':[0,valTimer], '10832':[0,valTimer], 
				'10847':[0,valTimer], '10862':[0,valTimer], '10876':[0,valTimer], '10979':[0,valTimer], '11023':[0,valTimer], '11038':[0,valTimer], 
				'11097':[0,valTimer], '11156':[0,valTimer], '11171':[0,valTimer], '11303':[0,valTimer], '11318':[0,valTimer], '11362':[0,valTimer], 
				'11436':[0,valTimer], '11464':[0,valTimer], '11479':[0,valTimer], '11509':[0,valTimer], '11538':[0,valTimer], '11568':[0,valTimer], 
				'11597':[0,valTimer], '11627':[0,valTimer], '11671':[0,valTimer], '11686':[0,valTimer], '11720':[0,valTimer], '11739':[0,valTimer],
				'11758':[0,valTimer], '11778':[0,valTimer], '11798':[0,valTimer], '11817':[0,valTimer], '11836':[0,valTimer], '11856':[0,valTimer], 
				'11876':[0,valTimer], '11895':[0,valTimer], '11914':[0,valTimer], '11934':[0,valTimer], '11954':[0,valTimer], '11973':[0,valTimer], 
				'11992':[0,valTimer], '12012':[0,valTimer], '12032':[0,valTimer], '12051':[0,valTimer], '12070':[0,valTimer], '12090':[0,valTimer], 
				'12110':[0,valTimer], '12129':[0,valTimer], '12148':[0,valTimer], '12168':[0,valTimer], '12188':[0,valTimer], '12207':[0,valTimer], 
				'12226':[0,valTimer], '12246':[0,valTimer], '12266':[0,valTimer], '12285':[0,valTimer], '12304':[0,valTimer], '12324':[0,valTimer],
				'12344':[0,valTimer], '12363':[0,valTimer], '12382':[0,valTimer], '12402':[0,valTimer], '12422':[0,valTimer], '12441':[0,valTimer], 
				'12460':[0,valTimer], '12480':[0,valTimer], '12515':[0,valTimer], '12545':[0,valTimer], '12552':[0,valTimer], '12574':[0,valTimer], 
				'12581':[0,valTimer], '12604':[0,valTimer], '12610':[0,valTimer], '12633':[0,valTimer], '12640':[0,valTimer], '12663':[0,valTimer], 
				'12670':[0,valTimer], '12692':[0,valTimer], '12699':[0,valTimer], '12722':[0,valTimer], '12728':[0,valTimer] }
	numFreq = len(satFreq)

	# Open that scaning.log file
	fLog = open('logs/scanning.log', 'a')
	while scanningFlag:

		# Alex: ---- check if it can adapt it's adapter
		cmd = 'w_scan > dvb-t/allFrequencies.txt'
		# Alex: ---- 
		fLog.write('Info: Scaning all available frequencies from your antenna\n')

		outtext = commands.getoutput(cmd)
		(exitstatus, outtext) = commands.getstatusoutput(cmd)
		if not exitstatus:
			f = open('dvb-t/allFrequencies.txt', 'r')
			lines = f.readlines()
			# Get total number of line, representing all the number of programs found
			totalNumOfLines = totalNumOfLines + len(lines)
			for line in lines:
				# Search for the frequencies available from the scan
				matchFreq = re.search(r':([\w]+)', line)
				if matchFreq:
					freq = matchFreq.group(1) + '000'
				line = line[::-1]
				# Search for the PID's corresponding to the frequencies detected
				matchPid = re.search(r'([\w]+):([\w]+):([\w]+):([\w]+):', line)
				if matchPid:
					pid = matchPid.group(4)[::-1]
				
				# Create all the necesary '.cfg' files
				if not os.path.isfile('pid' + freq + '.cfg'):
					cmd = 'touch dvb-t/pid' + freq + '.cfg' 
					outtext = commands.getoutput(cmd)
					(exitstatus, outtext) = commands.getstatusoutput(cmd)
					if not exitstatus:
						fLog.write('Info: Creating missing pid' + freq + '.cfg file\n')

				# Update the rtspServer2.config file with the new available frequencies
				if numIter == 1:
					fLog.write('Info: Create rtspServer2.config file')
					f = open('conf/rtspServer2.config', 'w')
					f.write('# Please be carefull when editing this file. \n')
					f.write('# The syntax is :\n')
					f.write('# fakeFrequency' 'dvbtFrequency' 'bandwidth' 'modulationType' 'pid' ' (for the moment no bandwith or modulation)\n')
					f.write('# Use "#' '" to comment line\n')
					f.write('\n')
					for currentFreq in sorted(satFreq):
						if satFreq[currentFreq][0] == 0:
							satFreq[currentFreq][0] = 1
							f.write(currentFreq + ' ' + freq + ' ' + pid + ' \n')
							f.close()
							break
					# Alex TO DO -- what if we ran out of available sat freq
				elif:
					chDict = getChList()
					newFreqFlag = True
					for freqPid in chDict.values():
						fLog.write('Info: Check the avalability of our frequencies')
						if freq == frePid[0] and pid == freqPid[1]:
							newFreqFlag = False
							# Increase timer (i.e second value from satFreq) mod valTimer
							satFreq[chDict.keys()[chDict.values().index([freq, pid])]][1] = (satFreq[chDict.keys()[chDict.values().index([freq, pid])]][1] + 1) % valTimer 
							# break
						satFreq[chDict.keys()[chDict.values().index([freq, pid])]][1] = satFreq[chDict.keys()[chDict.values().index([freq, pid])]][1] - 1
					
					if newFreqFlag:
						fLog.write('Info: Update rtspServer2.config with new freq = ' + freq + ' found.')
						for currentFreq in sorted(satFreq):
							if satFreq[currentFreq][0] == 0:
								satFreq[currentFreq][0] = 1
								satFreq[currentFreq][1] = satFreq[currentFreq][1] - 1
								f = open('conf/rtspServer2.config', 'a')
								f.write(currentFreq + ' ' + freq + ' ' + pid + ' \n')
								f.close()
								break
						# Alex TO DO -- what if we ran out of available sat freq

			fLog.write('Info: W_SCAN has finished. All configuration files have been update\n')
		else:
			fLog.write('Info: Something went wrong with W_SCAN')

		if numIter == valTimerCheck:
			fLog.write('Info: clean unavailable frequencies')
			for currentFreq in sorted(satFreq):
			if satFreq[currentFreq][1] == 0:
				f = open('conf/rtspServer2.config', 'r')
				lines = f.readlines()
				f.close()

				f = open('conf/rtspServer2.config', 'w')
				f.write('# Please be carefull when editing this file. \n')
				f.write('# The syntax is :\n')
				f.write('# fakeFrequency' 'dvbtFrequency' 'bandwidth' 'modulationType' 'pid' ' (for the moment no bandwith or modulation)\n')
				f.write('# Use "#' '" to comment line\n')
				f.write('\n')
				for line in lines:
					matchFreq = re.search(currentFreq, line)
					if not matchFreq:
						f.write(line)
				f.close()
		# Check every hour for new frequencies. It can be changed to longer periods from site
		time.sleep(periodNewScan)
		numIter = numIter + 1
	fLog.close()

if __name__ == '__main__':
	# Default period for new scan is 3600 seconds.
	# It can be changed from the site interface
	periodNewScan = 3600
	scanning(periodNewScan)