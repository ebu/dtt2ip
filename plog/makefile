VERSION = 0.1.0
CFLAGS += -Wall -g -O2 -std=gnu99 -DPLOG_MAX_TMPSOCK=$(max_tmp_socks) -DPLOG_TMPSOCK=$(tmp_sock_base)
OBJS = server.o process.o llist.o misc.o udp.o file.o
ifndef INSTALL_PATH
    INSTALL_PATH = /usr/local/
endif
# runtimedir is the hardcoded default runtime directory used by
# plogsrvd.  
# See the plogsrvd man page for more information.
runtimedir = /var/local/plog
# max_tmp_socks is the number of temporary sockets to tolerate.
# Again, see the plogsrvd man page for more information.
max_tmp_socks = 20
# tmp_sock_base is the absolute path and basename for the
# temporary sockets.  If you change this, take care not to change
# the quoting, which should '"like this"'
tmp_sock_base = '"/tmp/.plog"'

all: plogsrvd client


%.o: %.c %.h
	$(CC) $(CFLAGS) -c $<

plogsrvd: main.c $(OBJS)
	$(CC) $(CFLAGS) main.c $(OBJS) -o plogsrvd

client: udp.o file.o client.c
	$(CC) $(CFLAGS) client.c udp.o file.o -o plog

tarball: clean
	cd .. && tar --exclude-from=plog-$(VERSION)/.tar_ignore \
	-czf plog-$(VERSION).tar.gz plog-$(VERSION)/

# doc

manpages: plog.pod
	-pod2man -u -c plog -r "plog $(VERSION)" -d "October 2011" plog.pod plog.1
	-pod2man -u -c plogrsvd -r "plogsrvd $(VERSION)" -d "October 2011" plogsrvd.pod plogsrvd.1

htmldoc: plog.pod
	-pod2html --infile plog.pod --outfile plog.1.html --flush
	-pod2html --infile plogsrvd.pod --outfile plogsrvd.1.html --flush

# installs

install: plogsrvd client manpages
	-mkdir -p $(INSTALL_PATH)/bin
	-cp plogsrvd $(INSTALL_PATH)/bin
	-cp plog $(INSTALL_PATH)/bin
	-mkdir -p $(INSTALL_PATH)/share/man/man1
	-cp plogsrvd.1 $(INSTALL_PATH)/share/man/man1
	-cp plog.1 $(INSTALL_PATH)/share/man/man1
	mkdir -p $(runtimedir)
	chmod 1777 $(runtimedir)

PHONY: clean uninstall

uninstall:
	-rm $(INSTALL_PATH)/bin/plogsrvd
	-rm $(INSTALL_PATH)/bin/plog
	-rm $(INSTALL_PATH)/share/man/man1/plogsrvd.1
	-rm $(INSTALL_PATH)/share/man/man1/plog.1
	@echo "$(runtimedir) was not removed"

# clean

clean:
	-rm plog plogsrvd *.o
	-rm plog.1 plog.1.html plogsrvd.1 plogsrvd.1.html
