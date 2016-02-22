/* llist.h for plog 0.1.0
 * Copyright 2011 M. Thomas Eriksen
 * Distributed under the terms of the GNU General Public License, v3
 * http://www.gnu.org/licenses/gpl.html */

#ifndef PLOG_LLIST_H
#define PLOG_LLIST_H

#include "process.h"

void llistAdd (plProcess **head, plProcess *new);
int llistGetTotal ();
void llistRemove (plProcess **head, plProcess *out);

#endif
