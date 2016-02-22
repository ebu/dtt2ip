README for plog v.0.1.0
October 27, 2011

Report bugs, etc:
http://www.cognitivedissonance.ca/cogware/plog

Plog is distributed under the terms of the GNU General Public License, v3.
There should be a copy in this package with the title "LICENCE.txt".

Contents of this file:
1. Installation and Configuration
2. Removing Plog
3. Starting the Plog Server Automatically at Boot Time


1. Installation and Configuration
---------------------------------

Plog does not require any configuration to compile.  However, there are a
number of variables at the beginning of the makefile you may wish to change,
including the base install directory and some hardcoded elements such as the
default runtime directory.  See the makefile comments and the plogsrvd man
page, included in this source package, for more information.  You can view the
man page pre-build/install by entering "man ./plogsrvd.1" in this directory.

To build, just enter:

make

at the command line.  This should create the executables plog and plogsrvd.
You can test them from within this directory if you wish.  To install into the
system, use:

make install

The default install path is /usr/local.  If you wish to use a different directory,
use:

make INSTALL_PATH=/some/path install

Binaries go into $INSTALL_PATH/bin and man pages into $INSTALL_PATH/share/man/man1.
These directories will be created if they do not exist.

"Make install" also creates the runtime directory (by default,
/var/local/plog), and sets permissions on it 1777 (see "IPC MODE" in the
plogsrvd man page).

After installation, you may delete this directory (ie, the one with this
README in it).  However, you may want to keep the source package around in
case you want to uninstall or re-install later.


2. Removing Plog
----------------

You can remove this version of plog (or any sufficiently similar version) by
unpacking the source and entering:

make uninstall

at the command line.  If you changed the "installdir" in the makefile
originally, you should also change it now.  "Make uninstall" does not remove
the runtime directory (/var/local/plog).

If you do not want to use "make uninstall", here is a list of the files
installed by "make install" with their default paths:

/usr/local/bin/plog
/usr/local/bin/plogsrvd
/usr/local/share/man/man1/plog.1
/usr/local/share/man/man1/plogsrvd.1
/var/local/plog (directory)

No other changes are made to the system.


3. Starting the Plog Server Automatically at Boot Time
------------------------------------------------------

If you would like to run a plogsrvd as a system service at start-up,
this is an init script in this source package, "plog-daemon.sh", for
this purpose.  Exactly how you use this depends on your distribution, 
but the easiest way may be to just place the script into /etc/init.d,
and then add this somewhere in your rc.local script (or its equivalent):

/etc/init.d plog-daemon.sh start

This will start a plogsrvd with uid root using the "-m any" switch to
allow any user to make requests.  This should be quite safe as the 
only thing a plogsrvd is capable of is logging process.  

The init script also uses the -d switch to set the runtime directory 
to /var/local/plog (which is the normal default anyway), and full paths
to the executable in /usr/local/bin.  If you have installed plog in 
some other location or wish to use a different runtime directory, make
sure you make the appropriate changes at the top of "plog-daemon.sh".

The init script also includes standard "stop" and "status" functions.
