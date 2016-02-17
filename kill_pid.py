#!/usr/bin/python 

import commands
def main():
	cmd = "netstat | grep 1900 | grep -v grep | awk '{print $6}' | cut -d / -f 1"
	print "Command to run:", cmd   ## good to debug cmd before actually running it
	(status, output) = commands.getstatusoutput(cmd)
	
	if status:    ## Error case, print the command's output to stderr and exit
		sys.stderr.write(output)
		sys.exit(1)
		print output  ## Otherwise do something with the command's output
		for line in output:
			print "line", line


if __name__ == '__main__':
	main()