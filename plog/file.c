/* file.c for plog 0.1.0
 * Copyright 2011 M. Thomas Eriksen
 * Distributed under the terms of the GNU General Public License, v3
 * http://www.gnu.org/licenses/gpl.html */

#include <stdio.h>
#include <sys/stat.h>
#include <errno.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include "file.h"

int fileExists (const char *path) {
	struct stat info;
	int check = stat(path, &info);
	if (!check) return 1;
	if (check == -1 && errno == ENOENT) return 0;
	return -1;
}

int fileSize (const char *path) {
	struct stat info;
	int check = stat(path, &info);
	if (check == -1) return -1;
	return info.st_size;
}

char *fileSlurp (const char *path, int blksz) {
	char *rv = malloc(blksz+1);
	if (!rv) return NULL;

// can't use stream with /proc files, must use low-level primitives
// also: use smaller than page size units on large proc files
	int fd = open(path, O_RDONLY);
	if (fd == -1) {
		free(rv);
		return NULL;
	}

	size_t cur = read(fd, rv, blksz), blocks = 1;
	if (cur == -1) {
		close(fd);
		return NULL;
	}
	rv[cur] = '\0';
	while (cur == blksz) {
		int count = blocks*blksz;
		blocks++;
		char *tmp = realloc(rv, blocks*blksz+1);
		if (!tmp) {
			free(rv);
			close(fd);
			return NULL;
		}
		rv = tmp;
		cur = read(fd, &rv[count], blksz);
		if (cur == -1) {
			close(fd);
			return rv;
		}
		rv[count+cur] = '\0';
	}

	close(fd);
	return rv;
}
