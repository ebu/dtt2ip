/* misc.h for plog 0.1.0
 * Copyright 2011 M. Thomas Eriksen
 * Distributed under the terms of the GNU General Public License, v3
 * http://www.gnu.org/licenses/gpl.html */

/* miscellaneous functions */
#include <time.h>

char *memUnits (unsigned int pages);
char *my_itoa (int n);
char *timestamp (time_t time);
char *timeStr (unsigned long int secs);
