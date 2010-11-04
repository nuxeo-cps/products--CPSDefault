# See README.txt for usage
.PHONY: clean prepare all build test doc log RAZ pack start stop
.PHONY:	start_zope stop_zope restart_zope
.PHONY:	start_monitor stop_monitor restart_monitor
.PHONY:	start_credential stop_credential restart_credential

INSTANCE_HOME := ./var/fl_zope
ZOPE_HOME := /opt/Zope-2.9
SOFTWARE_HOME := $(ZOPE_HOME)/lib/python
FSDUMP := PYTHONPATH=$(SOFTWARE_HOME) python $(ZOPE_HOME)/bin/fsdump.py

CREDCTL := fl-credential-ctl credential.conf
MONCTL := fl-monitor-ctl monitor.conf
SRC_DOCS := README.txt
HTML_DOCS := $(subst .txt,.html,${SRC_DOCS})
RST2HTML := rst2html -t --stylesheet-path=../doc/cps_doc.css --embed-stylesheet


ifdef URL
	FLOPS = -u $(URL)
	ZOPECTL := @true
else
	FLOPS =
	ZOPECTL := $(INSTANCE_HOME)/bin/zopectl
endif

define START_ZOPE
	$(ZOPECTL) start
	fl-run-test -v test_Cps.py Cps.test_00_availability $(FLOPS)
endef

define START_BENCH
	$(CREDCTL) restart
	$(MONCTL) restart
	$(ZOPECTL) restart
	fl-run-test -v test_Cps.py Cps.test_00_availability $(FLOPS)
endef

define PACK_ZODB
	-$(ZOPECTL) stop
	-ls -l $(INSTANCE_HOME)/var/Data.fs
	-cat pack_zodb.py | $(ZOPECTL) debug
	-ls -l $(INSTANCE_HOME)/var/Data.fs
endef

all: build test

prepare:
	-mkdir --parent report log

# zope management
build: prepare
	-$(ZOPECTL) stop
	python create_zope_server.py

start_zope:
	$(ZOPECTL) start

stop_zope:
	-$(ZOPECTL) stop

restart_zope:
	$(ZOPECTL) restart

log:
	tail -f $(INSTANCE_HOME)/log/event.log

RAZ:
	-$(ZOPECTL) stop
	-rm -rf $(INSTANCE_HOME)

pack:
	$(PACK_ZODB)

# monitor ctl
start_monitor:
	$(MONCTL) start

stop_monitor:
	-$(MONCTL) stop

restart_monitor:
	-$(MONCTL) restart

# credential ctl
start_credential:
	$(CREDCTL) start

stop_credential:
	-$(CREDCTL) stop

restart_credential:
	-$(CREDCTL) restart

# initialize the cps test server
test: prepare
	$(START_BENCH)
	-fl-run-test -v test_Cps.py Cps $(FLOPS)

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
	-$(MONCTL) status;
	-$(CREDCTL) status;
	@echo "### Zope status:"
	$(ZOPECTL) status

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
