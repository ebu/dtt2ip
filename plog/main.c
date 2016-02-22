/* main.c for plog 0.1.0
 * Copyright 2011 M. Thomas Eriksen
 * Distributed under the terms of the GNU General Public License, v3
 * http://www.gnu.org/licenses/gpl.html */

#define __USE_POSIX2	// gcc -std=gnu99 should cover this
#include "server.h"
#include <stdio.h>
#include <errno.h>
#include <string.h>
#include <fcntl.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>
#include <stdarg.h>
#include <syslog.h>
#include <malloc.h>
#include <sys/vlimit.h>
#include <sys/stat.h>
#include "process.h"
#include "llist.h"
#include "misc.h"
#include "exitcodes.h"

/* bitfields for use in takecall() when adding new process */
#define UNLINK_LOGFILE 1
#define FREE_PROCOBJ 2

void consoleLog (char *msg, ...);
void end (int sig);
void error (char *msg, ...);
void fatal (char *msg, int code);
void sigHandler (int sig);
void takecall (DataPacket *pkt);
void usage ();

PlogServer *Server;
extern long int TicksPerSecond;
extern long int PageSize;

int main (int argc, char *argv[]) {
	TicksPerSecond = sysconf(_SC_CLK_TCK);
	PageSize = sysconf(_SC_PAGE_SIZE) / 1024;

// some memory settings
	mallopt(M_TRIM_THRESHOLD, 1);
	mallopt(M_TOP_PAD, 0);
	vlimit(LIM_STACK, 32768);

// get args
	char rtdir[PLOG_RDIR_MAX+1] = "/var/local/plog", sock_fullpath[108];
	char opts[] = "fe:hvd:s:m:";
	int cur, check;
	mode_t sock_mode = S_IRWXU;
	uint32_t cfgState = PLOG_MAX_TMPSOCK << 20;	// sets max stale /tmp sockets, qv. server.h
	cfgState |= PLOG_DEFAULT;

	char *tmp = getenv("PLOGDIR");
	if (tmp) {
		if (strlen(tmp) > PLOG_RDIR_MAX) {
			fprintf(stderr, "$PLOGDIR is too long:\n%s\n", tmp);
			return XIT_RTDIR_PATH_TOOLONG;
		}
		else strcpy(rtdir, tmp);
	}

	while ((cur = getopt(argc, argv, opts)) > 0) {
		switch (cur) {
			case ('h'): usage();
			case ('f'):	// foreground
				cfgState |= PLOG_FG;
				if (cfgState & PLOG_DEFAULT) {
					cfgState ^= PLOG_DEFAULT;
					cfgState |= PLOG_ERROUT;
				}
				break;
			case ('e'):	// error logging
				if (cfgState & PLOG_DEFAULT) cfgState ^= PLOG_DEFAULT;
				if (!strcmp(optarg, "stderr")) cfgState |= PLOG_ERROUT;
				else if (!strcmp(optarg, "both")) {
					cfgState |= PLOG_ERROUT;
					cfgState |= PLOG_SYSLOG;
				} else if (!strcmp(optarg, "none")) break;
				else usage();
				break;
			case ('v'):	// verbose
				cfgState |= PLOG_VERBOSE;
				break;
			case ('d'):	// runtime directory
				if (strlen(optarg) > PLOG_RDIR_MAX) {
					fprintf(stderr, "Runtime path %s is too long.\n", optarg);
					return XIT_RTDIR_PATH_TOOLONG;
				}
				strcpy(rtdir, optarg);
				rtdir[sizeof(rtdir)-1] = '\0';
				break;
			case ('s'):	// max tmp sockets
				if (!sscanf(optarg, "%d", &check)) usage();
				if (check < 2 || check > 4095) usage();
				cfgState &= 0xfff;
				cfgState |= check << 20;
				break;
			case ('m'):	// socket mode
				if (!strcmp(optarg, "any")) sock_mode |= S_IRWXG + S_IRWXO;
				else if (!strcmp(optarg, "group")) sock_mode |= S_IRWXG;
				else usage();
				break;
			default: usage();
		}
	}

	if (cfgState & PLOG_DEFAULT) {
		cfgState ^= PLOG_DEFAULT;
		cfgState |= PLOG_SYSLOG;
	}

// check runtime directory
	if (chdir(rtdir) == -1) {
		fprintf(stderr, "Could not change directory to %s: %s\n", rtdir, strerror(errno));
		return XIT_CHDIR_FAIL;
	}

// create server object
	snprintf(sock_fullpath, 108, "%s/%s", rtdir, PLOGSRV_SOCK_NAME);
	if (!(Server = createServer(sock_fullpath))) fatal("Not enough memory!", XIT_NOMEM);
	Server->cfg = cfgState;
	checkServer(&Server);

	if (chmod(sock_fullpath, sock_mode) == -1) perror("Set mode on socket failed: ");

// daemonize
	char msg[1024];
	if (!(cfgState & PLOG_FG)) {
		pid_t pid = fork();
		if (pid == -1) {
			sprintf(msg, "Failed to fork: %s", strerror(errno));
			fatal(msg, XIT_FORK_FAILED);
		} else if (pid) return 0;	// parent exits
		setsid();
	}
	sprintf(msg, "Plogsrvd started, pid %d, using ", getpid());
	consoleLog(msg, rtdir, NULL);

// set-up signal handlers
	signal(SIGQUIT, end);
	signal(SIGPIPE, sigHandler);

// run server
	int cause_of_death = runServer(Server, takecall);
	switch (cause_of_death) {
		case (PS_POLL_FAIL):
			snprintf(msg, 1024, "Poll() failed: %s", strerror(errno));
			fatal(msg, XIT_ABORT_POLL_FAIL);
		case (PS_SOCKETFILE_GONE):
			snprintf(msg, 1024, "Socket %s gone.", Server->path);
			fatal(msg, XIT_ABORT_SOCK_GONE);
		case (PS_OUT_OF_MEM):
			fatal("Out of memory.", XIT_NOMEM);
		default: return 666;
	}

	return 0;
}


