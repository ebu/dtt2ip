/* udp.h for plog 0.1.0
 * Copyright 2011 M. Thomas Eriksen
 * Distributed under the terms of the GNU General Public License, v3
 * http://www.gnu.org/licenses/gpl.html */

#include <sys/un.h>

#define PLOG_VERSION "0.1.0"

/* plog uses local UDP sockets, so the full pathname to the socket
 * is required for communication and must be < 108 bytes total */
#define PLOG_RDIR_MAX 96
#define PLOGSRV_SOCK_NAME "plogd_sock"
#define	PLOGSRV_LISTDONE "0000"
#define PLOG_MAX_PAYLOAD 1024

#ifndef PLOG_MAX_TMPSOCK
#define PLOG_MAX_TMPSOCK 20
#endif

#ifndef PLOG_TMPSOCK
#define PLOG_TMPSOCK "/tmp/.plog"
#endif

typedef struct {
	void *data;
	int bytes;
	struct sockaddr_un from;
} DataPacket;

DataPacket *getPacket (int sock);
int sendPacket (void *msg, int len, int sock, char *path);
void freePacket (DataPacket **pkt);
int getTmpSock (char *filename, int maxsocks);

/* About "plogd protocol":
 * DataPacket.data is usually just two ints:
 * #1 is either a pid or 0 to indicate a special request
 * if #1 is non-zero, then #2 is an interval in minutes 
 * otherwise, #2 indicates the type of special request:
 *		1: list of active log files
 *		2: pid
 *		3: runtime directory
 * Qv. main.c takecall() */
