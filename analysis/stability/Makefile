BASE=Makefile gridlabd.conf model.glm model.py auction.py system.glm

all: system market

system: regulation/system.png regulation/ramp_up.png regulation/ramp_down.png regulation/noise.png

market: retail/power.png

retail/%.png: $(BASE) %.glm
	@echo "$$(basename $@ | sed 's/.png/.glm/'): "
	@gridlabd $$(basename $@ | sed 's/.png/.glm/') 

regulation/%.png: $(BASE) %.glm
	@echo "$$(basename $@ | sed 's/.png/.glm/'): "
	@gridlabd $$(basename $@ | sed 's/.png/.glm/')
