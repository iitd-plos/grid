include config-host.mak

all: $(build)/Makefile

$(build)/Makefile: Makefile.build
	cp $< $@

runmaster::
	celery -A gridmaster worker -c1 --loglevel=info

runworker::
	python gridworker.py
