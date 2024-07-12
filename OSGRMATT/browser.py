import shutil
from pathlib import Path
from selenium import webdriver
from selenium.common import SessionNotCreatedException
from selenium.webdriver.chrome.options import Options as Chromeoptions
from selenium.webdriver.remote.file_detector import FileDetector
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager, ChromeType
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from OSGRMATT.utils import get_used_memory

import logging

logger = logging.getLogger(__name__)
logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)


def get_download_dir():
    """Возвращает путь к папке для скачивания файлов. Не используется."""
    base_dir = Path(__file__).parent.parent.resolve()
    return base_dir / "tmp/downloads"


class LocalFileDetector(FileDetector):
    """Класс отвечает за скачивание и загрузку локальных файлов при использовании ноды грида. Не используется."""
    def is_available(self):
        pass

    def file_detected(self, file_path):
        download_dir = get_download_dir()
        new_file_path = download_dir / Path(file_path).name
        shutil.copyfile(file_path, str(new_file_path))
        logger.info("File saved to path: %s", new_file_path)
        return True

    def is_local_file(self, file_path):
        pass


class Browser:
    def setup_options(self,
                      arguments: list = None,
                      experimental_options: list = None,
                      capabilities: list = None):
        options = Chromeoptions()
        if arguments:
            for argument in arguments:
                options.add_argument(argument)
        if experimental_options:
            for option in experimental_options:
                for key, value in option.items():
                    options.add_experimental_option(key, value)
        if capabilities:
            for capability in capabilities:
                for key, value in capability.items():
                    options.set_capability(key, value)

        return options

    def setup_driver(self, options: Chromeoptions = None, command_executor: str = None):
        logger.info("Setup driver")
        if options is None:
            options = Chromeoptions()
        if command_executor:
            options.add_argument('--headless')
            options.add_argument('-lang=ru')
            """
            Опция ниже не тестировалась. Подробнее об опции:
            https://www.selenium.dev/documentation/webdriver/drivers/remote_webdriver/#enable-downloads-in-the-grid
            options.enable_downloads = True
            """
            cloud_options = {'build': "build_3",
                             'name': "test_abc3",
                             "browserVersion": "120.0.6099.130"}
            logger.info("Cloud options: %s", cloud_options)
            options.set_capability('cloud:options', cloud_options)
            try:
                driver = webdriver.Remote(command_executor=command_executor,
                                          options=options)
            except SessionNotCreatedException as e:
                logger.error("Create session error: %s", e.msg)
                logger.error("Create session error stacktrace: %s", e.stacktrace)
                raise TypeError("Driver creation error: %s", e.msg)
        else:
            service = Service(ChromeDriverManager(chrome_type=ChromeType.GOOGLE).install())
            driver = webdriver.Chrome(service=service, options=options)

        return driver


class SeleniumLogic:
    def __init__(self, driver):
        self.driver = driver

    def click_element(self, by, value):
        WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((by, value))).click()

    def click_element_fast(self, by, value):
        WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((by, value))).click()

    def enter_text(self, by, value, text):
        element = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((by, value)))
        element.clear()
        element.send_keys(text)

    def enter_text_by_letter(self, by, value, text):
        element = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((by, value)))
        element.clear()
        for i in text:
            element.send_keys(i)
            sleep(0.25)

    def enter_text_in_hidden_input(self, by, value, text):
        """Enter path for upload file"""
        element = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((by, value)))
        element.send_keys(text)

    def find_element_fast(self, by, value):
        return WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((by, value)))

    def find_element(self, by, value):
        return WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((by, value)))

    def find_element_slow(self, by, value):
        return WebDriverWait(self.driver, 180).until(EC.presence_of_element_located((by, value)))

    def find_elements(self, by, value):
        """find all presence elements with same locator"""
        return WebDriverWait(self.driver, 30).until(EC.presence_of_all_elements_located((by, value)))

    def find_visible_elements(self, by, value):
        """find all visible elements with same locator"""
        return WebDriverWait(self.driver, 30).until(EC.visibility_of_all_elements_located((by, value)))

    def find_element_instantly(self, by, value):
        return self.driver.find_element(by, value)

    def check_visible_element(self, by, value):
        return WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((by, value)))

    def check_visible_fast(self, by, value):
        return WebDriverWait(self.driver, 1).until(EC.visibility_of_element_located((by, value)))

    def wait_invisibility_of_element(self, by, value):
        try:
            WebDriverWait(self.driver, 30).until(EC.invisibility_of_element_located((by, value)))
        except TimeoutException:
            return 'need more TO'

    def wait_invisibility_of_element_slow(self, by, value):
        try:
            WebDriverWait(self.driver, 180).until(EC.invisibility_of_element_located((by, value)))
        except TimeoutException:
            return 'need more TO'

    def send_keys_to_element(self, by, value, keys):
        element = self.driver.find_element(by, value)
        element.send_keys(keys)

    def send_keys_and_press_enter(self, locator, keys):
        element = self.find_element(*locator)
        element.send_keys(keys)
        element.send_keys(Keys.ENTER)

    def get_alert_info(self, by, value):
        alert = self.find_element(by, value).text
        return alert

    def get_alert_info_slow(self, by, value):
        alert = self.find_element_slow(by, value).text
        return alert

    def press_escape(self):
        ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()

    def click_element_parametrized(self, contains_text: str):
        dialog_xpath = f"//*[contains(text(), '{contains_text}')]"
        self.click_element(By.XPATH, dialog_xpath)

    def get_cookies(self):
        return self.driver.get_cookies()

    def get_bearer(self):
        return self.driver.execute_script("return window.localStorage.getItem('token');")

    def ctrl_f5(self):
        ActionChains(self.driver).key_down(Keys.CONTROL).send_keys(Keys.F5).key_up(Keys.CONTROL).perform()

    def get_used_memory(self):
        used_memory = get_used_memory(self.driver)
        logger.info("Used memory in the end: %s Mb", used_memory)
        return str(used_memory)

    def _from_list_of_dicts_to_str(self, data: list):
        string = ''
        for i in data:
            for key, value in i.items():
                string += f'_{key}_{value}_'

        return string

    def check_lists_of_dicts(self, list_a: list, list_b: list):
        first_string = self._from_list_of_dicts_to_str(list_a)
        second_string = self._from_list_of_dicts_to_str(list_b)

        return first_string == second_string

    def tear_down(self):
        self.driver.quit()
