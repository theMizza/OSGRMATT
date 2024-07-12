import json
import logging
from time import sleep
import sys
from datetime import datetime


logger = logging.getLogger(__name__)


def process_browser_log_entry(entry):
    """Принимаем даннаые из performance и возвращаем json"""
    response = json.loads(entry['message'])['message']
    return response


def check_requests(driver):
    """
    Функция смотрит в DevTools Chrome в раздел Network.
    Если у запроса ответ не 200 или 204, кладет в лог урл и статус
    """
    statuses = [200, 204, 304]
    for performance_data in driver.get_log('performance'):
        requests_json = process_browser_log_entry(performance_data)
        if requests_json["method"] == "Network.responseReceived":
            if requests_json["params"]["response"]["status"] in statuses:
                pass
            else:
                logger.error("Request Url: %s, status - %s",
                             requests_json["params"]["response"]["url"],
                             requests_json["params"]["response"]["status"])


def notifies_needed():
    """Функция, проверяющая аргументы на наличие --send-notifies (активация отправки уведомлений в ТГ)"""
    if '--send-notifies' in sys.argv:
        logger.info("Notifies are enabled!")
        return True
    else:
        logger.info("Notifies are disabled!")
        return False


def screencast_needed():
    """Функция, проверяющая аргументы на наличие --screencast (запись скринкаста)"""
    if '--screencast' in sys.argv:
        logger.info("Screencast is enabled!")
        return True
    else:
        logger.info("Screencast is disabled!")
        return False


def get_response_data(driver, url: str, wait: int = None):
    """Функция для логгирования ответа от эндпойнта, url которого передаем аргументом"""
    logger.info("Try to get response data for endpoint %s", url)
    if wait:
        sleep(wait)
    browser_log = driver.get_log('performance')
    events = [process_browser_log_entry(entry) for entry in browser_log]
    events = [event for event in events if 'Network.response' in event['method']]
    tmp_event_list = []
    event_list = []
    for event in events:
        try:
            event_type = event['params']['type']
        except Exception:
            event_type = 'None'
        if event_type == 'XHR':
            tmp_event_list.append(event)
    for event in tmp_event_list:
        try:
            event_url = event['params']['response']['url']
        except Exception:
            event_url = "None"
        if url == event_url:
            event_list.append(event)

    if len(event_list) > 0:
        for i in range(len(event_list)):
            response = driver.execute_cdp_cmd('Network.getResponseBody',
                                              {'requestId': event_list[i]["params"]["requestId"]})
            logger.info("Endpoint's %s response: %s", url, response['body'])
    else:
        logger.error("Responses list is empty")


def get_datetime():
    now = datetime.now()
    logger.info("Fixed datetime: %s", now)
    return now


def get_timediff(start_time: datetime, end_time: datetime):
    time_diff = end_time - start_time
    logger.info("Time diff: %s", time_diff)
    return time_diff


def get_used_memory(driver):
    """Смотрим в консоли, сколько памяти загрузил в себя js"""
    return driver.execute_script("""var mem = window.performance.memory.usedJSHeapSize /  1048576; return mem;""")
