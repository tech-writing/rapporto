import datetime as dt
import io
import typing as t

import attr
import yaml
from attrs import define

from rapporto.source.github.actions import GitHubActionsReport
from rapporto.source.github.attention import GitHubAttentionReport
from rapporto.source.github.model import GitHubInquiry, GitHubMultiRepositoryInquiry, GitHubOptions
from rapporto.util import week_to_day_range


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

    output_format: str = "markdown"


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
        raise NotImplementedError("Needs special support by `cattrs`, see Zyp/Tikray")
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

    def render(self, format_: str):
        if format_ in ["markdown", "md"]:
            return self.markdown
        elif format_ == "yaml":
            return self.to_yaml()
        elif format_ == "json":
            return self.to_json()
        else:
            raise NotImplementedError(f"Unknown format: {format_}")


@define
class DailyReport(ReportBase):
    """
    Produce a daily recurring report.
    """

    day: str
    github_options: GitHubOptions
    report_options: ReportOptions
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
        self.github_actions()
        self.github_attention()

    def github_actions(self):
        """
        CI workflow run failures on GitHub.
        """
        # TODO: Use `TimeIntervalParser`.
        created = f"{self.day}..{self.day}"
        inquiry = GitHubMultiRepositoryInquiry(
            repositories=self.github_options.repositories, created=created
        )
        report = GitHubActionsReport(inquiry=inquiry)
        self.items.append(DailyItem(type="github-actions", day=self.day, markdown=report.markdown))

    def github_attention(self):
        """
        Items on GitHub that deserve your attention.
        """
        # TODO: Use `TimeIntervalParser`.
        updated = f"{self.day}..{self.day}"
        inquiry = GitHubInquiry(organization=self.github_options.organization, updated=updated)
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
    github_options: GitHubOptions
    report_options: ReportOptions
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
        return week_to_day_range(self.week, skip_the_future=self.SKIP_THE_FUTURE)

    def process(self):
        """
        Create all daily reports.
        """
        for day in self.days:
            report = DailyReport(
                day=day, github_options=self.github_options, report_options=self.report_options
            )
            report.process()
            self.dailies.append(report)

    def to_dict(self):
        return {
            "meta": {"week": self.week},
            "data": self.dailies,
        }
