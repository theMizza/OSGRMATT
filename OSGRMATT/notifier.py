from telebot import TeleBot
from pathlib import Path
from datetime import datetime

import logging

logger = logging.getLogger(__name__)


class NotifySender:
    def __init__(self, token: str, chat_id: str):
        self._token = token
        self._chat_id = chat_id
        self._bot = TeleBot(self._token)

    @property
    def bot(self):
        return self._bot

    @property
    def chat_id(self):
        return self._chat_id

    def _send_report_file(self, file_path: Path, caption: str, parse_mode: str = 'html'):
        """
        Send file private method
        :param file_path: Path
        :param caption: str
        :param parse_mode: str
        :return:
        """
        try:
            with open(file_path, 'rb') as document:
                self.bot.send_document(chat_id=self.chat_id, document=document, caption=caption, parse_mode=parse_mode)
                document.close()
            logger.info('Report file was send')
        except Exception as ex:
            logger.error("send_notify_files: %s", ex)

    def send_report_file(self, file_path: Path, caption, parse_mode="html"):
        logger.info("Send report file")
        self._send_report_file(file_path, caption, parse_mode)

    def send_screenshot(self, caption: str, parse_mode: str = 'html', delete_after_send: bool = False):
        """
        Send screenshot to tg
        :param caption: str
        :param parse_mode: str
        :param delete_after_send: bool = False
        :return:
        """
        logger.info("Send screenshot")
        base_dir = Path(__file__).parent.resolve()
        path = Path(base_dir / 'tmp/screenshots/last.png')
        self._send_report_file(path, caption, parse_mode)
        if delete_after_send is True:
            path.unlink()

    def send_screencast(self, caption: str, file_name: str, parse_mode: str = "html", delete_after_send: bool = False):
        """
        Send screencast to tg
        :param file_name: str
        :param caption: str
        :param parse_mode: str
        :param delete_after_send: bool = False
        :return:
        """
        logger.info("Send screencast")
        base_dir = Path(__file__).parent.resolve()
        path = Path(base_dir / f'tmp/screencasts/{file_name}')
        self._send_report_file(path, caption, parse_mode)
        if delete_after_send is True:
            path.unlink()

    def send_start_test_message(self, test_name: str, parse_mode: str = "html"):
        """
        Send start of test message
        :param test_name: str
        :param parse_mode: str
        :return:
        """
        try:
            text = f"================================\n" \
                    f"<b>Test of {test_name} starts!</b>\n" \
                    f"<i>Start time: {datetime.now()}</i>"
            self.bot.send_message(self.chat_id, text=text, parse_mode=parse_mode)
        except Exception as ex:
            logger.error("send_message: %s", ex)

    def send_test_status_message(self, message, parse_mode="html"):
        logger.info("Send text message")
        try:
            self.bot.send_message(chat_id=self.chat_id, text=message, parse_mode=parse_mode)
        except Exception as ex:
            logger.error("send_text_message: %s", ex)
