#
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

get-cp-info:
	curl $(VERBOSE) --location --location-trusted \
		-O $(CPURL)/cp/devices.json \
		-O $(CPURL)/cp/version.json

.gitignore:
	curl https://www.toptal.com/developers/gitignore/api/python,circuitpython,git,virtualenv,macos,vim,pycharm -o .gitignore
	printf "\n# ignore the downloads directory\ndownloads\n" >> .gitignore
	printf "\n# ignore version.py that updates each push\nversion.py\n" >> .gitignore

clean:
	rm -fr __pycache__ version.py devices.json version.json
