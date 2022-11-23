# This will overwrite local settings when pasted into REPL
f = open('.env', 'w')
f.write("CIRCUITPY_WIFI_SSID='CHANGEME'\n")
f.write("CIRCUITPY_WIFI_PASSWORD='CHANGEME'\n")
f.write("CIRCUITPY_WEB_API_PASSWORD='REDACTED_FOR_GITHUB'\n")
f.close()
