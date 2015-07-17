#!/usr/bin/python

import commands, re, os.path

def main():
	# Statically asigned frequencies from 19.2 degrees E satelite
	satFreq = { '10729':0, '10743':0, '10773':0, '10788':0, '10818':0, '10832':0, '10847':0, '10862':0, '10876':0, '10979':0, 
				'11023':0, '11038':0, '11097':0, '11156':0, '11171':0, '11303':0, '11318':0, '11362':0, '11436':0, '11464':0,
				'11479':0, '11509':0, '11538':0, '11568':0, '11597':0, '11627':0, '11671':0, '11686':0, '11720':0, '11739':0,
				'11758':0, '11778':0, '11798':0, '11817':0, '11836':0, '11856':0, '11876':0, '11895':0, '11914':0, '11934':0,
				'11954':0, '11973':0, '11992':0, '12012':0, '12032':0, '12051':0 }
	numFreq = len(satFreq)

	# cmd = 'w_scan > allFrequencies.txt'
	# print 'about to do this: ', cmd
	# outtext = commands.getoutput(cmd)
	# (exitstatus, outtext) = commands.getstatusoutput(cmd)
	# if not exitstatus:
	f = open('allFrequencies.txt', 'r')
	lines = f.readlines()
	print lines
	for line in lines:
		# Search for the frequencies available from the scan
		matchFreq = re.search(r':([\w]+)', line)
		if matchFreq:
			freq = matchFreq.group(1) + '000'
			print 'freq', freq
		line = line[::-1]
		# Search for the PID's corresponding to the frequencies detected
		matchPid = re.search(r'([\w]+):([\w]+):([\w]+):([\w]+):', line)
		if matchPid:
			pid = matchPid.group(4)[::-1]
			print 'pid', pid
		
		# Create all the necesary '.cfg' files
		if not os.path.isfile('pid' + freq + '.cfg'):
			cmd = 'touch pid' + freq + '.cfg' 
			print 'about to do this: ', cmd
			outtext = commands.getoutput(cmd)
			(exitstatus, outtext) = commands.getstatusoutput(cmd)
			if not exitstatus:
				print 'Info: Creating missing pid' + freq + '.cfg file'

		for currentFreq in sorted(satFreq):
			if satFreq[currentFreq] == 0:
				satFreq[currentFreq] = 1
				f = open('../conf/rtspServer2.config', 'a')
				f.write(currentFreq + ' ' + freq + ' ' + pid + ' \n')
				f.close()
				break




if __name__ == '__main__':
	main()