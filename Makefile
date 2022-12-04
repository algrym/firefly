 
# firefly Makefile
# 
# https://docs.circuitpython.org/en/latest/docs/workflows.html#get
#

# Location to write files onto the Pi Pico W, pre-CircuitPython
UF2_DIR=/Volumes/RPI-RP2

# Location to write files onto the Pi Pico W, post-CircuitPython
CIRCUIT_PYTHON_DIR=/Volumes/CIRCUITPY

CODEPY_LIB_DIR=$(CIRCUIT_PYTHON_DIR)/lib

# No config below this line
all: install install-libs .gitignore

install: .install-all

.install-all: boot.py code.py firefly.py version.py
	rsync -avlC $? $(CIRCUIT_PYTHON_DIR) && touch $@

version.py: code.py firefly.py
	date -r $< "+__version__ = %'%Y-%m-%d %H:%M:%S%'" > $@

install-libs: .install-libs

.install-libs: downloads/bundle
	cd downloads/bundle/lib && \
	rsync -avlC \
		neopixel.mpy \
		adafruit_ticks.mpy \
		adafruit_debouncer.mpy \
		adafruit_minimqtt \
		adafruit_fancyled \
			$(CODEPY_LIB_DIR) && \
				touch ../../../$@

.gitignore:
	curl https://www.toptal.com/developers/gitignore/api/python,circuitpython,git,virtualenv,macos,vim,pycharm -o .gitignore
	printf "\n# ignore the downloads directory\ndownloads\n" >> .gitignore
	printf "\n# ignore version.py that updates each install\nversion.py\n" >> .gitignore
	printf "\n# ignore .install-* files that tracks installation\n.install-*\n" >> .gitignore

downloads/bundle:
	test -d downloads || mkdir downloads
	cd downloads && curl --location --progress-bar \
        -O https://downloads.circuitpython.org/bin/raspberry_pi_pico_w/en_US/adafruit-circuitpython-raspberry_pi_pico_w-en_US-8.0.0-beta.4.uf2 \
		-O https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases/download/20221122/adafruit-circuitpython-bundle-8.x-mpy-20221122.zip \
		&& unzip adafruit-circuitpython-bundle-8.x-mpy-20221122.zip && \
		ln -s adafruit-circuitpython-bundle-8.x-mpy-20221122 bundle

clean:
	rm -fr __pycache__ version.py downloads .install-*.py
