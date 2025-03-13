"""
Use Slack conversations like a static documentation generator target.
"""

import dataclasses
import datetime as dt
import logging
import typing as t

from pueblo_goof.slack.conversation import SlackConversation
from rapporto import __version__
from rapporto.report.model import DailyItem, ReportOptions, WeeklyReport
from rapporto.source.github.model import GitHubOptions

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class SlackWeekly:
    """
    Publish daily reports to Slack, in a per-week context, with hourly granularity.
    """

    ROOT_EVENT = "qabot_root_created"
    PREAMBLE_EVENT = "qabot_preamble_created"
    ITEM_EVENT = "qabot_item_created"
    AUTHOR = "qa-bot"

    week: str
    github_options: GitHubOptions
    report_options: ReportOptions
    conversation: SlackConversation

    # Message id of the root message.
    root_id: t.Optional[str] = dataclasses.field(default=None)

    def __post_init__(self):
        if self.week is None:
            self.week = dt.datetime.now().strftime("%YW%V")

    def refresh(self):
        self.seed()
        self.render()

    def seed(self, just_created: bool = False):
        """
        Create/update and seed the conversation.
        """

        logger.info(f"Creating or updating conversation for calendar week: {self.week}")

        message = self.conversation.find_message_by_metadata(
            self.conversation.messages(), type="root", week=self.week
        )
        metadata = {
            "author": self.AUTHOR,
            "type": "root",
            "week": self.week,
        }
        if message:
            self.root_id = message["ts"]
            if self.root_id is None:
                raise KeyError("Root message was not created")
            self.conversation.update(
                ts=self.root_id, markdown=self.root_markdown, metadata=metadata
            )
        else:
            # Submit the root message.
            response = self.conversation.send(
                markdown=self.root_markdown, event=self.ROOT_EVENT, metadata=metadata
            )
            self.root_id = response["ts"]
            if self.root_id is None:
                raise KeyError("Root message was not created")

        # Submit or update the preamble message.
        preamble = DailyItem(type="preamble", day=self.week, markdown=self.preamble_markdown)
        self.create_or_update_item(item=preamble, msg_type="preamble", event=self.PREAMBLE_EVENT)

    @property
    def root_markdown(self):
        """
        The message body for the root message, in Markdown format.
        """
        return f"# qa-bot {self.week}"

    @property
    def preamble_markdown(self):
        """
        The message body for the preamble message, in Markdown format.
        """
        timestamp = dt.datetime.now().replace(microsecond=0).isoformat()
        conversation_link = (
            self.root_id and f"[🔗]({self.conversation.get_permalink(self.root_id)})"
        ) or ""
        changelog_link = "[🔗](https://rapporto.readthedocs.io/changes.html)"
        caveats_link = "[🔗](https://rapporto.readthedocs.io/project/caveats.html)"
        items = [
            f"**Week:** {self.week}",
            f"**Updated:** {timestamp}",
            f"**Root message:** {self.root_id}  {conversation_link}",
            f"**Producer:** Rapporto v{__version__}  {changelog_link}",
            f"**Caveats:** Use responsibly.  {caveats_link}",
        ]
        return "\n".join(items)

    def render(self):
        weekly = WeeklyReport(
            week=self.week,
            github_options=self.github_options,
            report_options=self.report_options,
        )
        weekly.process()
        for daily_report in weekly.dailies:
            for daily_item in daily_report.items:
                self.create_or_update_item(daily_item)

    def create_or_update_item(
        self, item: DailyItem, msg_type: str = "item", event: str = ITEM_EVENT
    ):
        """
        Create or update a Slack message representing a DailyItem.

        TODO: Add timestamp fields to metadata, and also update them on Slack's `update` operations.
        TODO: Generalize to also use with conversation's `seed` operation.
        """
        key = f"{item.type}_{item.day}"

        if self.root_id is None:
            raise KeyError("Unable to create items without root message")
        logger.info(f"Creating or updating reply for key: {key}")
        message = self.conversation.find_message_by_metadata(
            self.conversation.replies(ts=self.root_id), type=msg_type, key=key
        )
        metadata = {
            "key": key,
            "type": msg_type,
            "author": self.AUTHOR,
            "week": self.week,
            "day": item.day,
        }
        if message:
            message_id = message["ts"]
            logger.info(f"Updating message with key: {key}")
            return self.conversation.update(
                ts=message_id, markdown=item.markdown, metadata=metadata
            )
        else:
            logger.info(f"Sending message with key: {key}")
            return self.conversation.send(
                markdown=item.markdown,
                reply_to=self.root_id,
                event=event,
                metadata=metadata,
            )
