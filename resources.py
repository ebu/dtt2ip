#!/usr/bin/python

import commands, re

def getFrontEnds():
	# Initialize frontEnd dictionary 
	frontEndDict = {}

	# List the available adapters
	cmd = 'ls -l /dev/dvb/'
	print 'about to do this: ', cmd
	outtext = commands.getoutput(cmd)
	(exitstatus, outtext) = commands.getstatusoutput(cmd)
	if not exitstatus:
		linesArray = outtext.split('\n')
		for line in linesArray:
			matchAdapter = re.search(r'adapter([\w]+)', line)
			if matchAdapter:
				adapter = 'adapter' + matchAdapter.group(1)
				frontEndDict[adapter] = {}
				frontEndDict[adapter]['owner'] = '0.0.0.0'
				frontEndDict[adapter]['freq'] = ''
		print 'Info: available adapters detected'
	# print frontEndDict
	else:
		print 'Info: NO AVAILABLE adapters detected'
	return frontEndDict
	
if __name__ == '__main__':
	getFrontEnds()