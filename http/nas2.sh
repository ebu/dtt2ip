#!/bin/sh

# Start chroot
echo "Start chroot"
/var/packages/debian-chroot/scripts/start-stop-status start

# Chroot into debian
echo "Chroot to debian..."
/var/packages/debian-chroot/scripts/start-stop-status chroot
#./start-stop-status3 chroot $LOCATION
