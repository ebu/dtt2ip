/* process.c for plog 0.1.0
 * Copyright 2011 M. Thomas Eriksen
 * Distributed under the terms of the GNU General Public License, v3
 * http://www.gnu.org/licenses/gpl.html */

#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include "misc.h"
#include "process.h"
#include "file.h"

long int TicksPerSecond;
extern long int PageSize;

static int procSmaps(char *proc_path, unsigned int *share, unsigned int *pss);

plProcess *newProcess (int pid, int interval) {
// check proc
	char ppath[64];
	sprintf(ppath, "/proc/%d", pid);
	plProcess *rv = malloc(sizeof(plProcess));
	if (!rv) return NULL;

	int check = fileExists(ppath);
	if (!check) {
		rv->pid = 0;
		rv->interval = -1;
	}
	else if (check == -1) {
		rv->pid = 0;
		rv->interval = errno;
	} else {
		strcpy(rv->proc_path, ppath);
		rv->pid = pid;
		rv->interval = interval;
		rv->next = NULL;
	}

	return rv;
}

int initProcLog (plProcess *pr) {
// get name for log file
	// read data from /proc/[pid]/stat
	char fname[64];
	sprintf(fname, "%s/stat", pr->proc_path);
	char *data = fileSlurp(fname, 256);
	if (!data) return PLPR_READSTAT_ERR;

	// extract name
	if (sscanf(data, "%*d (%59[^)]) ", fname) != 1) return PLPR_READSTAT_ERR;
	free(data);
	int i, check = strlen(fname);
	for (i = 0; i < check; i++)
		if (fname[i] == '*' || fname[i] == '/') fname[i] = '_';
	// add pid
	sprintf(pr->logfile, "%s.%d", fname, pr->pid);
	strcpy(fname, pr->logfile);
	// check if log file exists, add .2, .3, etc if necessary
	i = 2;
	while ((check = fileExists(pr->logfile))) {
		if (check == -1) return PLPR_CHECKLOG_ERR;
		sprintf(pr->logfile, "%s.%d", fname, i);
		if (i++ > 999) {
			errno = 0;
			return PLPR_CHECKLOG_ERR;
		}
	}

// create logfile
	// get cmdline
	sprintf(fname, "%s/cmdline", pr->proc_path);
	char *cmdline = fileSlurp(fname, 32);
	// open
	FILE *log = fopen(pr->logfile, "w");
	if (!log) return PLPR_CREATELOG_ERR;
	// write
	if (cmdline) {
		fwrite(cmdline, strlen(cmdline), 1, log);
		free(cmdline);
	}
	char cols[] = "\nDate   Time State Prio  __Utime__ Threads VirtualSz ResidentSz "
		"Share Proportion Data+Stack Priv&Write MinorFaults MajFlts";
	fwrite(cols, strlen(cols), 1, log);
	fclose(log);

	return updateLog(pr);
}


int updateLog (plProcess *pr) {
	if (!fileExists(pr->logfile)) return PLPR_NOLOGFILE;
	FILE *log = fopen(pr->logfile, "a");
	if (!log) return PLPR_APPENDLOG_ERR;

// get data from [proc_path]/stat
	char fname[64];
	sprintf(fname, "%s/stat", pr->proc_path);
	char *data = fileSlurp(fname, 256), state;
	if (!data) {
		fclose(log);
		return PLPR_READSTAT_ERR;
	}
	unsigned long int minfaults[2], majfaults[2], utime;
	int prio, threads;
	sscanf(data, "%*d %*s %c %*d %*d %*d %*d %*d %*u %lu %lu %lu %lu %lu %*u %*d %*d %d %*d %d",
		&state, &minfaults[0], &minfaults[1], &majfaults[0], &majfaults[1], &utime, &prio, &threads);
	free(data);

// write
	fprintf(log, "\n%s   %c   %4d %10s %6d", timestamp(time(NULL)),
		state, prio, timeStr(utime/TicksPerSecond), threads);

// get data from [proc_path]/smaps
	unsigned int share, pss;
	int smaps = procSmaps(pr->proc_path, &share, &pss);

// get data from [proc_path]/statm
	sprintf(fname, "%s/statm", pr->proc_path);
	data = fileSlurp(fname, 64);
	if (!data) {
		fclose(log);
		return PLPR_READSTATM_ERR;
	}
	unsigned int virt, rss, stack;
	if (!smaps) sscanf(data, "%u %u %u %*u %*u %u", &virt, &rss, &share, &stack);
	else sscanf(data, "%u %u %*u %*u %*u %u", &virt, &rss, &stack);
	free(data);

// calculate share %
	float share_cent = (float)share/(float)(rss*PageSize) * 100.0f;

// write
	fprintf(log, " %10s", memUnits(virt));
	fprintf(log, " %10s", memUnits(rss));
	fprintf(log, " %4.1f%%", share_cent);
	if (smaps == 2) fprintf(log, " %10s", memUnits(pss/PageSize));
	else if (smaps == 1) fprintf(log, "   n/a     ");
	else fprintf(log, "           ");
	fprintf(log, " %10s", memUnits(stack));
	pr->nextUpdate = time(NULL) + 60*pr->interval;

// get data from [proc_path]/maps for "Private & Writable"
	sprintf(fname, "%s/maps", pr->proc_path);
	data = fileSlurp(fname, 1024);
	if (!data) {
		fprintf(log, "           ");
		goto faults;
	}
	size_t bytes = 0, len = strlen(data);
	char *ptr = data, perms[8];
	unsigned long int a, b;
	while (ptr-data < len) {
		if (sscanf(ptr, "%lx-%lx %s", &a, &b, perms) != 3) {
			free(data);
			fclose(log);
			return PLPR_READMAPS_SHORT;
		}
		if (perms[3] == 'p' && perms[1] == 'w') bytes += b-a;
		ptr = strchr(ptr, '\n');
		ptr++;
	}
	free(data);

// write
	fprintf(log, " %10s", memUnits(bytes / sysconf(_SC_PAGE_SIZE)));

// add minor and major page faults
	faults:
	fprintf(log, " %11lu %7lu", minfaults[0]+minfaults[1], majfaults[0]+majfaults[1]);

	fclose(log);
	return 0;
}


static int procSmaps(char *proc_path, unsigned int *share, unsigned int *pss) {
	char fpath[64], *data;
	sprintf(fpath, "%s/smaps", proc_path);
	data = fileSlurp(fpath, 1024);
	if (!data) return 0;

	*share = *pss = 0;

	char *line = strtok(data, "\n");
	unsigned int cur, pss_found = 0, share_found = 0;
	while ((line = strtok(NULL, "\n"))) {
		if (!strncmp(line, "Pss", 3)) {
			if (sscanf(line, "Pss:%*[ \t]%d kB", &cur) > 0) *pss += cur;
			pss_found++;
		} else if (!strncmp(line, "Shared", 6)) {
			if (sscanf(line, "Shared_%*[A-Za-z \t:_]%d kB", &cur) > 0) *share += cur;
			share_found++;
		}
	}

	free(data);
	if (pss_found && share_found) return 2;
	return 1;
}
