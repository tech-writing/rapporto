import datetime as dt
import io
import typing as t

import attr
import yaml
from aika import TimeIntervalParser
from attrs import define

from rapporto.github.attention import GitHubAttentionReport
from rapporto.github.model import GitHubInquiry


@define
class DailyItem:
    """
    Represent a single item of daily recurring report information.
    """

    type: str
    day: str
    markdown: str


@define
class WeeklyItem:
    """
    Represent a multiple weekly items of daily recurring report information.
    """

    type: str
    week: str
    items: t.List[DailyItem] = attr.field(factory=list)


@define
class ReportOptions:
    """
    Composite report options.
    """

    github_organization: str


@define
class ReportBase:
    """
    Common base class for reports.
    """

    def to_dict(self) -> t.Dict[str, t.Any]:
        return attr.asdict(self)

    def data_items(self) -> t.List[t.Union[DailyItem, DailyItem]]:
        return self.to_dict()["data"]

    def to_yaml(self) -> str:
        return yaml.dump(self.to_dict(), sort_keys=False)

    def to_json(self) -> str:
        raise NotImplementedError("Needs special support for `attrs`, see Zyp/Tikray")
        # return json.dumps(yaml.load(self.to_yaml(), yaml.UnsafeLoader), sort_keys=False, indent=2)
        # return json.dumps(munchify(self.to_dict()), sort_keys=False, indent=2)

    @property
    def markdown(self):
        return self.to_markdown()

    def to_markdown(self) -> str:
        buffer = io.StringIO()
        for item in self.data_items():
            buffer.write(item.markdown)
            buffer.write("\n\n")
        return buffer.getvalue()


@define
class DailyReport(ReportBase):
    """
    Produce a daily recurring report.
    """

    day: str
    options: ReportOptions
    items: t.List[DailyItem] = attr.field(factory=list)

    def __attrs_post_init__(self):
        """
        Use current datetime by default.
        """
        if self.day is None:
            self.day = dt.datetime.now().strftime("%Y-%m-%d")

    def process(self):
        """
        Generate set of reports across different domains or topics.
        """
        self.github_attention()

    def github_attention(self):
        """
        Items on GitHub that deserve your attention.
        """
        updated = f"{self.day}..{self.day}"
        inquiry = GitHubInquiry(organization=self.options.github_organization, updated=updated)
        report = GitHubAttentionReport(inquiry=inquiry)
        self.items.append(
            DailyItem(type="github-attention", day=self.day, markdown=report.markdown)
        )

    def to_dict(self):
        return {
            "meta": {"day": self.day},
            "data": self.items,
        }


@define
class WeeklyReport(ReportBase):
    """
    Produce a weekly recurring report.
    """

    week: str
    options: ReportOptions
    dailies: t.List[DailyReport] = attr.field(factory=list)

    SKIP_THE_FUTURE = True

    def __attrs_post_init__(self):
        """
        Use current calendar week by default.
        """
        if self.week is None:
            self.week = dt.datetime.now().strftime("%YW%V")

    @property
    def days(self) -> t.List[str]:
        """
        Enumerate days of designated week.

        TODO: Refactor to Aika.
        """
        week = []
        today = dt.date.today()
        tip = TimeIntervalParser()
        rr = tip.parse(self.week)
        cursor = rr.start
        while cursor < rr.end:
            week.append(cursor.strftime("%Y-%m-%d"))
            cursor += dt.timedelta(days=1)
            if self.SKIP_THE_FUTURE and cursor.date() > today:
                break
        return week

    def process(self):
        """
        Create all daily reports.
        """
        for day in self.days:
            report = DailyReport(day=day, options=self.options)
            report.process()
            self.dailies.append(report)

    def to_dict(self):
        return {
            "meta": {"week": self.week},
            "data": self.dailies,
        }
