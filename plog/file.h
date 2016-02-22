/* file.h for plog 0.1.0
 * Copyright 2011 M. Thomas Eriksen
 * Distributed under the terms of the GNU General Public License, v3
 * http://www.gnu.org/licenses/gpl.html */

int fileExists (const char *path);
int fileSize (const char *path);	// unused
char *fileSlurp (const char *path, int blksz);
