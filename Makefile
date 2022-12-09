 
# firefly Makefile
# 
# https://docs.circuitpython.org/en/latest/docs/workflows.html#get
#

# URL to access circuitpython hardware
#   Use CPURL environment variable if its set
CPURL := $(if $(CPURL),$(CPURL),http://circuitpython.local)

# the web api login password
CIRCUITPY_WEB_API_PASSWORD=REDACTED_FOR_GITHUB

# Comment out if you don't want to see curl activity
VERBOSE=-v

# No config below this line
all: install .gitignore

install: .install-version.py .install-boot.py .install-code.py .install-firefly.py

version.py: code.py firefly.py
	date -r code.py "+__version__ = %'%Y-%m-%d %H:%M:%S%'" > version.py

.install-%.py: %.py
	curl $(VERBOSE) -u :$(CIRCUITPY_WEB_API_PASSWORD) --create-dirs --location --location-trusted \
		--upload-file $< $(CPURL)/fs/$< \
	  	&& touch $(@)

install-lib: downloads downloads/bundle/lib/neopixel.mpy downloads/bundle/lib/adafruit_minimqtt/adafruit_minimqtt.mpy \
		downloads/bundle/lib/adafruit_fancyled/adafruit_fancyled.mpy
	cd downloads/bundle/lib && \
	curl $(VERBOSE) -u :$(CIRCUITPY_WEB_API_PASSWORD) --create-dirs --location --location-trusted \
		--request PUT $(CPURL)/fs/lib/adafruit_fancyled \
		--request PUT $(CPURL)/fs/lib/adafruit_minimqtt \
		--upload-file adafruit_fancyled/adafruit_fancyled.mpy $(CPURL)/fs/lib/adafruit_fancyled/adafruit_fancyled.mpy \
		--upload-file adafruit_fancyled/__init__.py $(CPURL)/fs/lib/adafruit_fancyled/__init__.py \
		--upload-file adafruit_minimqtt/adafruit_minimqtt.mpy $(CPURL)/fs/lib/adafruit_minimqtt/adafruit_minimqtt.mpy \
		--upload-file adafruit_minimqtt/matcher.mpy $(CPURL)/fs/lib/adafruit_minimqtt/matcher.mpy \
		--upload-file adafruit_minimqtt/__init__.py $(CPURL)/fs/lib/adafruit_minimqtt/__init__.py \
		--upload-file neopixel.mpy $(CPURL)/fs/lib/neopixel.mpy

install-circuitpython: downloads downloads/adafruit-circuitpython-adafruit_feather_huzzah32-en_US-8.0.0-beta.4.bin
	esptool.py --port /dev/tty.usbserial-* erase_flash
	esptool.py --port /dev/tty.usbserial-* write_flash -z 0x0 \
    	~/PycharmProjects/firefly/downloads/adafruit-circuitpython-adafruit_feather_huzzah32-en_US-8.0.0-beta.4.bin

get-cp-info:
	test -d downloads || mkdir downloads
	cd downloads && curl $(VERBOSE) --location --location-trusted \
		-O $(CPURL)/cp/devices.json \
		-O $(CPURL)/cp/version.json

.gitignore:
	curl https://www.toptal.com/developers/gitignore/api/python,circuitpython,git,virtualenv,macos,vim,pycharm -o .gitignore
	printf "\n# ignore the downloads directory\ndownloads\n" >> .gitignore
	printf "\n# ignore version.py that updates each install\nversion.py\n" >> .gitignore
	printf "\n# ignore .install-* files that tracks installation\n.install-*\n" >> .gitignore

downloads:
	test -d downloads || mkdir downloads
	cd downloads && curl --location --progress-bar \
		-O https://downloads.circuitpython.org/bin/feather_m0_express/en_US/adafruit-circuitpython-feather_m0_express-en_US-7.3.3.uf2 \
		-O https://downloads.circuitpython.org/bin/adafruit_feather_huzzah32/en_US/adafruit-circuitpython-adafruit_feather_huzzah32-en_US-8.0.0-beta.4.bin \
		-O https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases/download/20221122/adafruit-circuitpython-bundle-8.x-mpy-20221122.zip \
		&& unzip adafruit-circuitpython-bundle-8.x-mpy-20221122.zip && \
		ln -s adafruit-circuitpython-bundle-8.x-mpy-20221122 bundle

clean:
	rm -fr __pycache__ version.py downloads .install-*.py
