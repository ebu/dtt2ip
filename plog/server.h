/* server.h for plog 0.1.0
 * Copyright 2011 M. Thomas Eriksen
 * Distributed under the terms of the GNU General Public License, v3
 * http://www.gnu.org/licenses/gpl.html */

#include <sys/types.h>
#include <time.h>
#include <poll.h>
#include <stdint.h>
#include "process.h"
#include "udp.h"

typedef struct {
	struct pollfd self;
	char dir[108];
	char path[108];
	int err;
	plProcess *listHead;
	uint32_t cfg;
} PlogServer;

// flags for PlogServer.cfg bitfield
// (number of max stale tmp sockets is PlogServer.cfg >> 20)
#define PLOG_DEFAULT 1
#define PLOG_ERROUT 1 << 1
#define PLOG_VERBOSE 1 << 2
#define PLOG_SYSLOG 1 << 3
#define PLOG_FG 1 << 4
#define PLOG_PROMISC 1 << 5

// values for PlogServer.err
enum {
	PS_SOCK_FAIL = 1,
	PS_BIND_FAIL,
	PS_POLL_FAIL,
	PS_SOCKETFILE_GONE,
	PS_RELATIVE_SOCKPATH,
	PS_OUT_OF_MEM
};

PlogServer *createServer (const char *sockpath);
void checkServer (PlogServer **srv);
int pingSocket (char *path, PlogServer *srv);
int runServer (PlogServer *srv, void(*takecall)(DataPacket*));
void freeServer (PlogServer *srv);
