include config-host.mak

HOSTNAME=$(shell hostname)

all: $(build)/Makefile

$(build)/Makefile: Makefile.build
	cp $< $@

runmaster::
	celery -A gridmaster worker -c1 --loglevel=info > master.out 2>&1

runworker::
	python gridworker.py > worker.$(HOSTNAME).out 2>&1 &
