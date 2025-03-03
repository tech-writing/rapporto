import typing as t

import attr
import click
from attrs import define
from furl import furl

slack_api_token_option = click.option(
    "--slack-token", type=str, envvar="SLACK_TOKEN", required=False, help="Slack API token"
)
slack_channel_option = click.option(
    "--slack-channel", "-c", type=str, envvar="SLACK_CHANNEL", required=False, help="Slack channel"
)


@define
class SlackOptions:
    """
    Composite Slack options.
    """

    token: str
    channel: str


@define
class SlackUrl:
    """
    Manage and decode a full HTTP Slack URL.

    https://acme.slack.com/archives/C08EF2NGZGB
    https://acme.slack.com/archives/C08EF2NGZGB/p1740421750904349
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
