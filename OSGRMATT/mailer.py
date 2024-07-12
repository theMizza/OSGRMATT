from exchangelib import Credentials, Account

import logging

logger = logging.getLogger(__name__)


class MailerException(Exception):
    ...


class MailReceiver:
    def __init__(self, username: str, password: str, primary_smtp_address: str):
        self.credentials = Credentials(username, password)
        self.account = Account(primary_smtp_address, credentials=self.credentials, autodiscover=True)

    def get_last_inbox_by_params(self, params: str):
        """
        Get last email
        :param params: str
        :return:
        """
        for item in self.account.inbox.all().order_by("-datetime_received")[:1]:
            if params in item.subject:
                return item.body
            else:
                raise MailerException("No email!")
