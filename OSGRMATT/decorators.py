import json
from functools import wraps
from time import sleep
import logging

logger = logging.getLogger(__name__)


def work_in_new_tab(func):
    """For work in new tab and close it."""
    @wraps(func)
    def switch(*args, **kwargs):
        current_handle = args[0].driver.current_window_handle
        logger.info("Current handle: %s", current_handle)
        args[0].driver.execute_script("window.open();")
        args[0].driver.switch_to.window(args[0].driver.window_handles[-1])
        sleep(3)

        res = func(*args, **kwargs)

        args[0].driver.execute_script("window.close();")
        args[0].driver.switch_to.window(current_handle)

        return res

    return switch


def fix_used_memory(func):
    """usedJSHeapSize to log"""
    @wraps(func)
    def fix_memory(*args, **kwargs):
        before_usage = args[0].driver.execute_script("""var mem = window.performance.memory.usedJSHeapSize / 
        1048576; return mem;""")
        logger.info("Before method %s runs memory usage: %s Mb", func.__name__, before_usage)

        res = func(*args, **kwargs)

        after_usage = args[0].driver.execute_script("""var mem = window.performance.memory.usedJSHeapSize / 
        1048576; return mem;""")
        logger.info("After method %s runs memory usage: %s Mb", func.__name__, after_usage)

        return res

    return fix_memory


def check_socket_data(func):
    """Get socket data from Network DevTools tab"""
    @wraps(func)
    def check_socket(*args, **kwargs):
        res = func(*args, **kwargs)
        for websocket_data in args[0].driver.get_log('performance'):
            ws_json = json.loads((websocket_data['message']))
            if ws_json["message"]["method"] == "Network.webSocketFrameReceived":
                logger.info("Received socket message: %s", str(ws_json["message"]["params"]["timestamp"]) +
                            ws_json["message"]["params"]["response"]["payloadData"])
            if ws_json["message"]["method"] == "Network.webSocketFrameSent":
                logger.info("Sent socket message: %s", ws_json["message"]["params"]["response"]["payloadData"])

        return res

    return check_socket


def upload_headers(func):
    @wraps(func)
    def work_with_headers(self, *args, **kwargs):
        logger.info("Remove headers 'accept' and 'Content-Type'")
        self._headers.pop('accept')
        self._headers.pop('Content-Type')

        res = func(self, *args, **kwargs)

        logger.info("Return headers 'accept' and 'Content-Type' and delete 'X-File-Size'")
        self._headers.pop('X-File-Size')
        self._headers.pop('X-File-Size-From')
        self._headers['accept'] = 'text/plain'
        self._headers['Content-Type'] = 'application/json-patch+json'

        return res
    return work_with_headers
