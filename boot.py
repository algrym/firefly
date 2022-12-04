#!/usr/bin/env python3
# boot.py
import os
import wifi

print(f"# Connecting to WiFi: {os.getenv('WIFI_SSID')}")
wifi.radio.connect(os.getenv('WIFI_SSID'), os.getenv('WIFI_PASSWORD'))
print("# My MAC addr: %02X:%02X:%02X:%02X:%02X:%02X" % tuple(wifi.radio.mac_address))
print("# My IP address is", wifi.radio.ipv4_address)