include config-host.mak

HOSTNAME=$(shell hostname)

all: $(build)/Makefile

$(build)/Makefile: Makefile.build
	cp $< $@

runmaster::
	rm -rf $(build)/readyq $(build)/doneq
	python gridinit.py
	celery -A gridmaster worker --concurrency 1 --loglevel=debug > master.out 2>&1 &

runworker::
	python gridworker.py > worker.$(HOSTNAME).out 2>&1 &

killmaster::
	pkill -9 -f "celery"
	rm -rf $(build)/readyq $(build)/workq_state $(build)/doneq $(build)/counter_state

killworker::
	pkill -9 -f "gridworker.py"
