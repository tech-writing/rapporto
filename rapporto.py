# PPP report support program.
# https://github.com/tech-writing/rapporto
#
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "click",
#     "dataclasses-json",
#     "munch",
#     "python-dateutil",
#     "requests-cache",
#     "tqdm",
# ]
# ///
import dataclasses
import datetime as dt
import os
import typing as t
import urllib.parse
from enum import Enum
from operator import attrgetter
from pathlib import Path
from textwrap import dedent

import click
import requests_cache
from dataclasses_json import CatchAll, Undefined, dataclass_json
from munch import munchify
from tqdm import tqdm


class HttpClient:
    session = requests_cache.CachedSession(backend="sqlite", expire_after=3600)
    session.headers.update({"Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}"})


@dataclasses.dataclass
class Inquiry:
    organization: str
    author: str
    created: str


class QType(Enum):
    API = 1
    HTML = 2


class QKind(Enum):
    ISSUE = 1
    PULLREQUEST = 2


class GitHubQueryBuilder:
    template_api = "https://api.github.com/search/issues?q={query}&per_page=100&sort=created&order=asc"
    template_html = "https://github.com/search?q={query}&per_page=100&s=created&o=asc"

    def __init__(self, inquiry: Inquiry):
        self.inquiry = inquiry
        self.type: t.Optional[QType] = None
        self.kind: t.Optional[QKind] = None

    @property
    def query(self):
        timerange = self.inquiry.created
        if "W" in timerange:
            p_year, p_week = timerange.split("W")
            timerange = self.date_range_str(*self.date_range_from_week(p_year, p_week))
        return (
            f"org:{self.inquiry.organization} "
            f"author:{self.inquiry.author} created:{timerange}"
        )

    @staticmethod
    def date_range_from_week(p_year, p_week):
        """
        http://mvsourcecode.com/python-how-to-get-date-range-from-week-number-mvsourcecode/
        """
        firstdayofweek = dt.datetime.strptime(
            f"{p_year}-W{int(p_week) - 1}-1", "%Y-W%W-%w"
        ).date()
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
            raise NotImplementedError(
                "Unknown kind: Only ISSUE and PULLREQUEST are supported"
            )
        return template.format(query=urllib.parse.quote(query))


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
    repo_name: t.Optional[int] = None

    # This dictionary includes all the remaining fields.
    more: t.Optional[CatchAll] = None

    def __post_init__(self):
        self.code_size = self.additions - self.deletions
        self.comments_total = self.comments + self.review_comments
        self.repo_name = self.more["base"]["repo"]["name"]

    def format_item(self):
        # Generic info (for debugging)
        # return (f"files: {self.changed_files}, "
        #        f"size: {self.code_size}, comments: {self.comments_total}")
        # Repo: PR+link
        return f"  - {self.repo_name}: [{self.title}]({self.html_url})"


class GitHubReport:
    def __init__(self, inquiry: Inquiry):
        self.inquiry = inquiry
        self.session = HttpClient.session

        address = GitHubQueryBuilder(inquiry=inquiry)
        self.url_issues_api = address.issue().api().url()
        self.url_pulls_api = address.pr().api().url()
        self.url_issues_html = address.issue().html().url()
        self.url_pulls_html = address.pr().html().url()

    @property
    def repository_names(self):
        items = []

        response = self.session.get(self.url_issues_api)
        response.raise_for_status()
        items += response.json()["items"]

        response = self.session.get(self.url_pulls_api)
        response.raise_for_status()
        items += response.json()["items"]

        names = []
        for item in items:
            url = urllib.parse.urlparse(item["repository_url"])
            names.append(Path(url.path).name)
        return sorted(set(names))

    def pull_requests(self):
        items = []
        response = self.session.get(self.url_pulls_api)
        response.raise_for_status()
        for item in response.json()["items"]:
            if "pull_request" in item:
                pr_url = item["pull_request"]["url"]
                response = self.session.get(pr_url)
                response.raise_for_status()
                pr_data = response.json()
                cm = PullRequestMetadata.from_dict(pr_data)
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
        by_size_items = sorted(
            prs, key=attrgetter(*by_size_sort_attributes), reverse=True
        )
        items += by_size_items[:items_max]

        by_comments_sort_attributes = ["comments_total", "changed_files", "code_size"]
        by_comments_items = sorted(
            prs, key=attrgetter(*by_comments_sort_attributes), reverse=True
        )
        # TODO: Need to deduplicate manually.
        # items += by_comments_items[:items_max]
        for item in by_comments_items[:items_max]:
            if item not in items:
                items.append(item)

        return items

    @property
    def markdown_overview(self):
        link_issues = f"[Issues]({self.url_issues_html})"
        link_pulls = f"[Pull requests]({self.url_pulls_html})"
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

    def format_pr(item: PullRequestMetadata):
        return (
            f"comments: {item.comments_total}, "
            f"files: {item.changed_files}, size: {item.code_size}"
        )

    def print(self):
        print(f"# PPP report for {self.inquiry.created}")
        # print("## Overview")
        print(self.markdown_overview)
        print()
        print("*Top changes:*")
        print(self.markdown_significant)


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
        return f"- [{self.repository}: {self.name}]({self.url})"


