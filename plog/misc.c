/* misc.c for plog 0.1.0
 * Copyright 2011 M. Thomas Eriksen
 * Distributed under the terms of the GNU General Public License, v3
 * http://www.gnu.org/licenses/gpl.html */

#include <stdio.h>
#include <unistd.h>
#include "misc.h"

long int PageSize;

char *memUnits (unsigned int pages) {
	static char rv[16];
	unsigned int kB = pages * PageSize;
	if (kB < 4096) {
		sprintf(rv, "%ukB", kB);
		return rv;
	}

	sprintf(rv, "%.2lfMB", (double)kB/1024.0);
	return rv;
}


char *my_itoa (int n) {
	static char rv[32];
	sprintf(rv, "%d", n);
	return rv;
}


char *timestamp (time_t time) {
	static char rv[12];
	struct tm *data = localtime(&time);
	sprintf(rv, "%2d-%02d %2d:%02d",
		data->tm_mon+1,
		data->tm_mday,
		data->tm_hour,
		data->tm_min
	);
	return rv;
}

char *timeStr (unsigned long int secs) {
	static char rv[64];
	if (secs < 60) {
		sprintf(rv, "%lus", secs);
		return rv;
	}
	if (secs < 3600) {
		sprintf(rv, "%lu:%02u", secs/60, (unsigned int)(secs%60));
		return rv;
	}
	int rem = secs%3600;
	sprintf(rv, "%lu:%02d:%02d", secs/3600, rem/60, rem%60);
	return rv;
}
