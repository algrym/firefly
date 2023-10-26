#!/usr/bin/env python3
# watch-serial.py - the worst websocket client ever

import asyncio
import websockets
import string
from datetime import datetime

printable = string.ascii_letters + string.digits + string.punctuation + ' '
def hex_escape(s):
    return ''.join(c if c in printable else r'\x{0:02x}'.format(ord(c)) for c in s)


async def client():
    # TODO: Make this work with HTTP 307 from circuitpython.local
    uri = "ws://:REDACTED_FOR_GITHUB@cpy-abc123.local/cp/serial/"
    async for websocket in websockets.connect(uri):
        try:
            print (f"Websocket connection open.  Listening ...")
            loop = asyncio.get_running_loop()
            async for message in websocket:
                if not message or message.isspace():
                    continue;
                message = message.strip('\r\n')
                timestamp = datetime.now().strftime("%x %X")
                print (f"{timestamp} {hex_escape(message)}")
        except websockets.ConnectionClosed:
            print (f"Websocket connection closed.  Reopening.")
            await websocket.close()
            continue

asyncio.run(client())