void consoleLog (char *msg, ...) {
/* verbose mode stdout messages */
	if (!(Server->cfg & PLOG_VERBOSE)) return;

	va_list args;
	char txt[1024], *cur;
	int remain = 1024 - strlen(msg);
	strncpy(txt, msg, 1024);

	va_start(args, msg);
	while ((cur = va_arg(args, char*)) && (remain > 0)) {
		strncat(txt, cur, remain-1);
		remain -= strlen(cur);
	}

	printf("%s %s\n", timestamp(time(NULL)), txt);
	fflush(stdout);
}


void error (char *msg, ...) {
	int maxsz = 1024;
	if (!(Server->cfg & PLOG_ERROUT) && !(Server->cfg &PLOG_SYSLOG)) return;

	va_list args;
	char txt[maxsz], *cur;
	int remain = maxsz - strlen(msg);
	strncpy(txt, msg, maxsz);

	va_start(args, msg);
	while ((cur = va_arg(args, char*)) && (remain > 1)) {
		strncat(txt, cur, remain);
		remain -= strlen(cur);
	}

	if (Server->cfg & PLOG_ERROUT)
		fprintf(stderr, "%s %s\n", timestamp(time(NULL)), txt);

	if (Server->cfg & PLOG_SYSLOG)
		syslog(LOG_MAKEPRI(LOG_DAEMON, LOG_ERR), "plogsrvd %d: %s", getpid(), txt);
}


void end (int sig) {
// signal handler for SIGQUIT
	close(Server->self.fd);
	if (unlink(Server->path) == -1) error("Could not unlink ", Server->path, ": ", strerror(errno), NULL);
	consoleLog("Recieved SIGQUIT, exiting.", NULL);
	freeServer(Server);
	exit(0);
}


void fatal (char *msg, int code) {
	close(Server->self.fd);
	if (unlink(Server->path) == -1) error("Could not unlink ", Server->path, ": ", strerror(errno), NULL);
	freeServer(Server);
	error("FATAL: ", msg, " ...exiting", NULL);
	exit(code);
}


void sigHandler (int sig) {
	char msg[1024];
	sprintf(msg, "Recieved signal %d.", sig);
	consoleLog(msg, NULL);
}


