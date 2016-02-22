/* udp.c for plog 0.1.0
 * Copyright 2011 M. Thomas Eriksen
 * Distributed under the terms of the GNU General Public License, v3
 * http://www.gnu.org/licenses/gpl.html */

#include <sys/socket.h>
#include <string.h>
#include <stdio.h>
#include <errno.h>
#include <stdlib.h>
#include "udp.h"
#include "file.h"

extern void error (char *msg, ...);

DataPacket *getPacket (int sock) {
	DataPacket *rv = malloc(sizeof(DataPacket));
	if (!rv) return NULL;
	if (!(rv->data = malloc(PLOG_MAX_PAYLOAD))) {
		free(rv);
		return NULL;
	}
	socklen_t sz = sizeof(struct sockaddr_un);
	rv->bytes = recvfrom(sock, rv->data, PLOG_MAX_PAYLOAD, 0, (struct sockaddr*)&(rv->from), &sz);
	return rv;
}

int sendPacket (void *msg, int len, int sock, char *path) {
	struct sockaddr_un dest;
	dest.sun_family = AF_LOCAL;
	strcpy(dest.sun_path, path);
	if (!len) len = strlen(msg)+1;
	int rv = sendto(sock, msg, len, 0, (struct sockaddr*)&dest, sizeof(struct sockaddr_un));
	if (rv == -1 && errno != ECONNREFUSED) error("sendto(", path, ") error: ", strerror(errno), NULL);
	return rv;
}

void freePacket (DataPacket **pkt) {
	free((*pkt)->data);
	free(*pkt);
	*pkt = NULL;
}

int getTmpSock (char *filename, int maxsocks) {
	int check, i = 1;
	strcpy(filename, PLOG_TMPSOCK);
	while ((check = fileExists(filename))) {
		if (check == -1) error("Could not check ", filename, ": ", strerror(errno), NULL);
		if (++i == maxsocks) return -1;
		sprintf(filename, "%s-%d", PLOG_TMPSOCK, i);
	}
	return 0;
}
