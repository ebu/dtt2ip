#!/bin/bash

# You may change these variables if you have installed plog
# in a non-standard location or wish to use a different
# runtime directory
PLOGSRVD_DIR="/var/local/plog"
PLOGSRVD_EXEC="/usr/local/bin/plogsrvd"
PLOGCLNT_EXEC="/usr/local/bin/plog"

start () {
	echo -n "Starting plogsrvd..."
	$PLOGSRVD_EXEC -d $PLOGSRVD_DIR -m any
	rv=$?
	srvPid=`$PLOGCLNT_EXEC -d $PLOGSRVD_DIR -q pid 2> /dev/null`
	case "$rv" in
		0)
			echo "okay, pid $srvPid"
			;;
		2) 
			echo -e "\n\"$PLOGSRVD_DIR\" is too long a path."
			;;
		3)
			echo "could not use $PLOGSRVD_DIR."
			;;
		11)
			echo "could not remove stale socket from $PLOGSRVD_DIR."
			;;
		12)
			echo "already running."
			;;
		*)
			echo "...FAILED (exit code $rv)"
			;;
	esac
	exit $rv
}

stop () {
	srvPid=`$PLOGCLNT_EXEC -d $PLOGSRVD_DIR -q pid 2> /dev/null`
	if [[ $? -ne 0 ]]; then
		echo "Plogsrvd not running or can't be reached."
		exit 1
	fi
	echo -e "Sending plogsrvd SIGQUIT...\n";
	echo $srvPid
	kill -3 $srvPid
	exit $?
}

status () {
	srvPid=`$PLOGCLNT_EXEC -d $PLOGSRVD_DIR -q pid 2> /dev/null`
	case "$?" in
		0)
			echo -e "Plogsrvd running, pid $srvPid\nLogging to: $PLOGSRVD_DIR\n"
			;;
		4)
			echo -e "Plogsrvd not running for $PLOGSRVD_DIR\n"
			;;
		5)
			echo -e "Plogsrvd not running, stale plogd_sock in $PLOGSRVD_DIR\n"
			;;
		6)
			echo -e "Permission denied for $PLOGSRVD_DIR\n"
			;;
		*)
			echo -e "Plog client error #$?\n"
			;;
	esac
	return
}

case "$1" in
	start)
		start
		;;
	stop)
		stop
		;;
	restart)
		stop
		start
		;;
	status)
		status
		;;
	*)
		echo -e "Usage: start|stop|restart|status\n";
		;;
esac

exit $?
