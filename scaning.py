#!/usr/bin/python

import commands, re, os.path

def getChList():
	# Open that scaning.log file
	fLog = open('logs/scaning.log', 'a')

	# Get chList 
	chList = {}
	f = open('conf/rtspServer.config', 'r')
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

def main():
	# Statically asigned frequencies from 19.2 degrees E satelite
	satFreq = { '10729':0, '10743':0, '10773':0, '10788':0, '10818':0, '10832':0, '10847':0, '10862':0, '10876':0, '10979':0, 
				'11023':0, '11038':0, '11097':0, '11156':0, '11171':0, '11303':0, '11318':0, '11362':0, '11436':0, '11464':0,
				'11479':0, '11509':0, '11538':0, '11568':0, '11597':0, '11627':0, '11671':0, '11686':0, '11720':0, '11739':0,
				'11758':0, '11778':0, '11798':0, '11817':0, '11836':0, '11856':0, '11876':0, '11895':0, '11914':0, '11934':0,
				'11954':0, '11973':0, '11992':0, '12012':0, '12032':0, '12051':0 }
	numFreq = len(satFreq)

	# Open that scaning.log file
	fLog = open('logs/scaning.log', 'a')
	# cmd = 'w_scan > allFrequencies.txt'
	# fLog.write('Info: Scaning all available frequencies from your antenna\n')

	# outtext = commands.getoutput(cmd)
	# (exitstatus, outtext) = commands.getstatusoutput(cmd)
	# if not exitstatus:
	f = open('allFrequencies.txt', 'r')
	lines = f.readlines()
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

		# Update the rtspServer.config file with the new available frequencies
		for currentFreq in sorted(satFreq):
			if satFreq[currentFreq] == 0:
				satFreq[currentFreq] = 1
				f = open('../conf/rtspServer2.config', 'a')
				f.write(currentFreq + ' ' + freq + ' ' + pid + ' \n')
				f.close()
				break

	fLog.write('Info: W_SCAN has finished. All configuration files have been update\n')

if __name__ == '__main__':
	main()