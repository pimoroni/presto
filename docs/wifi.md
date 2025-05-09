# EzWiFi <!--omit in toc-->

- [EzWiFi ](#ezwifi-)
  - [Easy EzWiFi](#easy-ezwifi)
  - [EzWiFi Class](#ezwifi-class)
    - [Asyncio](#asyncio)
    - [Connect Options](#connect-options)
    - [Handlers](#handlers)
    - [Other Functions](#other-functions)

EzWiFi, or Easy WiFi, is a helper module to get you connected to wireless networks.

It's based around the use of `secrets.py`, a Python file that very simply tucks
your wireless SSID and password away for use across multiple scripts.

`secrets.py` looks like this:

```python
WIFI_SSID = "your_ssid"
WIFI_PASSWORD = "your_password"
```

## Easy EzWiFi

The easiest way to use EzWiFi is with the blocking `connect` method, like so:

```python
import ezwifi

ezwifi.connect()
```

This will load login details from `secrets.py` and quietly connect to your
wireless network. It will try ten times by default with an overall timeout
of 60 seconds.

If you need a little more debugging information you can
supply a log handler like so:

```python
import ezwifi

ezwifi.connect(verbose=True)
```

If you need specific log messages, want to perform an action or display a message
on screen when connected/failed then you can supply:

* `connected` - Called when a connection is established (with no message).
* `failed` - Called when the connection fails.
* `info` - Called with basic info messages.
* `warning` - Called when a connection attempt fails (and in other cases in future).
* `error` - Called when a connection totally fails (and in other cases in future).
* `failed` - Called when a connection fails (with no message).

For example, this will call a function if/when the connection succeeds or fails:

```python
import ezwifi


def connect_handler(wifi):
    pass


def failed_handler(wifi):
    pass


ezwifi.connect(connected=connect_handler, failed=failed_handler)
```

## EzWiFi Class

EzWiFi is also available as a class if you need to integrate with async.

Create an instance with:

```python
from ezwifi import EzWiFi

wifi = EzWiFi()
```

You can then use the async `connect()` method, if you're using the class and
want this to run in synchronous code you'll need to:

```python
import asyncio

asyncio.get_event_loop().run_until_complete(wifi.connect())
```

### Asyncio

With asyncio you can do other things while waiting for WiFi to connect, like so:

```python
import asyncio
from ezwifi import EzWiFi

wifi = EzWiFi()


@wifi.on("connected")
async def handle_connect(wifi):
    print("Connected!")


@wifi.on("failed")
async def handle_connect(wifi):
    print("Failed!")


async def main():
    wifi_task = asyncio.create_task(wifi.connect())
    while True:
        print("Main loop...")
        await asyncio.sleep_ms(1000)


asyncio.run(main())
```

### Connect Options

You can supply an optional `ssid`, `password`, `timeout` and number of retries to
`connect()`:

### Handlers

If you need specific log messages, want to perform an action or display a message
on screen when connected/failed then you use the following handlers:

* `connected` - Called when a connection is established (with no message).
* `failed` - Called when the connection fails.
* `info` - Called with basic info messages.
* `warning` - Called when a connection attempt fails (and in other cases in future).
* `error` - Called when a connection totally fails (and in other cases in future).
* `failed` - Called when a connection fails (with no message).

These can be supplied to EzWiFi as an argument, eg:

```python
import asyncio
from ezwifi import EzWiFi


async def info_handler(wifi, message):
    print(message)


wifi = EzWiFi(info=info_handler)


async def main():
    wifi_task = asyncio.create_task(wifi.connect())
    while True:
        print("Main loop...")
        await asyncio.sleep_ms(1000)


asyncio.run(main())
```

Or by using the `wifi.on` decorator:

```python
import asyncio
from ezwifi import EzWiFi

wifi = EzWiFi()


@wifi.on("info")
async def info_handler(wifi, message):
    print(message)


async def main():
    wifi_task = asyncio.create_task(wifi.connect())
    while True:
        print("Main loop...")
        await asyncio.sleep_ms(1000)


asyncio.run(main())
```

### Other Functions

* `ipv4` - returns the ipv4 address, shortcut for `if.ipconfig("addr4")[0]`
* `ipv6` - returns the first ipv6 address, shortcut for `if.ipconfig("addr6")[0][0]`
* `isconnected` - returns the connection status
