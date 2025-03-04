import dataclasses
import logging
import typing as t
from abc import abstractmethod
from operator import attrgetter
from textwrap import dedent

from attrs import define
from dataclasses_json import CatchAll, Undefined, dataclass_json
from requests import Session
from tqdm import tqdm

from rapporto.source.github.model import (
    GitHubInquiry,
    GitHubQueryBuilder,
    GitHubSearch,
)
from rapporto.source.github.util import GitHubHttpClient, repository_name
from rapporto.util import sanitize_title

logger = logging.getLogger(__name__)


class GitHubActivityQueryBuilder(GitHubQueryBuilder):
    """
    Find all open issues and pull requests created by individual author.
    """

    def query(self):
        self.add("org", self.inquiry.organization)
        self.add("updated", self.timeinterval.githubformat())
        self.add("author", self.inquiry.author)


class GitHubActivityReport:
    """
    Report about activity across a whole GitHub organization.
    """

    def __init__(self, inquiry: GitHubInquiry):
        self.inquiry = inquiry
        self.session = GitHubHttpClient.session
        self.search = GitHubSearch.with_query_builder(
            self.session, GitHubActivityQueryBuilder(inquiry=inquiry)
        )

    @property
    def repository_names(self):
        items = self.search.issues_and_prs()
        names = []
        for item in items:
            names.append(repository_name(item["repository_url"]))
        return sorted(set(names))

    @property
    def markdown_overview(self):
        link_issues = f"[Issues]({self.search.issues_html})"
        link_pulls = f"[Pull requests]({self.search.pulls_html})"
        return dedent(f"""
        ## Overview
        *Progress:*
          - About: Bugfixes, Documentation, Guidance, Planning, Support
          - Activity: {", ".join(self.repository_names)}
          - Details: {link_issues}, {link_pulls}
        *Plans:* Dito.
        *Problems:* n/a
        """).strip()

    @property
    def markdown_significant_issues(self):
        return GitHubSignificantIssues(session=self.session, search=self.search).markdown

    @property
    def markdown_significant_prs(self):
        return GitHubSignificantPullRequests(session=self.session, search=self.search).markdown

    @staticmethod
    def format_pr(item: "PullRequestMetadata"):
        return (
            f"comments: {item.comments_total}, files: {item.changed_files}, size: {item.code_size}"
        )

    @property
    def markdown(self) -> str:
        timerange = (self.inquiry.updated and f"for {self.inquiry.updated}") or ""
        return f"""
# Activity report {timerange}

{self.markdown_overview}

## Top issues
{self.markdown_significant_issues}

## Top changes
{self.markdown_significant_prs}
""".strip()


@dataclass_json(undefined=Undefined.INCLUDE)
@dataclasses.dataclass
class IssueMetadata:
    """
    Manage attributes for a GitHub API issue item.
    """

    # Original fields from GitHub API.
    # TODO: Also count reactions.
    number: str
    url: str
    html_url: str
    title: str
    comments: int

    # Computed fields.
    comments_total: t.Optional[int] = None

    # This dictionary includes all the remaining fields.
    more: t.Optional[CatchAll] = None

    def __post_init__(self):
        self.comments_total = self.comments  # + self.review_comments
        try:
            self.repo_name = repository_name(self.html_url, with_org=True)
        except KeyError as ex:
            msg = f"Unable to decode repository name: {ex}"
            logger.error(msg)
            raise KeyError(msg) from ex

    def format_item(self):
        return f"  - [{self.repo_name}: {sanitize_title(self.title)}]({self.html_url})"


@dataclass_json(undefined=Undefined.INCLUDE)
@dataclasses.dataclass
class PullRequestMetadata:
    """
    Manage attributes for a GitHub API pull request item.
    """

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
        return f"  - [{self.repo_name}: {sanitize_title(self.title)}]({self.html_url})"


@define
class SignificantItemsBase:
    """
    Common base class for significant items.
    """

    session: Session
    search: GitHubSearch
    metadata_class: t.ClassVar[t.Type[t.Union[IssueMetadata, PullRequestMetadata]]]
    description: t.ClassVar[str]
    by_size_sort_attributes: t.ClassVar[t.List[str]]
    by_comments_sort_attributes: t.ClassVar[t.List[str]]

    @property
    @abstractmethod
    def api_url(self):
        """
        Implemented individually between Issue vs. PRs.
        """
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def decode_url(item):
        """
        Implemented individually between Issue vs. PRs.
        """
        raise NotImplementedError()

    def items(self):
        """
        Acquire items from GitHub API.
        """
        items = []
        response = self.session.get(self.api_url)
        response.raise_for_status()
        for item in tqdm(response.json()["items"], desc=self.description, leave=False):
            url = self.decode_url(item)
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            cm = self.metadata_class.from_dict(data)  # type: ignore[attr-defined,union-attr]
            items.append(cm)
        return items

    def significant(self):
        """
        Return 2/5 of the most significant PRs, or any other share.

        The list of candidates (all PRs within given time range) is sorted by
        number of comments, number of changed files, and delta code size.
        """
        items_in = self.items()
        items_out = []

        items_max = int(len(items_in) / 2 / 5) + 1

        by_size_items = sorted(
            items_in, key=attrgetter(*self.by_size_sort_attributes), reverse=True
        )
        items_out += by_size_items[:items_max]

        by_comments_items = sorted(
            items_in, key=attrgetter(*self.by_comments_sort_attributes), reverse=True
        )
        # TODO: Need to deduplicate manually.
        # items += by_comments_items[:items_max]
        for item in by_comments_items[:items_max]:
            if item not in items_out:
                items_out.append(item)

        return items_out

    @property
    def markdown(self):
        items = [item.format_item() for item in self.significant()]
        return "\n".join(items)


@define
class GitHubSignificantIssues(SignificantItemsBase):
    """
    Discover significant issues from GitHub API.
    """

    metadata_class = IssueMetadata
    description = "Fetching issues"
    by_size_sort_attributes: t.ClassVar[t.List[str]] = ["comments_total"]
    by_comments_sort_attributes: t.ClassVar[t.List[str]] = ["comments_total"]

    @property
    def api_url(self):
        return self.search.issues_api

    @staticmethod
    def decode_url(item):
        return item["url"]


@define
class GitHubSignificantPullRequests(SignificantItemsBase):
    """
    Discover significant pull requests from GitHub API.
    """

    metadata_class = PullRequestMetadata
    description = "Fetching pull requests"
    by_size_sort_attributes: t.ClassVar[t.List[str]] = [
        "code_size",
        "changed_files",
        "comments_total",
    ]
    by_comments_sort_attributes: t.ClassVar[t.List[str]] = [
        "comments_total",
        "changed_files",
        "code_size",
    ]

    @property
    def api_url(self):
        return self.search.pulls_api

    @staticmethod
    def decode_url(item):
        return item["pull_request"]["url"]
