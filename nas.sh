#!/bin/sh

# Replace start-stop-status script with the one provided
echo "Copy the new start-stop-status script..."
cp http/start-stop-status /var/packages/debian-chroot/scripts/start-stop-status
#cp start-stop-status start-stop-status3