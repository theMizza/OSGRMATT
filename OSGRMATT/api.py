import json
import logging
import requests
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class APIBase:
    """Base class for API"""
    _BASE_DIR = Path(__file__).parent.parent.resolve()
    _headers = {'accept': 'text/plain',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
                'Content-Type': 'application/json-patch+json'}

    @property
    def headers(self):
        return self._headers

    @property
    def base_dir(self):
        return self._BASE_DIR

    def _post(self, url: str, body, return_error: bool = False, return_file: bool = False):
        """POST request impl"""
        response = requests.post(url, data=body, headers=self.headers)
        if response.status_code == 200:
            if return_file is True:
                return response.content
            else:
                return json.loads(response.content)
        else:
            if return_error is True:
                error = self._handle_error(response)
                logger.error("Url: %s POST Error %s: %s", url, response.status_code, error)
                return f'{url} - {response.status_code}: {error}'
            else:
                logger.error("Url: %s POST Error %s: %s", url, response.status_code, response.content)
                raise ValueError(f'{url} - {response.status_code}: {response.content}')

    def _get(self, url: str, return_error: bool = False, return_file: bool = False):
        """GET request impl"""
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            if return_file is True:
                return response.content
            else:
                return json.loads(response.content)
        else:
            if return_error is True:
                error = self._handle_error(response)
                logger.error("Url: %s GET Error %s: %s", url, response.status_code, error)
                return f'{url} - {response.status_code}: {error}'
            else:
                logger.error("Url: %s GET Error %s: %s", url, response.status_code, response.content)
                raise ValueError(f'{url} - {response.status_code}: {response.content}')

    def _delete(self, url: str, data: json = None, return_error: bool = False):
        response = requests.delete(url=url, data=data, headers=self.headers)
        if response.status_code == 200:
            return json.loads(response.content)
        else:
            if return_error is True:
                error = self._handle_error(response)
                logger.error("Url: %s DELETE Error %s: %s", url, response.status_code, error)
                return f'{url} - {response.status_code}: {error}'
            else:
                logger.error("Url: %s DELETE Error %s: %s", url, response.status_code, response.content)
                raise ValueError(f'{url} - {response.status_code}: {response.content}')

    def _put(self, url: str, body: json, return_error: bool = False):
        """PUT request impl"""
        response = requests.put(url, data=body, headers=self.headers)
        if response.status_code == 200:
            return json.loads(response.content)
        else:
            if return_error is True:
                error = self._handle_error(response)
                logger.error("Url: %s PUT Error %s: %s", url, response.status_code, error)
                return f'{url} - {response.status_code}: {error}'
            else:
                logger.error("Url: %s PUT Error %s: %s", url, response.status_code, response.content)
                raise ValueError(f'{url} - {response.status_code}: {response.content}')

    def _send_file(self, url: str, file_name: str, return_error: bool = False):
        """Send file impl"""
        file = Path(f'{self.base_dir}/test_data/{file_name}')
        self._headers['X-File-Size-From'] = '0'
        self._headers['X-File-Size'] = str(file.stat().st_size)
        with open(file, 'rb') as send_file:
            data = send_file.read()
            logger.info("File name: %s", file.name)
            send_data = {'file': (file_name, data, 'multipart/form-data')}
            logger.info("Request headers: %s", self.headers)
            response = requests.post(url, files=send_data, headers=self.headers)
            if response.status_code == 200:
                return json.loads(response.content)
            else:
                if return_error is True:
                    error = self._handle_error(response)
                    logger.error("Url: %s SEND FILE/POST Error %s: %s",
                                 url, response.status_code, error)
                    return f'{url} - {response.status_code}: {error}'
                else:
                    logger.error("Url: %s POST Error %s: %s", url, response.status_code, response.content)
                    raise ValueError(f'{url} - {response.status_code}: {response.content}')

    def _handle_error(self, response):
        """Errors handler"""
        try:
            return json.loads(response.content)
        except json.decoder.JSONDecodeError:
            return response.content

    def _to_json(self, file: str, data: json):
        """Save response to json"""
        with open(f'{self.base_dir}/response_jsons/{file}', 'w+', encoding='utf-8') as file:
            json.dump(data, file, indent=2)

    def _compare_lists(self, list_a: list, list_b: list, equal: bool = False, to_log: bool = True):
        """List comparor"""
        if to_log is True:
            logger.info("Assert data in %s with data in %s", list_a, list_b)
        flag = True
        if len(list_a) != len(list_b):
            flag = False
        else:
            for i in range(len(list_a)):
                if list_a[i] != list_b[i]:
                    flag = False
                    break
        if equal is True:
            assert flag is True, f"Ожидаем, что при ставнении списков flag True, Реально flag {flag}"
        else:
            assert flag is False, f"Ожидаем, что при ставнении списков flag False, Реально flag {flag}"

    def get_now_datetime(self):
        """Get datetime now"""
        return datetime.now()

    def get_timediff(self, t1: datetime, t2: datetime):
        """Get diff between t1 and t2"""
        return int((t2 - t1).total_seconds())

    def auth(self, auth_url: str, email: str, password: str, token_key: str):
        """Auth method"""
        logger.info("Try to auth with acc %s & password %s", email, password)
        body = {"email": email, "password": password}
        response = self._post(auth_url, json.dumps(body))
        self._to_json('auth.json', response)
        logger.info("Token: %s", response[token_key])
        if 'Bearer' in response[token_key]:
            token = response[token_key]
        else:
            token = f"Bearer {response[token_key]}"
        self._headers['Authorization'] = token

    def logout(self):
        """Logout method"""
        try:
            self._headers.pop('Authorization')
            logger.info("Logout success!")
        except KeyError:
            logger.warning("You wasn't logged in!")
