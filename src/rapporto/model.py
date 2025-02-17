import dataclasses
import datetime as dt
import logging
import typing as t
import urllib.parse
from abc import abstractmethod
from enum import Enum

from dataclasses_json import CatchAll, Undefined, dataclass_json

from rapporto.util import sanitize_title

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class ActivityInquiry:
    organization: str
    author: str
    created: str


class QType(Enum):
    API = 1
    HTML = 2


class QKind(Enum):
    ISSUE = 1
    PULLREQUEST = 2


@dataclass_json(undefined=Undefined.INCLUDE)
@dataclasses.dataclass
class PullRequestMetadata:
    # Original fields from GitHub API.
    number: str
    url: str
    html_url: str
    title: str
    commits: int
    additions: int
    deletions: int
    changed_files: int
    comments: int
    review_comments: int

    # Computed fields.
    code_size: t.Optional[int] = None
    comments_total: t.Optional[int] = None
    repo_name: t.Optional[str] = None

    # This dictionary includes all the remaining fields.
    more: t.Optional[CatchAll] = None

    def __post_init__(self):
        self.code_size = self.additions - self.deletions
        self.comments_total = self.comments + self.review_comments
        try:
            self.repo_name = self.more["base"]["repo"]["name"]  # type: ignore[index]
        except KeyError as ex:
            msg = f"Unable to decode repository name: {ex}"
            logger.error(msg)
            raise KeyError(msg) from ex

    def format_item(self):
        # Generic info (for debugging)
        # return (f"files: {self.changed_files}, "
        #        f"size: {self.code_size}, comments: {self.comments_total}")
        # Repo: PR+link
        return f"  - {self.repo_name}: [{sanitize_title(self.title)}]({self.html_url})"


class GitHubQueryBuilder:
    template_api = (
        "https://api.github.com/search/issues?q={query}&per_page=100&sort=created&order=asc"
    )
    template_html = "https://github.com/search?q={query}&per_page=100&s=created&o=asc"

    def __init__(self, inquiry: ActivityInquiry):
        self.inquiry = inquiry
        self.type: t.Optional[QType] = None
        self.kind: t.Optional[QKind] = None

    @property
    @abstractmethod
    def query(self):
        raise NotImplementedError("Needs to be implemented")

    @staticmethod
    def date_range_from_week(p_year, p_week):
        """
        http://mvsourcecode.com/python-how-to-get-date-range-from-week-number-mvsourcecode/
        """
        firstdayofweek = dt.datetime.strptime(f"{p_year}-W{int(p_week) - 1}-1", "%Y-W%W-%w").date()
        lastdayofweek = firstdayofweek + dt.timedelta(days=6.9)
        return firstdayofweek, lastdayofweek

    @staticmethod
    def date_range_str(start: dt.datetime, end: dt.datetime):
        return f"{start.isoformat()}..{end.isoformat()}"

    @property
    def query_issues(self):
        return f"{self.query} is:issue"

    @property
    def query_pulls(self):
        return f"{self.query} is:pr"

    def issue(self):
        self.kind = QKind.ISSUE
        return self

    def pr(self):
        self.kind = QKind.PULLREQUEST
        return self

    def api(self):
        self.type = QType.API
        return self

    def html(self):
        self.type = QType.HTML
        return self

    def url(self):
        if self.type == QType.API:
            template = self.template_api
        elif self.type == QType.HTML:
            template = self.template_html
        else:
            raise NotImplementedError("Unknown type: Only API and HTML are supported")
        if self.kind == QKind.ISSUE:
            query = self.query_issues
        elif self.kind == QKind.PULLREQUEST:
            query = self.query_pulls
        else:
            raise NotImplementedError("Unknown kind: Only ISSUE and PULLREQUEST are supported")
        return template.format(query=urllib.parse.quote(query))


class GitHubActivityQueryBuilder(GitHubQueryBuilder):
    @property
    def query(self):
        timerange = self.inquiry.created
        if "W" in timerange:
            p_year, p_week = timerange.split("W")
            timerange = self.date_range_str(*self.date_range_from_week(p_year, p_week))
        return f"org:{self.inquiry.organization} author:{self.inquiry.author} created:{timerange}"


@dataclasses.dataclass
class ActionsInquiry:
    repositories: t.List[str]


@dataclasses.dataclass
class ActionsFilter:
    event: str
    status: str
    created: str

    @property
    def query(self) -> str:
        return f"event={self.event}&status={self.status}&created={self.created}"


@dataclasses.dataclass
class ActionsOutcome:
    status: str
    repository: str
    name: str
    url: str
    started: str

    @property
    def markdown(self):
        title = sanitize_title(f"{self.repository}: {self.name}")
        return f"- [{title}]({self.url})"
