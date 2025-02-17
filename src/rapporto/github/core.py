import datetime as dt
import logging
import os
import typing as t
import urllib.parse
from operator import attrgetter
from pathlib import Path
from textwrap import dedent

import requests_cache
from munch import munchify
from tqdm import tqdm

from rapporto.github.model import (
    ActionsFilter,
    ActionsInquiry,
    ActionsOutcome,
    ActivityInquiry,
    GitHubActivityQueryBuilder,
    PullRequestMetadata,
)

logger = logging.getLogger(__name__)


class HttpClient:
    session = requests_cache.CachedSession(backend="sqlite", expire_after=3600)
    if "GH_TOKEN" in os.environ:
        session.headers.update({"Authorization": f"Bearer {os.getenv('GH_TOKEN')}"})
    else:
        logger.warning("GH_TOKEN not defined. This will exhaust the rate limit quickly.")


class GitHubActivityReport:
    """
    Report about activity across a whole GitHub organization.
    """

    def __init__(self, inquiry: ActivityInquiry):
        self.inquiry = inquiry
        self.session = HttpClient.session

        address = GitHubActivityQueryBuilder(inquiry=inquiry)
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

    @staticmethod
    def format_pr(item: PullRequestMetadata):
        return (
            f"comments: {item.comments_total}, files: {item.changed_files}, size: {item.code_size}"
        )

    def print(self):
        print(f"# PPP report for {self.inquiry.created}")
        # print("## Overview")
        print(self.markdown_overview)
        print()
        print("*Top changes:*")
        print(self.markdown_significant)


class GitHubActionsReport:
    """
    Report about failed outcomes of GitHub Actions workflow runs.
    """

    DELTA_HOURS = 24

    def __init__(self, inquiry: ActionsInquiry):
        self.inquiry = inquiry
        self.session = HttpClient.session

    @property
    def yesterday(self) -> str:
        """
        Compute the start timestamp in ISO format.
        Truncate the ISO format after the hour, to permit caching.
        """
        return dt.datetime.strftime(
            dt.datetime.now() - dt.timedelta(hours=self.DELTA_HOURS), "%Y-%m-%dT%H"
        )

    def fetch(self, filter: ActionsFilter) -> t.List[ActionsOutcome]:  # noqa:A002
        outcomes = []
        for repository in tqdm(
            self.inquiry.repositories,
            desc=f"Fetching failed GitHub Actions outcomes for event={filter.event}",
            leave=False,
        ):
            url = f"https://api.github.com/repos/{repository}/actions/runs?{filter.query}"
            logger.debug(f"Using API URL: {url}")
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
            ActionsFilter(event="schedule", status="failure", created=f">{self.yesterday}")
        )
        items_pull_requests = self.to_markdown(
            ActionsFilter(event="pull_request", status="failure", created=f">{self.yesterday}")
        )
        items_dynamic = self.to_markdown(
            ActionsFilter(event="dynamic", status="failure", created=f">{self.yesterday}")
        )
        return dedent(f"""
# QA report {dt.datetime.today().strftime("%Y-%m-%d")}
A report about GitHub Actions workflow runs that failed recently (now-{self.DELTA_HOURS}h).

## Scheduled
{items_scheduled or "n/a"}

## Pull requests
{items_pull_requests or "n/a"}

## Dynamic
{items_dynamic or "n/a"}
        """)  # noqa: E501

    def print(self):
        print(self.markdown)
