#!/usr/bin/python

import commands, re

# Make sure that resources.log file is clean
fLog = open('logs/resources.log', 'w')
fLog.close()

def getFrontEnds(frontEndDict):
	# e.g. frontEndDict = {'adapter0': {'owner': '0.0.0.0', 'freq': '', 'numOwners': 0}} 
	# Initialize frontEnd dictionary 
	# frontEndDict = {}
	fLog = open('logs/resources.log', 'a')

	# Update the frontEndDict values (i.e number of owners, owners)
	if frontEndDict:
		for frontEnd in frontEndDict:
			if frontEndDict[frontEnd]['numOwners'] == 0:
				frontEndDict[frontEnd]['owner'] = '0.0.0.0'

	# List the available adapters
	cmd = 'ls -l /dev/dvb/'
	fLog.write('Info: about to do find all available adapters\n')
	outtext = commands.getoutput(cmd)
	(exitstatus, outtext) = commands.getstatusoutput(cmd)
	if not exitstatus:
		linesArray = outtext.split('\n')
		for line in linesArray:
			matchAdapter = re.search(r'adapter([\w]+)', line)
			if matchAdapter:
				adapter = 'adapter' + matchAdapter.group(1)
				if not frontEndDict.has_key(adapter):
					# print "Info resources: new adapter"
					frontEndDict[adapter] = {}
					frontEndDict[adapter]['owner'] = '0.0.0.0'
					frontEndDict[adapter]['freq'] = ''
					frontEndDict[adapter]['numOwners'] = 0
					fLog.write('Info: Available ' + adapter + ' detected\n')
	else:
		frontEndDict = {}
		fLog.write('Info: NO AVAILABLE adapters detected\n')
	fLog.close()
	return frontEndDict
	
if __name__ == '__main__':
	frontEndDict = {}
	frontEndDict = getFrontEnds(frontEndDict)
	print frontEndDict