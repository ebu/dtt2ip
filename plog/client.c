/* client.c for plog 0.1.0
 * Copyright 2011 M. Thomas Eriksen
 * Distributed under the terms of the GNU General Public License, v3
 * http://www.gnu.org/licenses/gpl.html */

#define __USE_POSIX2	// gcc -std=gnu99 should cover this
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>
#include <sys/socket.h>
#include <stdarg.h>
#include <signal.h>
#include <poll.h>
#include "udp.h"
#include "file.h"

// exit status
#define PLCL_PATH_TOOLONG 1
#define PLCL_SOCKFAIL 2
#define PLCL_NOBIND 3
#define PLCL_NOENT 4
#define PLCL_BAD_SERVSOCK 5
#define PLCL_NOACCESS 6
#define	PLCL_POLLERR 7
#define PLCL_TIMEOUT 8
#define PLCL_NOMEM 9
#define PLCL_SIGPIPE 10
#define PLCL_USAGE 11
#define PLCL_TOOMANY_TMPSOCK 12
#define PLCL_RECVERR 13

// request types
#define PLCL_NORM 1
#define PLCL_LISTALL 2
#define PLCL_GETPID 3
#define PLCL_GETDIR 4

void brokenPipe(int sig);
DataPacket *nextPacket (struct pollfd *self, const char *sockpath, int wait);
void end(int sock, const char *sockpath, int status);
void error (char *msg, ...);
void usage ();

int main(int argc, char *argv[]) {
	char plogServerPath[108] = "/var/local/plog";
	int maxTmp = PLOG_MAX_TMPSOCK, reqType = 0, waitSecs = 10;

	char *tmp = getenv("PLOGDIR");
	if (tmp) {
		if (strlen(tmp) > PLOG_RDIR_MAX) {
			fprintf(stderr, "$PLOGDIR is too long:\n%s\n", tmp);
			return PLCL_PATH_TOOLONG;
		}
		else strcpy(plogServerPath, tmp);
	}

// get args
	char opts[] = "hli:p:d:s:t:q:v";
	int cur, args[2] = {0, 0};
	while ((cur = getopt(argc, argv, opts)) > 0) {
		switch (cur) {
			case ('h'): usage();
			case ('p'):	// pid
				if (reqType && reqType != PLCL_NORM) usage();
				args[0] = strtol(optarg, NULL, 0);
				break;
			case ('i'):	// interval
				if (reqType) usage();
				args[1] = strtol(optarg, NULL, 0);
				reqType = PLCL_NORM;
				break;
			case ('d'):	// runtime directory
				if (strlen(optarg) > PLOG_RDIR_MAX) {
					fprintf(stderr, "Runtime directory path must be %d bytes or less.\n", PLOG_RDIR_MAX);
					return PLCL_PATH_TOOLONG;
				}
				strcpy(plogServerPath, optarg);
				break;
			case ('l'):	// list current logs
				if (reqType) usage();
				reqType = PLCL_LISTALL;
				break;
			case ('s'):	// max tmp socks
				if (!sscanf(optarg, "%d", &maxTmp)) usage();
				if (maxTmp < 2 || maxTmp > 4095) usage();
				break;
			case ('t'):	// request timeout
				if (!sscanf(optarg, "%d", &waitSecs)) usage();
				if (waitSecs < 1 || waitSecs > 300) usage();
				break;
			case ('q'):	// query
				if (reqType) usage();
				if (!strcmp(optarg, "pid")) reqType = PLCL_GETPID;
				else if (!strcmp(optarg, "dir")) reqType = PLCL_GETDIR;
				else usage();
				break;
			default: usage();
		}
	}
	strcat(plogServerPath, "/");
	strcat(plogServerPath, PLOGSRV_SOCK_NAME);

	switch (reqType) {
		case (PLCL_NORM):
			if (!args[0] || !args[1]) usage();
			break;
		case (PLCL_LISTALL):
			args[0] = 0;
			args[1] = 1;
			break;
		case (PLCL_GETPID):
			args[0] = 0;
			args[1] = 2;
			break;
		case (PLCL_GETDIR):
			args[0] = 0;
			args[1] = 3;
			break;
		default: usage();
	}

	signal(SIGPIPE, brokenPipe);

// get local file address for client socket
	struct sockaddr_un addr;
	if (getTmpSock(addr.sun_path, maxTmp) == -1) {
		fprintf(stderr, "%d+ %s sockets, exiting.", maxTmp, PLOG_TMPSOCK);
		return PLCL_TOOMANY_TMPSOCK;
	}

// set up socket
	struct pollfd self;
	self.fd = socket(PF_LOCAL, SOCK_DGRAM, 0);
	if (self.fd == -1) {
		fprintf(stderr,"Create socket failed: %s\n", strerror(errno));
		return PLCL_SOCKFAIL;
	}
	addr.sun_family = AF_LOCAL;
	if (bind(self.fd, (struct sockaddr*)&addr, SUN_LEN(&addr)) == -1) {
		fprintf(stderr, "Cannot bind to %s: %s\n", addr.sun_path, strerror(errno));
		return PLCL_NOBIND;
	}

// send request
	if (sendPacket(args, sizeof(int)*2, self.fd, plogServerPath) == -1) {
		switch (errno) {
			case (ENOENT):
				fprintf(stderr,"No plog server found.\n");
				end(self.fd, addr.sun_path, PLCL_NOENT);
			case (ECONNREFUSED):
				fprintf(stderr,"%s is a stale socket with no plogsrvd running.\n", plogServerPath);
				end(self.fd, addr.sun_path, PLCL_BAD_SERVSOCK);
			case (EACCES):
				fprintf(stderr,"Permission denied on %s.\nSee IPC MODE in the plogsrvd man page.\n", plogServerPath);
				end(self.fd, addr.sun_path, PLCL_NOACCESS);
			default:
				fprintf(stderr, "Sendto() returned %d: %s\n", errno, strerror(errno));
				end(self.fd, addr.sun_path, errno + 100);
		}
	}

// get reply
	DataPacket *reply = NULL;
	while (1) {
		if (reply) freePacket(&reply);
		reply = nextPacket(&self, addr.sun_path, waitSecs);
		if (!strcmp((char*)reply->data, PLOGSRV_LISTDONE)) break;
		printf("%s\n", (char*)reply->data);
		if (reqType != PLCL_LISTALL) break;
	} 
	if (reply) freePacket(&reply);

	end(self.fd, addr.sun_path, 0);
	return 666;
}


