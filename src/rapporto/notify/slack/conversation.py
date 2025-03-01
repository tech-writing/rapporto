"""
https://api.slack.com/methods/chat.postMessage
https://api.slack.com/surfaces/messages#threading
https://api.slack.com/messaging/retrieving#finding_conversation
https://api.slack.com/methods/conversations.history
https://api.slack.com/methods/conversations.replies
"""

import logging
import typing as t
import warnings
from contextlib import contextmanager

from munch import Munch, munchify
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from rapporto.notify.slack.model import SlackChannel, SlackMessage

logger = logging.getLogger(__name__)


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
            # print("channel:", channel)
            if channel.id == what or channel.name == what:
                return channel
        raise KeyError(f"Unable to find channel: {what}")

    def messages(self, limit: int = 20):
        """
        Enumerate all messages.
        """
        return munchify(
            self.webclient.conversations_history(
                channel=self.channel_id,
                limit=limit,
                inclusive=True,
                include_all_metadata=True,
            )["messages"]
        )

    def replies(self, ts: str, limit: int = 20):
        """
        Enumerate all replies.

        https://api.slack.com/methods/conversations.replies
        """
        return munchify(
            self.webclient.conversations_replies(
                channel=self.channel_id,
                ts=ts,
                limit=limit,
                inclusive=True,
                include_all_metadata=True,
            )["messages"]
        )

    def find_message_by_text(self, *labels):
        """
        Find message by labels in text body.
        """
        for message in self.messages():
            text = message["text"]
            if all(label in text for label in labels):
                return message
        return None

    @staticmethod
    def find_message_by_metadata(messages, **metadata):
        """
        Find message by metadata information.

        https://api.slack.com/reference/metadata
        """
        for message in messages:
            message_metadata = message.get("metadata", {}).get("event_payload", {})
            if not message_metadata:
                continue
            found = True
            for key, value in metadata.items():
                if message_metadata.get(key, None) != value:
                    found = False
                    break
            if found:
                return message
        return None

    def send(
        self,
        markdown: t.Union[str, None] = None,
        mrkdwn: t.Union[str, None] = None,
        reply_to: t.Union[str, None] = None,
        event: t.Union[str, None] = None,
        metadata: t.Union[t.Dict[str, str], None] = None,
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
            metadata_effective = None
            if event and metadata:
                metadata_effective = {
                    "event_type": event,
                    "event_payload": metadata,
                }
            with self._suppress_top_level_text_warning():
                response = self.webclient.chat_postMessage(
                    channel=self.channel_id,
                    thread_ts=reply_to,
                    **message_options,
                    metadata=metadata_effective,
                    # icon_emoji=":chart_with_upwards_trend:",
                )
            logger.info(f"Sent message: {response['ts']}")
            self.message_ids.append(response["ts"])
            return response
        except SlackApiError as e:
            logger.error(f"{e.response['error']}. Status code: {e.response.status_code}")

    def update(
        self,
        ts: str,
        markdown: t.Union[str, None] = None,
        mrkdwn: t.Union[str, None] = None,
        event: t.Union[str, None] = None,
        metadata: t.Union[t.Dict[str, str], None] = None,
    ):
        """
        Update existing Slack message.
        """
        message_options = self._get_message_options(markdown=markdown, mrkdwn=mrkdwn)
        ts_effective = SlackMessage.from_any(ts)
        if ts_effective is None:
            raise ValueError(f"Unable to decode message id: {ts}")
        metadata_effective = None
        if event and metadata:
            metadata_effective = {
                "event_type": event,
                "event_payload": metadata,
            }

        with self._suppress_top_level_text_warning():
            response = self.webclient.chat_update(
                channel=self.channel_id,
                ts=ts_effective,
                **message_options,
                metadata=metadata_effective,
            )

        logger.info(f"Updated message: {response['ts']}")
        return response

    @contextmanager
    def _suppress_top_level_text_warning(self):
        """
        Suppress `UserWarning` emitted by Python Slack API.

        UserWarning: The top-level `text` argument is missing in the request payload for a
                     chat.update call - It's a best practice to always provide a `text` argument
                     when posting a message. The `text` argument is used in places where content
                     cannot be rendered such as: system push notifications, assistive technology
                     such as screen readers, etc.
          warnings.warn(ww, UserWarning)

        https://github.com/tech-writing/rapporto/issues/29
        """
        effective_warnings = []
        with warnings.catch_warnings(record=True, category=UserWarning) as catched_warnings:
            warnings.simplefilter("always")
            yield
            for raw_item in catched_warnings:
                if "top-level `text` argument is missing" not in str(raw_item.message):
                    effective_warnings.append(raw_item.message)

        for warning_item in effective_warnings:
            warnings.warn(warning_item, UserWarning, stacklevel=1)

    def _get_message_options(
        self, markdown: t.Union[str, None] = None, mrkdwn: t.Union[str, None] = None
    ):
        """
        Get message body options, either for `mrkdwn` or `markdown`.
        """
        # if markdown and not mrkdwn:
        #    mrkdwn = to_mrkdwn(markdown, unordered_list=False)
        message_options: t.Dict[str, t.Any] = {
            "unfurl_links": False,
            "unfurl_media": False,
        }

        # Vanilla Markdown
        if markdown:
            message_options["markdown_text"] = markdown
        # Slack mrkdwn
        elif mrkdwn:
            message_options["text"] = mrkdwn

        """
        message_options = {}
        message_options["blocks"] = [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": mrkdwn},
                #"text": {"type": "markdown", "text": markdown},
                # "label": {"type": "plain_text", "text": "Feedback", "emoji": True},
            }
        ]
        """

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
