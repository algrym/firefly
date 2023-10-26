# 
# Firefly Makefile for huzzah32
# 
# https://docs.circuitpython.org/en/latest/docs/workflows.html#get
#

# URL to access circuitpython hardware
#   Use CPURL environment variable if its set
CPURL := $(if $(CPURL),$(CPURL),http://circuitpython.local)

# the web api login password
CIRCUITPY_WEB_API_PASSWORD := $(if $(CIRCUITPY_WEB_API_PASSWORD),$(CIRCUITPY_WEB_API_PASSWORD),REDACTED_FOR_GITHUB)

# Path to local serial port for ESPTool
CPPORT := $(if $(CPPORT),$(CPPORT),/dev/tty.usbserial-*)

# Comment out if you don't want to see curl activity
VERBOSE := $(if $(VERBOSE), $(VERBOSE),)

# Flags for esptool.py
ESPTOOL_FLAGS=--port /dev/tty.usbserial-*

# information for downloads
CIRCUIT_PYTHON_BOARD=adafruit_feather_huzzah32
#   use "bin" for serial installs like ESP32
#   use "uf2" for filesystem installs like Pi Pico
#CIRCUIT_PYTHON_EXT=uf2
CIRCUIT_PYTHON_EXT=bin
CIRCUIT_PYTHON_VER=8.2.7
CIRCUIT_PYTHON_LIB_VER=8.x
CIRCUIT_PYTHON_LIB_DATE=20231024

# No config below this line
all: install .gitignore

install: .install-version.py .install-boot.py .install-code.py .install-firefly.py

version.py: code.py firefly.py
	date -r code.py "+__version__ = %'%Y-%m-%d %H:%M:%S%'" > version.py

.install-%.py: %.py
	curl $(VERBOSE) -u :$(CIRCUITPY_WEB_API_PASSWORD) --create-dirs --location --location-trusted \
		--upload-file $< $(CPURL)/fs/$< \
	  	&& touch $(@)

install-wipe-huzzah32:
	esptool.py ${ESPTOOL_FLAGS} erase_flash

install-circuitpython: downloads
	esptool.py ${ESPTOOL_FLAGS} \
		write_flash -z 0x0 \
		downloads/adafruit-circuitpython-${CIRCUIT_PYTHON_BOARD}-en_US-$(CIRCUIT_PYTHON_VER).${CIRCUIT_PYTHON_EXT}

# TODO: this won't create directories on the device, unfortunately
install-lib: downloads \
	downloads/bundle/lib/neopixel.mpy \
	downloads/bundle/lib/adafruit_minimqtt/adafruit_minimqtt.mpy \
 	downloads/bundle/lib/adafruit_fancyled/adafruit_fancyled.mpy
	cd downloads/bundle/lib && \
	curl $(VERBOSE) -u :$(CIRCUITPY_WEB_API_PASSWORD) --create-dirs --location --location-trusted \
		--upload-file adafruit_fancyled/adafruit_fancyled.mpy $(CPURL)/fs/lib/adafruit_fancyled/adafruit_fancyled.mpy \
		--upload-file adafruit_fancyled/__init__.py $(CPURL)/fs/lib/adafruit_fancyled/__init__.py \
		--upload-file adafruit_minimqtt/adafruit_minimqtt.mpy $(CPURL)/fs/lib/adafruit_minimqtt/adafruit_minimqtt.mpy \
		--upload-file adafruit_minimqtt/matcher.mpy $(CPURL)/fs/lib/adafruit_minimqtt/matcher.mpy \
		--upload-file adafruit_minimqtt/__init__.py $(CPURL)/fs/lib/adafruit_minimqtt/__init__.py \
		--upload-file neopixel.mpy $(CPURL)/fs/lib/neopixel.mpy
	

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

downloads: \
	downloads/adafruit-circuitpython-${CIRCUIT_PYTHON_BOARD}-en_US-$(CIRCUIT_PYTHON_VER).${CIRCUIT_PYTHON_EXT} \
	downloads/adafruit-circuitpython-bundle-$(CIRCUIT_PYTHON_LIB_VER)-mpy-$(CIRCUIT_PYTHON_LIB_DATE).zip

downloads/adafruit-circuitpython-bundle-$(CIRCUIT_PYTHON_LIB_VER)-mpy-$(CIRCUIT_PYTHON_LIB_DATE).zip:
	test -d downloads || mkdir downloads
	curl $(VERBOSE) --location https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases/download/$(CIRCUIT_PYTHON_LIB_DATE)/adafruit-circuitpython-bundle-$(CIRCUIT_PYTHON_LIB_VER)-mpy-$(CIRCUIT_PYTHON_LIB_DATE).zip -o $(@)
	unzip $(@) -d downloads/
	cd downloads && ln -sf adafruit-circuitpython-bundle-$(CIRCUIT_PYTHON_LIB_VER)-mpy-$(CIRCUIT_PYTHON_LIB_DATE) bundle

downloads/adafruit-circuitpython-${CIRCUIT_PYTHON_BOARD}-en_US-$(CIRCUIT_PYTHON_VER).${CIRCUIT_PYTHON_EXT}:
	test -d downloads || mkdir downloads
	curl $(VERBOSE) --location https://downloads.circuitpython.org/bin/${CIRCUIT_PYTHON_BOARD}/en_US/adafruit-circuitpython-${CIRCUIT_PYTHON_BOARD}-en_US-$(CIRCUIT_PYTHON_VER).${CIRCUIT_PYTHON_EXT} -o $(@)

requirements.txt:
	pip freeze > $(@)

clean:
	rm -fr __pycache__ version.py downloads .install-*.py
