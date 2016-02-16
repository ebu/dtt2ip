#!/bin/sh

# Instalation Directory
LOCATION=`pwd` 
echo $LOCATION

# Replace start-stop-status script with the one provided
echo "Copy the new start-stop-status script..."
cp start-stop-status /var/packages/debian-chroot/scripts/start-stop-status
#cp start-stop-status start-stop-status3