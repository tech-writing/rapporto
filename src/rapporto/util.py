import datetime as dt
import logging
import sys
import typing as t

from aika import TimeIntervalParser
from markdown_to_mrkdwn import SlackMarkdownConverter

logger = logging.getLogger(__name__)


def sanitize_title(title: str) -> str:
    """
    Strip characters that are unfortunate in Markdown link titles.
    """
    return title.replace("[", "⎡").replace("]", "⎦")


def goosefeet(text: str) -> str:
    """
    Parameters including spaces need to be treated specially for the GitHub API.
    """
    if " " in text:
        return f'"{text}"'
    return text


def to_mrkdwn(markdown: str, unordered_list: bool = True) -> str:
    """
    Convert standard Markdown to Slack `mrkdwn` format.
    """
    mrkdwn_converter = SlackMarkdownConverter()
    try:
        # Unordered list
        if not unordered_list:
            mrkdwn_converter.patterns.remove((r"^(\s*)- (.+)", r"\1• \2"))
    except ValueError:
        pass
    return mrkdwn_converter.convert(markdown)


def setup_logging(level=logging.INFO, verbose: bool = False):
    """
    Configure Python's logging module.
    """
    log_format = "%(asctime)-15s [%(name)-36s] %(levelname)-8s: %(message)s"
    logging.basicConfig(format=log_format, stream=sys.stderr, level=level)


def week_to_day_range(when: str, skip_the_future: bool = True) -> t.List[str]:
    """
    From a current point in time, derive the calendar week in ISO8601 format.

    TODO: Refactor to Aika.
    TODO: Make it configurable whether to return 7 or 8 days.
    """
    week = []
    today = dt.date.today()
    tip = TimeIntervalParser()
    interval = tip.parse(when)
    cursor = interval.start
    while cursor < interval.end:
        week.append(cursor.strftime("%Y-%m-%d"))
        cursor += dt.timedelta(days=1)
        if skip_the_future and cursor.date() > today:
            logger.info(f"Skipping day in the future: {cursor.date().isoformat()}.")
            break
    return week
