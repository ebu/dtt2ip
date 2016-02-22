/* llist.c for plog 0.1.0
 * Copyright 2011 M. Thomas Eriksen
 * Distributed under the terms of the GNU General Public License, v3
 * http://www.gnu.org/licenses/gpl.html */

#include "llist.h"
#include <string.h>
#include <stdlib.h>
#include <malloc.h>

static int TotalLogs;

void llistAdd (plProcess **head, plProcess *new) {
	TotalLogs++;
	new->next = *head;
	*head = new;
}

int llistGetTotal () { return TotalLogs; }

void llistRemove (plProcess **head, plProcess *out) {
	plProcess *cur = *head, *prev = NULL;
	while (cur) {
		if (!strcmp(cur->logfile, out->logfile)) {
			if (cur == *head) *head = cur->next;
			else prev->next = cur->next;
			free(cur);
			TotalLogs--;
			malloc_trim(0);
			return;
		}
		prev = cur;
		cur = cur->next;
	}
}
