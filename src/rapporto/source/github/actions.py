import dataclasses
import logging
import typing as t
from collections import OrderedDict

from aika import TimeInterval
from munch import Munch, munchify
from tqdm import tqdm

from rapporto.source.github.model import (
    GitHubMultiRepositoryInquiry,
    MarkdownContent,
    timeinterval,
)
from rapporto.source.github.util import GitHubHttpClient
from rapporto.util import sanitize_title

logger = logging.getLogger(__name__)


class GitHubActionsReport:
    """
    Report about failed outcomes of GitHub Actions workflow runs.
    """

    def __init__(self, inquiry: GitHubMultiRepositoryInquiry):
        self.inquiry = inquiry
        self.request = GitHubActionsRequest(inquiry)
        self.runs_failed = self.request.runs_failed
        self.runs_pr_success = self.request.runs_pr_success

    @property
    def runs(self):
        """
        All failed runs, modulo duplicates and subsequent succeeding PR runs.
        """
        seen = set()
        for run in self.runs_failed:
            # Filter duplicates.
            key = f"{run.repository.full_name}-{run.head_branch}-{run.name}"
            if key in seen:
                continue

            # Filter PRs that subsequently succeeded.
            if run.event == "pull_request" and self.is_pr_successful(run):
                continue

            seen.add(key)
            yield run

    def is_pr_successful(self, run):
        """
        Find out if a given run has others that succeeded afterward.
        """
        for pr_run in self.runs_pr_success:
            if (
                run.repository.full_name == pr_run.repository.full_name
                and run.head_branch == pr_run.head_branch
                and run.name == pr_run.name
            ):
                return True
        return False

    @property
    def markdown(self):
        mdc = MarkdownContent(labels=self.request.event_section_map)
        for run in self.runs:
            mdc.add(run.event, run.markdown)
        return f"""
# CI failures report {self.request.timeinterval.start.date().isoformat()}

A report about GitHub Actions workflow runs that failed recently.
Time range: {self.request.timeinterval.githubformat() or "n/a"}
{mdc.render()}
        """.strip()


class GitHubActionsRequest:
    """
    Fetch outcomes of recent GitHub Actions workflow runs.

    Possible event types are: dynamic, pull_request, push, schedule
    """

    event_section_map: t.ClassVar[t.OrderedDict[str, str]] = OrderedDict(
        schedule="Schedule",
        pull_request="Pull requests",
        # push="Pushes",
        dynamic="Dynamic",
    )

    def __init__(self, inquiry: GitHubMultiRepositoryInquiry):
        self.inquiry = inquiry
        self.session = GitHubHttpClient.session

    @property
    def timeinterval(self) -> TimeInterval:
        """
        Return same-day time interval.

        TODO: Expand to use other, more broad time intervals sensibly.
        """
        ti = timeinterval(self.inquiry.created)
        ti.end = ti.start
        return ti

    @property
    def created(self) -> str:
        """
        Compute the start timestamp in ISO format.
        Truncate the ISO format after the hour, to permit caching.
        """
        # TODO: What about `%Y-%m-%dT%H`?
        # TODO: What about `dt.timedelta(hours=self.DELTA_HOURS)`, with `DELTA_HOURS = 24`?
        return self.timeinterval.githubformat()

    def fetch(self, filter: "ActionsFilter") -> t.List["ActionsOutcome"]:  # noqa:A002
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
            for run in munchify(response.json()).workflow_runs:
                outcome = ActionsOutcome(
                    id=run.id,
                    event=run.event,
                    status=run.status,
                    conclusion=run.conclusion,
                    repository=run.repository,
                    name=run.display_title,
                    url=run.html_url,
                    started=run.run_started_at,
                    head_branch=run.head_branch,
                )
                outcomes.append(outcome)
        return outcomes

    @property
    def runs_failed(self):
        return self.fetch(filter=ActionsFilter(status="failure", created=self.created))

    @property
    def runs_pr_success(self):
        return self.fetch(
            filter=ActionsFilter(event="pull_request", status="success", created=self.created)
        )


@dataclasses.dataclass
class ActionsFilter:
    event: t.Optional[str] = None
    status: t.Optional[str] = None
    created: t.Optional[str] = None

    @property
    def query(self) -> str:
        expression = []
        if self.event:
            expression.append(f"event={self.event}")
        if self.status:
            expression.append(f"status={self.status}")
        if self.created:
            expression.append(f"created={self.created}")
        return "&".join(expression)


@dataclasses.dataclass
class ActionsOutcome:
    id: int
    event: str
    status: str
    conclusion: str
    repository: Munch
    name: str
    url: str
    started: str
    head_branch: str

    @property
    def markdown(self):
        title = sanitize_title(f"{self.repository.full_name}: {self.name}")
        return f"- [{title}]({self.url})"