class GitHubActionsCheck:
    def __init__(self, inquiry: ActionsInquiry):
        self.inquiry = inquiry
        self.session = HttpClient.session

    @property
    def yesterday(self) -> str:
        return dt.datetime.strftime(dt.date.today() - dt.timedelta(days=1), "%Y-%m-%dT%H")

    def fetch(self, filter: ActionsFilter) -> t.List[ActionsOutcome]:  # noqa:A002
        outcomes = []
        for repository in tqdm(
            self.inquiry.repositories,
            desc=f"Fetching GitHub Actions outcomes for: {filter}",
        ):
            url = f"https://api.github.com/repos/{repository}/actions/runs?{filter.query}"
            # click.echo(f"Using API URL: {url}", file=sys.stderr)
            response = self.session.get(url)
            if response.status_code == 404:
                continue
            response.raise_for_status()
            runs = munchify(response.json()).workflow_runs
            for run in runs:
                outcome = ActionsOutcome(
                    status=run.status,
                    repository=repository,
                    name=run.display_title,
                    url=run.html_url,
                    started=run.run_started_at,
                )
                outcomes.append(outcome)
        return outcomes

    def to_markdown(self, filter: ActionsFilter) -> str:  # noqa:A002
        return "\n".join([item.markdown for item in self.fetch(filter=filter)])

    @property
    def markdown(self):
        items_scheduled = self.to_markdown(
            ActionsFilter(
                event="schedule", status="failure", created=f">{self.yesterday}"
            )
        )
        items_pull_requests = self.to_markdown(
            ActionsFilter(
                event="pull_request", status="failure", created=f">{self.yesterday}"
            )
        )
        items_dynamic = self.to_markdown(
            ActionsFilter(event="dynamic", status="failure", created=f">{self.yesterday}")
        )
        return dedent(f"""
# CrateDB QA
## Drivers & Integrations » Build Status » Scheduled
{items_scheduled}
## Drivers & Integrations » Build Status » Pull requests
{items_pull_requests}
## Drivers & Integrations » Build Status » Dynamic
{items_dynamic}
        """)

    def print(self):
        print(self.markdown)


@click.group()
def cli():
    pass


@cli.command()
@click.option("--organization", type=str, required=True)
@click.option("--author", type=str, required=True)
@click.option("--timerange", type=str, required=True)
def ppp(organization: str, author: str, timerange: str):
    """
    Generate PPP report.
    """
    inquiry = Inquiry(organization=organization, author=author, created=timerange)
    report = GitHubReport(inquiry=inquiry)
    report.print()


@cli.command()
@click.option("--repository", type=str, required=False)
@click.option("--repositories-file", type=Path, required=False)
def qa(repository: str, repositories_file: Path = None):
    """
    Generate QA report.
    """
    if repository:
        inquiry = ActionsInquiry(repositories=[repository])
    elif repositories_file:
        inquiry = ActionsInquiry(repositories=repositories_file.read_text().splitlines())
    else:
        click.echo("Please specify --repository or --repositories-file.", err=True)
        raise SystemExit(1)
    report = GitHubActionsCheck(inquiry=inquiry)
    report.print()


def main():
    cli()


if __name__ == "__main__":
    main()
