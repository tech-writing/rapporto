"""
https://api.slack.com/methods/chat.postMessage
https://api.slack.com/surfaces/messages#threading
https://api.slack.com/messaging/retrieving#finding_conversation
https://api.slack.com/methods/conversations.history
"""

import logging
import typing as t

import attr
from attrs import define
from furl import furl
from munch import Munch, munchify
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logger = logging.getLogger(__name__)


@define
class SlackUrl:
    """
    Manage a Slack URL.
    https://acme.slack.com/archives/C08EF2NGZGB
    https://acme.slack.com/archives/C08EF2NGZGB/p1740478361323219?thread_ts=1740421750.904349&cid=C08EF2NGZGB
    """

    url: str
    _url: furl = attr.field(init=False, default=None)

    def __attrs_post_init__(self):
        self._url = furl(self.url)

    @classmethod
    def from_url(cls, url: str) -> "SlackUrl":
        return cls(url=url)

    @property
    def channel_id(self) -> str:
        return self._url.path.segments[1]

    @property
    def ts(self) -> t.Union[str, None]:
        try:
            message_id = self._url.path.segments[2].lstrip("p")
            message_id = message_id[:-6] + "." + message_id[-6:]
            return message_id
        except IndexError:
            return None

    @property
    def cid(self) -> str:
        return self._url.query.params.get("cid")

    @property
    def thread_ts(self) -> str:
        return self._url.query.params.get("thread_ts")


class SlackChannel:
    @classmethod
    def from_any(cls, value: t.Union[str, None]) -> t.Union[str, None]:
        if value is None:
            return None
        if value.startswith("http://") or value.startswith("https://"):
            return SlackUrl.from_url(value).channel_id
        else:
            return value.lstrip("#")


class SlackMessage:
    @classmethod
    def from_any(cls, value: t.Union[str, None]) -> t.Union[str, None]:
        if value is None:
            return None
        if value.startswith("http://") or value.startswith("https://"):
            return SlackUrl.from_url(value).ts
        else:
            return value


class SlackConversation:
    """
    Wrap a Slack conversation.
    """

    def __init__(self, api_token: str, channel: str):
        self.api_token = api_token
        self.message_ids: t.List[str] = []
        self.webclient = WebClient(token=self.api_token)
        self.channel_id = self.decode_channel(channel)

    def decode_channel(self, channel: str) -> str:
        """
        Decode channel id from channel id, name, or URL.
        """
        channel_search = SlackChannel.from_any(channel)
        try:
            return self.find_channel(what=channel_search).id
        except (AttributeError, KeyError, TypeError) as e:
            raise KeyError(f"Resolving channel failed: {channel_search}") from e

    def channels(self, limit: int = 999) -> t.List[Munch]:
        """
        Enumerate all channels.
        """
        return munchify(self.webclient.conversations_list(limit=limit)["channels"])

    def find_channel(self, what: t.Optional[str] = None):
        """
        Find channel by id or name.
        """
        for channel in self.channels():
            if channel.id == what or channel.name == what:
                return channel
        raise KeyError(f"Unable to find channel: {what}")

    def messages(self, limit: int = 20):
        """
        Enumerate all messages.
        """
        return self.webclient.conversations_history(channel=self.channel_id, limit=limit)

    def find_message(self, *labels):
        """
        Find message by labels in text body.

        TODO. Find message by metadata information.
        """
        response = self.messages()
        for message in response["messages"]:
            text = message["text"]
            if all(label in text for label in labels):
                return message
        return None

    def send(
        self,
        markdown: t.Union[str, None] = None,
        mrkdwn: t.Union[str, None] = None,
        reply_to: t.Union[str, None] = None,
    ):
        """
        Submit new Slack message to channel.
        """
        message_options = self._get_message_options(markdown=markdown, mrkdwn=mrkdwn)

        reply_to = SlackMessage.from_any(reply_to)

        try:
            # Ephemeral messages can be deleted by the addressed user,
            # but on the other hand, can't be deleted by the bot.
            """
            response = self._webclient.chat_postEphemeral(
                channel=self.channel,
                text=mrkdwn,
                type="mrkdwn",
                thread_ts=reply_to,
                user="U017YMHL5FY",
            )
            response["message_ts"]
            """
            response = self.webclient.chat_postMessage(
                channel=self.channel_id,
                thread_ts=reply_to,
                **message_options,
                # icon_emoji=":chart_with_upwards_trend:",
                # attachments=[{"pretext": "pre-hello", "text": "text-world", "foo": "bar"}],
            )
            """
            blocks=[
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": mrkdwn},
                    #"label": {"type": "plain_text", "text": "Feedback", "emoji": True},
                }
            ],
            """
            logger.info(f"Sent message: {response['ts']}")
            self.message_ids.append(response["ts"])
            return response
        except SlackApiError as e:
            logger.error(f"{e.response['error']}. Status code: {e.response.status_code}")

    def update(
        self, ts: str, markdown: t.Union[str, None] = None, mrkdwn: t.Union[str, None] = None
    ):
        """
        Update existing Slack message.
        """
        message_options = self._get_message_options(markdown=markdown, mrkdwn=mrkdwn)
        ts_effective = SlackMessage.from_any(ts)
        if ts_effective is None:
            raise ValueError(f"Unable to decode message id: {ts}")
        response = self.webclient.chat_update(
            channel=self.channel_id, ts=ts_effective, **message_options
        )
        logger.info(f"Updated message: {response['ts']}")
        return response

    def _get_message_options(
        self, markdown: t.Union[str, None] = None, mrkdwn: t.Union[str, None] = None
    ):
        """
        Get message body options, either for `mrkdwn` or `markdown`.
        """
        # if markdown and not mrkdwn:
        #    mrkdwn = to_mrkdwn(markdown, unordered_list=False)
        message_options = {}

        # Vanilla Markdown
        if markdown:
            message_options["markdown_text"] = markdown
        # Slack mrkdwn
        elif mrkdwn:
            message_options["text"] = mrkdwn
        return message_options

    def delete(self):
        """
        Remove entire conversation, i.e. all replies.
        """
        message_ids = list(reversed(self.message_ids))
        logger.info(f"Deleting messages: {message_ids}")
        for message_id in message_ids:
            self.delete_message(message_id)

    def delete_message(self, identifier: str):
        """
        Delete specific message by identifier.
        """
        identifier_effective = SlackMessage.from_any(identifier)
        if identifier_effective is None:
            raise ValueError(f"Unable to decode message id: {identifier}")
        response = self.webclient.chat_delete(channel=self.channel_id, ts=identifier_effective)
        logger.info(f"Deleted message: {response['ts']}")
        return response