void takecall (DataPacket *pkt) {
	char msg[PLOG_MAX_PAYLOAD];

	if (pkt->bytes == -1) {
		error("recvfrom() fail", strerror(errno), NULL);
		return;
	}
// all requests to the server follow the "plogd protocol" (qv. udp.h):
	int pid = *(int*)pkt->data, interval = *(int*)(pkt->data + sizeof(int));

// if first int is zero, this is a special request:
	if (pid == 0) {
		int listsz, msgsz = 0;
		switch (interval) {
			case (1):	// send current list
				listsz = llistGetTotal();
				if (listsz) {
					plProcess *cur = Server->listHead;
					while (cur) {
						// bail on error
						if (sendPacket(cur->logfile, 0, Server->self.fd, pkt->from.sun_path) == -1) return;
						cur = cur->next;
					}
				}
				strcpy(msg, PLOGSRV_LISTDONE);
				break;
			case (2):	// send pid
				sprintf(msg, "%d", getpid());
				break;
			case (3):	// send cwd
				strcpy(msg, Server->dir);
				break;
			default:
				strcpy(msg, "Unrecognized request.");
				break;
		}
		sendPacket(msg, msgsz, Server->self.fd, pkt->from.sun_path);
		return;
	}

// add new plProcess:
	plProcess *process = newProcess(pid, interval);
	if (!process) fatal("Out of memory!", XIT_NOMEM);
	if (!process->pid) {
		if (process->interval == -1) sprintf(msg, "No such process (%d).", pid);
		else sprintf(msg, "pid %d: %s", pid, strerror(process->interval));
		sendPacket(msg, 0, Server->self.fd, pkt->from.sun_path);
		free(process);
		return;
	}
	int check = initProcLog(process);
	if (check) {
		sprintf(msg, "Problem logging to %s -- ", process->logfile);
		int act = 0;
		switch (check) {
			case (PLPR_READSTAT_ERR):
				strcat(msg, "Can't read 'stat': ");
				act |= FREE_PROCOBJ;
				break;
			case (PLPR_NOLOGFILE):
				strcat(msg, "Can't find log: ");
				act |= FREE_PROCOBJ;
				break;
			case (PLPR_CHECKLOG_ERR):
				if (errno) strcat(msg, "Error checking files: ");
				else strcat(msg, "Too many files!");
				act |= FREE_PROCOBJ;
				break;
			case (PLPR_CREATELOG_ERR):
				strcat(msg, "Can't create logfile: ");
				act |= FREE_PROCOBJ;
				break;
			case (PLPR_APPENDLOG_ERR):
				strcat(msg, "Can't append logfile: ");
				act |= FREE_PROCOBJ + UNLINK_LOGFILE;
				break;
			case (PLPR_READSTATM_ERR):
				strcat(msg, "Can't read 'statm': ");
				act |= FREE_PROCOBJ + UNLINK_LOGFILE;
				break;
			case (PLPR_READMAPS_ERR):	// no longer reported
				strcat(msg, "Can't read 'maps': ");
				break;
			case (PLPR_READMAPS_SHORT):
				strcat(msg, "Short read on 'maps'.");
				errno = 0;
				break;
			default:
				break;
		}
		if (act) {
			if (errno) strncat(msg, strerror(errno), PLOG_MAX_PAYLOAD - strlen(msg) - 1);
			error(msg, NULL);
			sendPacket(msg, 0, Server->self.fd, pkt->from.sun_path);
			if (act & UNLINK_LOGFILE) unlink(process->logfile);
			if (act & FREE_PROCOBJ) free(process);
			return;
		} else {
			if (errno) strncat(msg, strerror(errno), PLOG_MAX_PAYLOAD - strlen(msg) - 1);
			error(msg, NULL);
		}
	}
	llistAdd(&Server->listHead, process);
	consoleLog("Now logging to ", process->logfile, ", every ", my_itoa(process->interval), " minutes.", NULL);

// all good
	sprintf(msg, "Log file: %s/%s", Server->dir, process->logfile);
	sendPacket(msg, 0, Server->self.fd, pkt->from.sun_path);
}


void usage () {
	printf("Plogsrvd version %s usage:\n"
		"-f run in foreground.\n"
		"-e [stderr|both|none] where to log errors (defaults to syslog):\n"
		"\tstderr = process's stderr stream (default if foregrounded).\n"
		"\tboth = syslog and stderr\n"
		"\tnone = no error reporting\n"
		"-d [runtime directory], default is /var/local/plog or by environment's PLOGDIR.\n"
		"-v verbose operation.\n"
		"-s [2-4095] max number of %s sockets (default %d).\n"
		"-m [any|group] IPC mode (see man page)\nThe default is to only accept requests from"
		" plog clients with the same uid.\n"
		"\tany = allow any plog client to make a request\n"
		"\tgroup = allow plog clients with the same gid to make requests\n"
		"-h print this message.\n\n", PLOG_VERSION, PLOG_TMPSOCK, PLOG_MAX_TMPSOCK);
	exit(XIT_USAGE);
}
