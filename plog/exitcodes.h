/* exitcodes.h for plog 0.1.0
 * Copyright 2011 M. Thomas Eriksen
 * Distributed under the terms of the GNU General Public License, v3
 * http://www.gnu.org/licenses/gpl.html */

enum {
	XIT_USAGE = 1,				//  1 invalid command line parameters
	XIT_RTDIR_PATH_TOOLONG,		//  2 -d path exceeds PLOG_RTDIR_MAX (qv. main.c)
	XIT_CHDIR_FAIL,				//  3 could not cd to runtime directory
	XIT_FORK_FAILED,			//  4 could not fork to background
	XIT_ABORT_POLL_FAIL,		//  5 poll() failed during operation
	XIT_ABORT_SOCK_GONE,		//  6 local socket file was deleted from runtime directory during operation
	XIT_NO_SERVER,				//  7 server initialization failed (insufficient memory)
	XIT_SOCK_FAIL,				//  8 socket() failed during initialization
	XIT_BIND_FAIL,				//  9 bind() failed during initialization
	XIT_LISTEN_FAIL,			// 10 listen() failed during initialization
	XIT_STUBBORN_SOCKET,		// 11 stale local socket file could not be removed from runtime directory
	XIT_SOCK_INUSE,				// 12 a running server is using the runtime socket
	XIT_NOMEM,					// 13 out of memory!
	XIT_RELATIVE_SOCKPATH,		// 14 relative path given with -d
	XIT_EXCESSIVE_STALE_SOCKS,	// 15 more than -s plog_socks in /tmp (default 20)
};
