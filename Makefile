include config-host.mak

HOSTNAME=$(shell hostname)

all: $(build)/Makefile

$(build)/Makefile: Makefile.build
	cp $< $@

runmaster::
	celery -A gridmaster worker -c1 --loglevel=info > master.out 2>&1 &
	python gridinit.py

runworker::
	python gridworker.py > worker.$(HOSTNAME).out 2>&1 &

killmaster::
	killall -9 celery
	rm -rf $(build)/readyq $(build)/workq $(build)/doneq $(build)/counter
