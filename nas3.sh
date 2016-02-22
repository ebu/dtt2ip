#!/bin/sh

# Kill the Discovery server from NAS
echo "Killing NAS Discovery server...for later(Python)"
# #pids=`ps -aux | grep -wF 1900 | grep -v grep | awk '{print $2}'`
# pids=`netstat -lptu | grep 1900 | grep -v grep | awk '{print $6}' | cut -d / -f 1 `
# pids=`netstat -lptu | grep 1900 | grep -v grep | awk '{print $6}' | cut -d / -f 1 `
# for i in "${pids[@]}"
# do
  # :
  # echo $i
   # kill -9 ${pids[$i]}
# done
# Update and upgrade
echo "Update the packages..."
apt-get update
apt-get -y --force-yes upgrade

# Install mumudvb dependencie
echo "Install mumudvb dependencie..."
apt-get install -y --force-yes git devscripts pgpgpg debhelper 
apt-get install -y --force-yes autoconf
apt-get install -y --force-yes libproc-processtable-perl

# Clone mumudvb
echo "Clone mumudvb..."
git clone git://github.com/braice/MuMuDVB.git mumudvb

# Changing directory
echo "Changing directory..."
cd mumudvb

# Installing mumudvb
echo "Installing mumudvb...autoreconf"
autoreconf -i -f
echo "Configure..."
./configure
echo "Make..."
make
echo "Make install..."
make install


# Install V4L-DVB Device Drivers
echo "Build, Install V4L-DVB Device Drivers..."
apt-get install -y --force-yes debhelper dh-autoreconf autotools-dev doxygen graphviz libasound2-dev libtool libjpeg-dev libqt4-dev libqt4-opengl-dev libudev-dev libx11-dev pkg-config udev

echo "Getting V4L-DVB..."
cd ../
git clone https://github.com/gjasny/v4l-utils.git
cd v4l-utils
echo "Boostrap..."
./bootstrap.sh
echo "Configure..."
./configure
echo "Make..."
make
echo "Make install..."
make install





