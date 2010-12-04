# See README.txt for usage
.PHONY: clean prepare all build test doc log RAZ pack start stop
.PHONY:	start_zope stop_zope restart_zope
.PHONY:	start_monitor stop_monitor restart_monitor
.PHONY:	start_credential stop_credential restart_credential

INSTANCE_HOME := ~/opt/zope/funkload_instance 
ZOPE_HOME := ~/opt/zope/zope-server
SOFTWARE_HOME := $(ZOPE_HOME)/lib/python
FSDUMP := PYTHONPATH=$(SOFTWARE_HOME) python $(ZOPE_HOME)/bin/fsdump.py

CRED_CTL := fl-credential-ctl credential.conf
MON_CTL := fl-monitor-ctl monitor.conf
SRC_DOCS := README.txt
HTML_DOCS := $(subst .txt,.html,${SRC_DOCS})
RST2HTML := rst2html -t --stylesheet-path=../doc/cps_doc.css --embed-stylesheet


ifdef URL
	FLOPS = -u $(URL)
	ZOPE_CTL := @true
else
	FLOPS =
	ZOPE_CTL := $(INSTANCE_HOME)/bin/zopectl
endif

define START_ZOPE
	$(ZOPE_CTL) start
	fl-run-test -v test_Cps.py Cps.test_00_availability $(FLOPS)
endef

define START_BENCH
	$(CRED_CTL) restart
	$(MON_CTL) restart
	$(ZOPE_CTL) restart
	fl-run-test -v test_Cps.py Cps.test_00_availability $(FLOPS)
endef

define PACK_ZODB
	-$(ZOPE_CTL) stop
	-ls -l $(INSTANCE_HOME)/var/Data.fs
	-cat pack_zodb.py | $(ZOPE_CTL) debug
	-ls -l $(INSTANCE_HOME)/var/Data.fs
endef

all: build test

prepare:
	-mkdir --parent report log

# Zope management
build: prepare
	-$(ZOPE_CTL) stop
	python create_zope_server.py

start_zope:
	$(ZOPE_CTL) start

stop_zope:
	-$(ZOPE_CTL) stop

restart_zope:
	$(ZOPE_CTL) restart

log:
	tail -f $(INSTANCE_HOME)/log/event.log

RAZ:
	-$(ZOPE_CTL) stop
	-rm -rf $(INSTANCE_HOME)

pack:
	$(PACK_ZODB)

# monitor ctl
start_monitor:
	$(MON_CTL) start

stop_monitor:
	-$(MON_CTL) stop

restart_monitor:
	-$(MON_CTL) restart

# credential ctl
start_credential:
	$(CRED_CTL) start

stop_credential:
	-$(CRED_CTL) stop

restart_credential:
	-$(CRED_CTL) restart

# initialize the cps test server
test: prepare
	$(START_BENCH)
	-fl-run-test -v test_Cps.py $(FLOPS)

# produce ~150 documents in all personal workspaces in 3 minutes
volumize: volumize_create_docs pack

volumize_create_docs:
	$(START_BENCH)
	-fl-run-bench test_Cps.py Cps.test_10_create_doc -c 1:1:1 -D 60 -m0 -M0 $(FLOPS)
	-fl-build-report log/cps-bench.xml --html -o ./report/volumize

# bench
bench: volumize readers writers pack

readers: reader_anonymous reader_member

reader_anonymous:
	$(START_BENCH)
	-fl-run-bench -c 1:2:4:6:8:10:12:14:16:18:20 -D 30 test_Cps.py Cps.test_30_reader_anonymous $(FLOPS)
	-fl-build-report log/cps-bench.xml --html -o ./report/bench

reader_member:
	$(START_BENCH)
	-fl-run-bench -c 1:3:5:7:9 -D 60 test_Cps.py Cps.test_31_reader_member $(FLOPS)
	-fl-build-report log/cps-bench.xml --html -o ./report/bench


writers: write_and_publish write_docs

write_and_publish:
	$(START_BENCH)
	-fl-run-bench -c 1:2:3:4:5 -D 60 test_Cps.py Cps.test_22_publish $(FLOPS)
	-fl-build-report log/cps-bench.xml --html -o ./report/bench

write_docs:
	$(START_BENCH)
	-fl-run-bench -c 1:2:3:4:5 -D 60 test_Cps.py Cps.test_10_create_doc $(FLOPS)
	-fl-build-report log/cps-bench.xml --html -o ./report/bench


# CpsRemoteController
CRC_test:
	$(START_BENCH)
	fl-run-test -v test_CpsRemoteController.py $(FLOPS)

CRC_write_docs:
	$(START_BENCH)
	-fl-run-bench -c 1:2:3:4:5 -D 60 test_CpsRemoteController.py CpsRemoteController.test_20_createDocument $(FLOPS)
	-fl-build-report log/cps-remote-controller-bench.xml --html -o ./report/bench


# misc
status:
	-$(MON_CTL) status;
	-$(CRED_CTL) status;
	@echo "### Zope status:"
	$(ZOPE_CTL) status

stop: stop_monitor stop_credential stop_zope

start: start_monitor start_credential start_zope

restart: restart_monitor restart_credential restart_zope

doc: ${HTML_DOCS}

%.html: %.txt
	${RST2HTML} $< $@

hotspot:
	$(FSDUMP) $(INSTANCE_HOME)/var/Data.fs > /tmp/Data.fs.dump
	cat /tmp/Data.fs.dump|sed -n  's/.*data #[0-9]*//p'|sort|uniq -c|sort -n|tail -n 50

conflicts:
	grep "ZODB conflict error" $(INSTANCE_HOME)/log/event.log | wc -l

clean:
	-find . "(" -name "*~" -or  -name ".#*" -or -name "*.pyc" ")" -print0 | xargs -0 rm -f
	rm -f ${HTML_DOCS}
	rm -rf report
	rm -rf log
