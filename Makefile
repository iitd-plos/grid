include config-host.mak

HOSTNAME=$(shell hostname)

all: $(build)/Makefile

$(build)/Makefile: Makefile.build
	cp $< $@

runmaster::
	rm -rf $(build)/readyq $(build)/doneq
	celery -A gridmaster worker --concurrency 1 --loglevel=info > master.out 2>&1 &
	sleep 2
	python gridinit.py

runworker::
	python gridworker.py > worker.$(HOSTNAME).out 2>&1 &

killmaster::
	pkill -9 -f "celery"
	rm -rf $(build)/readyq $(build)/workq_state $(build)/doneq $(build)/counter_state

killworker::
	pkill -9 -f "gridworker.py"
