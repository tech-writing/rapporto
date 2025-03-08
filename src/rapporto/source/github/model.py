import dataclasses
import datetime as dt
import logging
import typing as t
import urllib.parse
from abc import abstractmethod
from collections import OrderedDict
from enum import Enum
from pathlib import Path

import attr
import dateparser
from aika import TimeInterval, TimeIntervalParser
from attrs import define

logger = logging.getLogger(__name__)


@define
class GitHubOptions:
    """
    Options for GitHub.
    """

    organization: t.Optional[str] = None
    repositories: t.List[str] = attr.field(factory=list)

    def add_repos(self, repos: t.Union[str, Path]) -> "GitHubOptions":
        if repos is None:
            return self
        path = Path(repos)
        if path.exists():
            self.add_repositories_file(path)
        elif isinstance(repos, str):
            self.add_repository(repos)
        else:
            raise TypeError("repos must be a str or Path")
        return self

    def add_repository(self, name: str):
        self.repositories.append(name)

    def add_repositories_file(self, path: Path):
        self.repositories += path.read_text().splitlines()


@dataclasses.dataclass
class GitHubInquiry:
    organization: t.Optional[str] = None
    updated: t.Optional[str] = None
    author: t.Optional[str] = None


@dataclasses.dataclass
class GitHubMultiRepositoryInquiry:
    repositories: t.List[str]
    created: t.Optional[str] = None


class QType(Enum):
    API = 1
    HTML = 2


class QKind(Enum):
    ISSUE = 1
    PULLREQUEST = 2


class GitHubQueryBuilder:
    template_api = (
        "https://api.github.com/search/issues?q={query}&per_page=100&sort=created&order=asc"
    )
    template_html = "https://github.com/search?q={query}&per_page=100&s=created&o=asc"

    def __init__(self, inquiry: GitHubInquiry):
        self.inquiry = inquiry
        self.type: t.Optional[QType] = None
        self.kind: t.Optional[QKind] = None
        self.constraints: t.List[str] = []
        self.query()

    def add(self, field: str, value: t.Optional[str] = None, is_list: bool = False):
        if value is not None:
            if is_list:
                for item in value.split(","):
                    self.add(field, item.strip())
                return
            self.constraints.append(f"{field}:{value}")

    @property
    def expression(self):
        return " ".join(self.constraints)

    @abstractmethod
    def query(self):
        raise NotImplementedError("Needs to be implemented")

    @property
    def timeinterval(self) -> TimeInterval:
        return timeinterval(self.inquiry.updated)

    @property
    def timerange(self) -> str:
        timerange_user = self.inquiry.updated
        timerange_effective = self.timeinterval.githubformat()
        logger.info(f'Using timerange: user="{timerange_user}" effective="{timerange_effective}"')
        return timerange_effective

    @property
    def query_issues(self):
        return f"{self.expression} is:issue"

    @property
    def query_pulls(self):
        return f"{self.expression} is:pr"

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


@dataclasses.dataclass()
class MarkdownContent:
    labels: t.OrderedDict[str, str] = dataclasses.field(default_factory=OrderedDict)
    content: t.Dict[str, t.List[str]] = dataclasses.field(default_factory=dict)

    def add(self, section, content):
        self.content.setdefault(section, [])
        self.content[section].append(content)

    def render_section(self, section) -> t.Optional[str]:
        if section not in self.content:
            return None
        label = self.labels.get(section, section)
        body = "\n".join(self.content[section])
        return f"\n## {label}\n{body}"

    def render(self):
        sections = []
        for section in self.labels.keys():
            if markdown := self.render_section(section):
                sections.append(markdown)
        return "\n".join(sections)


def timeinterval(when: t.Optional[str] = None) -> TimeInterval:
    if when is None:
        return TimeInterval(dt.datetime.today())

    # TODO: Add edge case to Aika. -- https://github.com/panodata/aika/issues/112
    if when and ".." in when:
        parts = when.split("..")
        return TimeInterval(start=dateparser.parse(parts[0]), end=dateparser.parse(parts[1]))
    # TODO: Let optionally Aika NOT set the `end` part of the interval to NOW.
    tr = TimeIntervalParser()
    return tr.parse(when)
