import network
import asyncio
from micropython import const


class LogLevel:
    INFO = const(0)
    WARNING = const(1)
    ERROR = const(2)

    text = ["info", "warning", "error"]


class EzWiFi:
    def __init__(self, **kwargs):
        get = kwargs.get

        self._ssid = get("ssid")
        self._password = get("password", "")

        if not self._ssid and not self._password:
            self._ssid, self._password = self._secrets()
        elif self._password and not self._ssid:
            raise ValueError("ssid required!")

        self._last_error = None

        self._verbose = get("verbose", False)

        self._events = {
            "connected": get("connected", None),
            "failed": get("failed", None),
            "info": get("info", None),
            "warning": get("warning", None),
            "error": get("error", None)
        }

        self._if = network.WLAN(network.STA_IF)
        self._if.active(True)
        # self._if.config(pm=0xa11140) # TODO: ???
        self._statuses = {v: k[5:] for (k, v) in network.__dict__.items() if k.startswith("STAT_")}

    def _callback(self, handler_name, *args, **kwargs):
        handler = self._events.get(handler_name, None)
        if callable(handler):
            handler(self, *args, **kwargs)
            return True
        return False

    def _log(self, text, level=LogLevel.INFO):
        self._callback(LogLevel.text[level], text) or (self._verbose and print(text))

    def on(self, handler_name):
        if handler_name not in self._events.keys():
            raise ValueError(f"Invalid event: \"{handler_name}\"")

        def _on(handler):
            self._events[handler_name] = handler

        return _on

    def error(self):
        if self._last_error is not None:
            return self._last_error, self._statuses[self._last_error]
        return None, None

    async def connect(self, timeout=60, retries=10):
        for retry in range(retries):
            self._log(f"Connecting to {self._ssid} (Attempt {retry + 1})")
            try:
                self._if.connect(self._ssid, self._password)
                if await asyncio.wait_for(self._wait_for_connection(), timeout):
                    return True

            except asyncio.TimeoutError:
                self._log("Attempt failed...", LogLevel.WARNING)

        self._callback("failed")
        return False

    async def _wait_for_connection(self):
        while not self._if.isconnected():
            self._log("Connecting...")
            status = self._if.status()
            if status in [network.STAT_CONNECT_FAIL, network.STAT_NO_AP_FOUND, network.STAT_WRONG_PASSWORD]:
                self._log(f"Connection failed with: {self._statuses[status]}", LogLevel.ERROR)
                self._last_error = status
                return False
            await asyncio.sleep_ms(1000)
        self._log(f"Connected! IP: {self.ipv4()}")
        self._callback("connected")
        return True

    def ipv4(self):
        return self._if.ipconfig("addr4")[0]

    def ipv6(self):
        return self._if.ipconfig("addr6")[0][0]

    def isconnected(self):
        return self._if.isconnected()

    def _secrets(self):
        try:
            from secrets import WIFI_SSID, WIFI_PASSWORD
            if not WIFI_SSID:
                raise ValueError("secrets.py: WIFI_SSID is empty!")
            if not WIFI_PASSWORD:
                raise ValueError("secrets.py: WIFI_PASSWORD is empty!")
            return WIFI_SSID, WIFI_PASSWORD
        except ImportError:
            raise ImportError("secrets.py: missing or invalid!")


def connect(**kwargs):
    return asyncio.get_event_loop().run_until_complete(EzWiFi(**kwargs).connect(retries=kwargs.get("retries", 10)))
