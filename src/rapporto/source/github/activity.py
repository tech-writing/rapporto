import dataclasses
import io
import logging
import typing as t
from contextlib import redirect_stdout
from operator import attrgetter
from textwrap import dedent

from dataclasses_json import CatchAll, Undefined, dataclass_json
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

    def pull_requests(self):
        items = []
        response = self.session.get(self.search.pulls_api)
        response.raise_for_status()
        for item in tqdm(response.json()["items"], leave=False):
            if "pull_request" in item:
                pr_url = item["pull_request"]["url"]
                response = self.session.get(pr_url)
                response.raise_for_status()
                pr_data = response.json()
                cm = PullRequestMetadata.from_dict(pr_data)  # type: ignore[attr-defined]
                items.append(cm)
        return items

    def significant_pull_requests(self):
        """
        Return 2/5 of the most significant PRs, or any other share.

        The list of candidates (all PRs within given time range) is sorted by
        number of comments, number of changed files, and delta code size.
        """
        prs = self.pull_requests()
        items_max = int(len(prs) / 2 / 5) + 1
        items = []

        by_size_sort_attributes = ["code_size", "changed_files", "comments_total"]
        by_size_items = sorted(prs, key=attrgetter(*by_size_sort_attributes), reverse=True)
        items += by_size_items[:items_max]

        by_comments_sort_attributes = ["comments_total", "changed_files", "code_size"]
        by_comments_items = sorted(prs, key=attrgetter(*by_comments_sort_attributes), reverse=True)
        # TODO: Need to deduplicate manually.
        # items += by_comments_items[:items_max]
        for item in by_comments_items[:items_max]:
            if item not in items:
                items.append(item)

        return items

    @property
    def markdown_overview(self):
        link_issues = f"[Issues]({self.search.issues_html})"
        link_pulls = f"[Pull requests]({self.search.pulls_html})"
        return dedent(f"""
        *Progress:*
          - About: Bugfixes, Documentation, Guidance, Planning, Support
          - Activity: {", ".join(self.repository_names)}
          - Details: {link_issues}, {link_pulls}
        *Plans:* Dito.
        *Problems:* n/a
        """).strip()

    @property
    def markdown_significant(self):
        items = [item.format_item() for item in self.significant_pull_requests()]
        return "\n".join(items)

    @staticmethod
    def format_pr(item: "PullRequestMetadata"):
        return (
            f"comments: {item.comments_total}, files: {item.changed_files}, size: {item.code_size}"
        )

    @property
    def markdown(self) -> str:
        timerange = (self.inquiry.updated and f"for {self.inquiry.updated}") or ""
        with redirect_stdout(io.StringIO()) as buffer:
            print(f"# Activity report {timerange}")
            # print("## Overview")
            print(self.markdown_overview)
            print()
            print("*Top changes:*")
            print(self.markdown_significant)
        buffer.seek(0)
        return buffer.read()


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
