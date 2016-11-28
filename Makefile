include config-host.mak

all: $(build)/Makefile

$(build)/Makefile: Makefile.build
	cp $< $@
