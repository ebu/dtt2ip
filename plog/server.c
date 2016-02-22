/* server.c for plog 0.1.0
 * Copyright 2011 M. Thomas Eriksen
 * Distributed under the terms of the GNU General Public License, v3
 * http://www.gnu.org/licenses/gpl.html */

#include "server.h"
#include "llist.h"
#include <stdlib.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>
#include <sys/select.h>
#include <sys/time.h>
#include <stdarg.h>
#include <errno.h>
#include <stdio.h>
#include "file.h"
#include "exitcodes.h"

#define PLSRV_CYCLE_SECS 30

extern void error (char *msg, ...);
extern char *my_itoa(int n);

PlogServer *createServer (const char *sockpath) {
// validate args
	if (strlen(sockpath) > 107) return NULL;

// allocate object
	PlogServer *rv = malloc(sizeof(PlogServer));
	if (!rv) return NULL;
	rv->err = 0;
	strcpy(rv->path, sockpath);
	char *p = strrchr(sockpath, '/');
	if (p) {
		strncpy(rv->dir, sockpath, p-sockpath);
		rv->dir[p-sockpath] = '\0';
	} else {
		rv->err = PS_RELATIVE_SOCKPATH;
		return rv;
	}
	rv->listHead = NULL;

// socket
	rv->self.fd = socket(PF_LOCAL, SOCK_DGRAM, 0);
	if (rv->self.fd < 3) {
		rv->err = PS_SOCK_FAIL;
		return rv;
	}

// bind
	struct sockaddr_un info;
	info.sun_family = AF_LOCAL;
	strcpy(info.sun_path, rv->path);
	if (bind(rv->self.fd, (struct sockaddr*)&info, SUN_LEN(&info)) == -1) {
		rv->err = PS_BIND_FAIL;
		return rv;
	}

	return rv;
}


void checkServer (PlogServer **srv) {
// post initialization error handling
	if (!(*srv)) {
		fprintf(stderr,"Could not create server: %s\n", strerror(errno));
		exit(XIT_NO_SERVER);
	}
	switch ((*srv)->err) {
		case (PS_SOCK_FAIL):
			fprintf(stderr,"Could not create socket: %s\n", strerror(errno));
			freeServer(*srv);
			exit(XIT_SOCK_FAIL);
		case (PS_BIND_FAIL):
			if (errno == EADDRINUSE) {
				int pid = pingSocket((*srv)->path, *srv);
				if (pid == -1) {
					fprintf(stderr, "Bind %s socket failed: %s\n", PLOG_TMPSOCK, strerror(errno));
					freeServer(*srv);
					exit(XIT_BIND_FAIL);
				}
				if (pid == -2) {
					fprintf(stderr, "Query existing server on %s failed: %s\n", (*srv)->path, strerror(errno));
					freeServer(*srv);
					exit(XIT_SOCK_INUSE);
				}
				if (pid) {
					fprintf(stderr,"Plogsrvd (pid %d) already running on %s.\n", pid, (*srv)->path);
					freeServer(*srv);
					exit(XIT_SOCK_INUSE);
				}
			// unlink stale socket and try again:
				if (unlink((*srv)->path) == -1) {
					fprintf(stderr, "Could not remove stale socket %s: %s\n", (*srv)->path, strerror(errno));
					freeServer(*srv);
					exit(XIT_STUBBORN_SOCKET);
				}
				uint32_t savecfg = ((*srv)->cfg);
				*srv = createServer((*srv)->path);
				(*srv)->cfg = savecfg;
				checkServer(srv);
				return;
			}
			fprintf(stderr,"Bind() fail: %s\n", strerror(errno));
			freeServer(*srv);
			exit(XIT_BIND_FAIL);
		case (PS_RELATIVE_SOCKPATH):
			fprintf(stderr,"%s is not an absolute path, sorry.\n", (*srv)->path);
			freeServer(*srv);
			exit(XIT_RELATIVE_SOCKPATH);
		default: break;
	}
}


int pingSocket (char *path, PlogServer *srv) {
/* checks for running server on socket, returns pid or
 * deletes stale file if no connect */
	int sock = socket(PF_LOCAL, SOCK_DGRAM, 0);
	if (sock == -1) {
		fprintf(stderr, "Could not create socket: %s", strerror(errno));
		exit(XIT_SOCK_FAIL);
	}

// get path for local socket
	struct sockaddr_un addr;
	if (getTmpSock(addr.sun_path, srv->cfg >> 20) == -1) {
		fprintf(stderr, "%d+ %s sockets, exiting.", srv->cfg >> 20, PLOG_TMPSOCK);
		freeServer(srv);
		exit(XIT_EXCESSIVE_STALE_SOCKS);
	}

// bind
	addr.sun_family = AF_LOCAL;
	if (bind(sock, (struct sockaddr*)&addr, SUN_LEN(&addr)) == -1) return -1;

// query
	int rv = 0, msg[2] = { 0, 2 };	// see main.c takecall()
	if (sendPacket(msg, sizeof(int)*2, sock, srv->path) == -1) {
		if (errno != ECONNREFUSED) rv = -2;
	} else {
		DataPacket *reply = getPacket(sock);
		rv = strtol(reply->data, NULL, 0);
	}

// close temp sock
	close(sock);
	if (unlink(addr.sun_path) == -1) error("Could not remove ", addr.sun_path, NULL);
	return rv;
}


int runServer (PlogServer *srv, void(*takecall)(DataPacket *pkt)) {
	int check;
	time_t now;

	while (1) {
		if (!fileExists(srv->path)) return PS_SOCKETFILE_GONE;

	// set poll (timeout on single fd)
		srv->self.events = POLLIN;
		check = poll(&(srv->self), 1, PLSRV_CYCLE_SECS * 1000);
		if (check == -1 || srv->self.revents & POLLERR
		  || srv->self.revents & POLLHUP || srv->self.revents & POLLNVAL)
			return PS_POLL_FAIL;
		now = time(NULL);

	// handle incoming packet
		if (check) {
			DataPacket *pkt = getPacket(srv->self.fd);
			if (!pkt) return PS_OUT_OF_MEM;
			takecall(pkt);
			freePacket(&pkt);
		}

	// walk list of logged processes
		plProcess *cur = srv->listHead;
		while (cur) {
			if (now >= cur->nextUpdate) {
			// update item
				plProcess *next = cur->next;
				int check = updateLog(cur);
				switch (check) {
					case (0): break;
					case (PLPR_NOLOGFILE):
					// if somebody removed the logfile, stop logging
						if (errno == ENOENT) llistRemove(&srv->listHead, cur);
						else error("Stat logfile error for ", cur->logfile, ": ", strerror(errno), NULL);
						break;
					case (PLPR_APPENDLOG_ERR):
						error("Can't append logfile ", srv->dir, "/", cur->logfile, ": ", strerror(errno), NULL);
							break;
					case (PLPR_READSTAT_ERR):
					// if the process no longer exists, stop logging
						if (errno == ENOENT) llistRemove(&srv->listHead, cur);
						else error("Slurp /proc/", my_itoa(cur->pid), "/stat error:", strerror(errno), NULL);
						break;
					default:
						error("runServer()->updateLog() returned ", my_itoa(check),", errno=", my_itoa(errno), NULL);
						break;
				}
				cur = next;
			} else cur = cur->next;
		}
	}
}


void freeServer (PlogServer *srv) {
	plProcess *cur = srv->listHead, *prev;
	while (cur) {
		prev = cur;
		cur = cur->next;
		free(prev);
	}
	free(srv);
}
