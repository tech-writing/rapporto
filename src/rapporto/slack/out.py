import logging
import os

from pueblo import setup_logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logger = logging.getLogger(__name__)


class SlackOut:
    def __init__(self):
        self.client = WebClient(token=os.environ["SLACK_TOKEN"])

    def send(self, channel: str, message: str):
        try:
            response = self.client.chat_postMessage(channel=channel, text=message)
            print(response)
        except SlackApiError as e:
            logger.error(f"{e.response['error']}. Status code: {e.response.status_code}")


if __name__ == "__main__":
    setup_logging()
    out = SlackOut()
    out.send(channel="#sig-automation-testdrive", message="Hello world!")
