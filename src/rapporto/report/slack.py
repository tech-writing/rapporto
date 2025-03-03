"""
Use Slack conversations like a static documentation generator target.
"""

import dataclasses
import datetime as dt
import logging
import typing as t

from pueblo_goof.slack.conversation import SlackConversation
from rapporto.report.model import DailyItem, ReportOptions, WeeklyReport

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class SlackWeekly:
    """
    Publish daily reports to Slack, in a per-week context, with hourly granularity.
    """

    ROOT_EVENT = "qabot_root_created"
    ITEM_EVENT = "qabot_item_created"
    AUTHOR = "qa-bot"

    week: str
    options: ReportOptions
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
        Seed the root message.
        """

        logger.info(f"Creating or updating root message for week {self.week}")

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
            # Prevent running in circles.
            if just_created:
                return

            # Submit the root / seed message.
            self.conversation.send(
                markdown=self.root_markdown, event=self.ROOT_EVENT, metadata=metadata
            )
            self.seed(just_created=True)

    @property
    def root_markdown(self):
        """
        The message body for the root message, in Markdown format.
        """
        timestamp = dt.datetime.now().replace(microsecond=0).isoformat()
        items = [
            f"**Week:** {self.week}",
            f"**Updated:** {timestamp}",
            f"**Message:** {self.root_id}",
        ]
        return "# qa-bot ready\n\n" + "\n".join(items)

    def render(self):
        weekly = WeeklyReport(
            week=self.week,
            options=self.options,
        )
        weekly.process()
        for daily_report in weekly.dailies:
            for daily_item in daily_report.items:
                key = f"{daily_item.type}_{daily_item.day}"
                self.create_or_update_item(key, daily_item)

    def create_or_update_item(self, key: str, item: DailyItem):
        """
        Create or update a Slack message representing a DailyItem.

        TODO: Add timestamp fields to metadata, and also update them on Slack's `update` operations.
        TODO: Generalize to also use with conversation's `seed` operation.
        """
        if self.root_id is None:
            raise KeyError("Unable to create items without root message")
        logger.info(f"Creating or updating reply for key: {key}")
        message = self.conversation.find_message_by_metadata(
            self.conversation.replies(ts=self.root_id), type="item", key=key
        )
        metadata = {
            "key": key,
            "type": "item",
            "author": self.AUTHOR,
            "week": self.week,
            "day": item.day,
        }
        if message:
            message_id = message["ts"]
            self.conversation.update(ts=message_id, markdown=item.markdown, metadata=metadata)
            logger.info(f"Updated message for key: {key}")
        else:
            self.conversation.send(
                markdown=item.markdown,
                reply_to=self.root_id,
                event=self.ITEM_EVENT,
                metadata=metadata,
            )
            logger.info(f"Created message for key: {key}")
