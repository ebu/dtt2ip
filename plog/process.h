/* process.h for plog 0.1.0
 * Copyright 2011 M. Thomas Eriksen
 * Distributed under the terms of the GNU General Public License, v3
 * http://www.gnu.org/licenses/gpl.html */

#ifndef PLOG_PROCESS_H 
#define PLOG_PROCESS_H

#include <sys/types.h>

enum { // errors
	PLPR_READSTAT_ERR = 1,
	PLPR_NOLOGFILE,
	PLPR_CHECKLOG_ERR,
	PLPR_CREATELOG_ERR,
	PLPR_APPENDLOG_ERR,
	PLPR_READSTATM_ERR,
	PLPR_READMAPS_ERR,
	PLPR_READMAPS_SHORT
};

typedef struct plog_process {
	pid_t pid;
	char proc_path[16];
	char logfile[64];
	time_t nextUpdate;
	int interval;
	struct plog_process *next;
} plProcess;

int initProcLog (plProcess *pr);
plProcess *newProcess (int pid, int interval);
int updateLog (plProcess *pr);

#endif
