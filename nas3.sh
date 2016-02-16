#!/bin/bash

# Kill the Discovery server from NAS
echo "Killing NAS Discovery server..."
#pids=`ps -aux | grep -wF 1900 | grep -v grep | awk '{print $2}'`
pids=`netstat -lptu | grep 1900 | grep -v grep | awk '{print $6}' | cut -d / -f 1 `
k=0
for ((l=${pids[0]};k<${#pids[@]} && l<=${pids[k]};l++)); do
	((++k))
	echo pids[l]

# Update and upgrade
echo "Update the packages..."
# apt-get update
# apt-get -y --force-yes upgrade

# Install git
# Install mumudvb dependencie
echo "Install mumudvb dependencie..."
# apt-get install git devscripts pgpgpg debhelper 

# Clone mumudvb
echo "Clone mumudvb..."
#git clone git://github.com/braice/MuMuDVB.git mumudvb

# Changing directory
echo "Changing directory..."
# cd mumudvb

# Installing mumudvb
echo "Installing mumudvb...autoreconf"
# autoreconf -i -f
echo "Configure..."
# ./configure
echo "Make..."
# make
echo "Make install..."
# make install

# Other
echo "Other"