DataPacket *nextPacket (struct pollfd *self, const char *sockpath, int wait) {
	self->events = POLLIN;
	int check = poll(self, 1, wait*1000);
	if (!check) {
		fprintf(stderr,"Request timed out.\n");
		end(self->fd, sockpath, PLCL_TIMEOUT);
	}
	if (check == -1 || self->revents & POLLERR || self->revents & POLLHUP || self->revents & POLLNVAL) {
		fprintf(stderr,"Poll(revents=%d) error: %s\n", self->revents, strerror(errno));
		end(self->fd, sockpath, PLCL_POLLERR);
	}
	DataPacket *reply = getPacket(self->fd);
	if (!reply) {
		fprintf(stderr,"Out of memory!\n");
		end(self->fd, sockpath, PLCL_NOMEM);
	}
	if (reply->bytes == -1) {
		fprintf(stderr,"Recvfrom() error: %s\n", strerror(errno));
		freePacket(&reply);
		end(self->fd, sockpath, PLCL_RECVERR);
	}
	return reply;
}


void brokenPipe(int sig) {
	static int count = 0;
	fprintf(stderr, "Received SIGPIPE %d/3\n", count+1);
	if (count++ > 2) exit(PLCL_SIGPIPE);
	sleep(1);
}


void end(int sock, const char *sockpath, int status) {
	close(sock);
	if (unlink(sockpath) == -1) fprintf(stderr,"Could not remove %s\n.", sockpath);
	exit(status);
}


void error (char *msg, ...) {
// used in udp.c via extern
	int maxsz = 1024;
	va_list args;
	char txt[maxsz], *cur;
	int remain = maxsz - strlen(msg);
	strncpy(txt, msg, maxsz);

	va_start(args, msg);
	while ((cur = va_arg(args, char*)) && (remain > 1)) {
		strncat(txt, cur, remain);
		remain -= strlen(cur);
	}

	fprintf(stderr,"%s\n", txt);
}


void usage () {
	printf("Plog version %s usage:\n"
		"-p [pid] to log (required unless -l or -q)\n"
		"-i [interval] to log at, in minutes (required unless -l or -q)\n"
		"-d [runtime directory] of plogsrvd (not required)\n"
		"-l list currently active logfiles (conflicts with -p -i -q)\n"
		"-s [2-4095] number of %s sockets to tolerate\n"
		"-t [1-300] seconds to wait for reply (default 10).\n"
		"-q ['dir'|'pid'] get server runtime directory or pid (conflicts with -p -i -l)\n"
		"-h display this message.\n", PLOG_VERSION, PLOG_TMPSOCK
	);
	exit(PLCL_USAGE);
}
