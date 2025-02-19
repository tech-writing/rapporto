import dataclasses
import datetime as dt
import logging
import typing as t
import urllib.parse
from abc import abstractmethod
from enum import Enum
from pathlib import Path

from attrs import define
from dataclasses_json import CatchAll, Undefined, dataclass_json

from rapporto.util import sanitize_title

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class ActivityInquiry:
    organization: str
    created: str
    author: t.Optional[str] = None


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

    @property
    def timerange(self):
        timerange = self.inquiry.created
        if "W" in timerange:
            p_year, p_week = timerange.split("W")
            timerange = self.date_range_str(*self.date_range_from_week(p_year, p_week))
        return timerange

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
    """
    Find all open issues and pull requests created by individual author.
    """

    @property
    def query(self):
        return (
            f"org:{self.inquiry.organization} created:{self.timerange} author:{self.inquiry.author}"
        )


class GitHubAttentionQueryBuilder(GitHubQueryBuilder):
    """
    Find all open issues and pull requests with labels "bug" or "important".
    """

    labels = [
        "bug",  # GitHub standard.
        "important",  # CrateDB.
        "type-bug",  # CPython
        "type-crash",  # CPython
    ]

    @property
    def query(self):
        return (
            f"org:{self.inquiry.organization} "
            f"created:{self.timerange} "
            f"label:{','.join(self.labels)} state:open"
        )


@define
class GitHubSearch:
    session: t.Any
    query_builder: GitHubQueryBuilder
    issues_api: str
    pulls_api: str
    issues_html: str
    pulls_html: str

    @classmethod
    def with_query_builder(cls, session, query_builder: GitHubQueryBuilder):
        return cls(
            session=session,
            query_builder=query_builder,
            issues_api=query_builder.issue().api().url(),
            pulls_api=query_builder.pr().api().url(),
            issues_html=query_builder.issue().html().url(),
            pulls_html=query_builder.pr().html().url(),
        )

    def issues_and_prs(self):
        items = []

        response = self.session.get(self.issues_api)
        response.raise_for_status()
        items += response.json()["items"]

        response = self.session.get(self.pulls_api)
        response.raise_for_status()
        items += response.json()["items"]

        return items


@dataclasses.dataclass
class MultiRepositoryInquiry:
    repositories: t.List[str]

    @classmethod
    def make(cls, repository: str, repositories_file: Path = None) -> "MultiRepositoryInquiry":
        if repository:
            return cls(repositories=[repository])
        elif repositories_file:
            return cls(repositories=repositories_file.read_text().splitlines())
        else:
            raise ValueError("No repository specified")


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
