 
# firefly Makefile
# 
# https://docs.circuitpython.org/en/latest/docs/workflows.html#get
#

# Generic name on the network
CPURL=http://circuitpython.local

# the web api login password
CIRCUITPY_WEB_API_PASSWORD=REDACTED_FOR_GITHUB

# Comment out if you don't want to see curl activity
VERBOSE=-v

# No config below this line
all: push .gitignore

push: boot.py code.py
	date -r code.py "+__version__ = %'%Y-%m-%d %H:%M:%S%'" > version.py
	curl $(VERBOSE) -u :$(CIRCUITPY_WEB_API_PASSWORD) --location --location-trusted \
		--upload-file version.py $(CPURL)/fs/version.py \
		--upload-file boot.py $(CPURL)/fs/boot.py \
		--upload-file code.py $(CPURL)/fs/code.py

push-lib: downloads downloads/bundle/lib/neopixel.mpy
	cd downloads/bundle/lib && \
	curl $(VERBOSE) -u :$(CIRCUITPY_WEB_API_PASSWORD) --location --location-trusted \
		--upload-file neopixel.mpy $(CPURL)/fs/lib/neopixel.mpy

get-cp-info:
	test -d downloads || mkdir downloads
	cd downloads && curl $(VERBOSE) --location --location-trusted \
		-O $(CPURL)/cp/devices.json \
		-O $(CPURL)/cp/version.json

.gitignore:
	curl https://www.toptal.com/developers/gitignore/api/python,circuitpython,git,virtualenv,macos,vim,pycharm -o .gitignore
	printf "\n# ignore the downloads directory\ndownloads\n" >> .gitignore
	printf "\n# ignore version.py that updates each push\nversion.py\n" >> .gitignore

downloads:
	test -d downloads || mkdir downloads
	cd downloads && curl --location --progress-bar \
		-O https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases/download/20221122/adafruit-circuitpython-bundle-8.x-mpy-20221122.zip \
		-O https://downloads.circuitpython.org/bin/adafruit_feather_huzzah32/en_US/adafruit-circuitpython-adafruit_feather_huzzah32-en_US-8.0.0-beta.4.bin && \
		unzip adafruit-circuitpython-bundle-8.x-mpy-20221122.zip && \
		ln -s adafruit-circuitpython-bundle-8.x-mpy-20221122 bundle

clean:
	rm -fr __pycache__ version.py downloads
