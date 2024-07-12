import pytest
from OSGRMATT.notifier import NotifySender
from datetime import datetime
from bs4 import BeautifulSoup
import json
from pathlib import Path
import os
import dotenv


def pytest_addoption(parser):
    """Добавление опции отправки уведомлений в ТГ"""
    parser.addoption("--send-notifies", action="store_true", default=False, help="Enable Telegram Notifies")
    parser.addoption("--screencast", action="store_true", default=False, help="Enable Screencast Writing")


def check_notifies(config):
    """Проверка опций на наличие --send-notifies"""
    notifies = config.getoption("--send-notifies")
    if notifies:
        return True
    else:
        return False


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    """Данная функция берет из ini название отчета и меняет его на уникальное"""
    base_dir = Path(__file__).parent.resolve()
    if len(config.invocation_params.args) > 0:
        try:
            file_name = config.invocation_params.args[0].split('/')[1].split('.')[0]
        except IndexError:
            file_name = config.invocation_params.args[0]
    else:
        file_name = 'no_args'
    config.option.htmlpath = (f'{base_dir}/html_reports/'
                              f'report_{file_name}_{datetime.now().strftime("%d-%m-%Y %H-%M-%S")}.html')
    alluredir = getattr(config.option, "allure_report_dir", None)
    if not alluredir:
        setattr(config.option, "allure_report_dir", f"{base_dir}/html_reports/'")


def pytest_unconfigure(config):
    """Данная функция срабатывает после тирдауна,
    забирает путь к отчету и отправляет его в нотифай если тест запущен с опцией --send-notifies"""
    notifies = check_notifies(config)
    if notifies:
        dotenv.load_dotenv()
        tg_token = os.getenv('TOKEN')
        chat_id = os.getenv("CHAT_ID")
        notifier = NotifySender(tg_token, chat_id)
        report_path = config.option.htmlpath
        try:
            report_name = config.invocation_params.args[0].split('/')[1].split('.')[0]
        except IndexError:
            report_name = config.invocation_params.args[0]
        """Parse report file"""
        messages = []
        with open(report_path) as file:
            html = file.read()
        soup = BeautifulSoup(html, 'html.parser')
        jdata = soup.find(id="data-container")
        search_data = jdata.get('data-jsonblob')
        search_jdata = json.loads(search_data)
        keys = list(search_jdata['tests'].keys())
        for key in keys:
            for i in search_jdata['tests'][key]:
                test_id = i["testId"].split('::')
                test_name = f"{test_id[1]}::{test_id[2]}"
                if i["result"] == "Passed":
                    result = "✅ Passed"
                elif i["result"] == "Failed":
                    result = "❌ Failed"
                else:
                    result = "❓️ Status N/A ️"
                messages.append(f'{test_name} - {result}')
        statuses = '\n\n'.join(messages)
        message = f"<b>ClientPortal Test Status</b>\n" \
                  f"{statuses}"
        notifier.send_test_status_message(message)
        """Send html report file"""
        caption = f"<b>ClientPortal HTML Report</b>\n" \
                  f"<i>{report_name}</i>\n\n" \
                  f"=========================="
        notifier.send_report_file(report_path, caption)
