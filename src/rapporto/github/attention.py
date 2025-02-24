import typing as t
from collections import OrderedDict
from operator import attrgetter

from munch import Munch, munchify
from tqdm import tqdm

from rapporto.github.model import (
    GitHubInquiry,
    GitHubQueryBuilder,
    GitHubSearch,
    MarkdownContent,
)
from rapporto.github.util import GitHubHttpClient, repository_name
from rapporto.util import goosefeet, sanitize_title


class GitHubAttentionQueryBuilder(GitHubQueryBuilder):
    """
    Find all open issues and pull requests with labels "bug" or "important".
    """

    labels = [
        "bug",  # GitHub standard.
        "important",  # CrateDB.
        "stale",  # CrateDB.
        "type-bug",  # CPython
        "type-crash",  # CPython
        "type: Bug",  # CrateDB.
        "type: bug",  # CrateDB.
    ]

    def query(self):
        self.add("org", self.inquiry.organization)
        self.add("created", self.timerange)
        self.add("label", ",".join(map(goosefeet, self.labels)))
        self.add("state", "open")


class GitHubAttentionReport:
    """
    Report about important items that deserve your attention, bugs first.

    Find all issues and pull requests with labels "bug" or "important".
    """

    label_section_map = OrderedDict(
        bug="Bugs",
        important="Important",
        stale="Stale",
        others="Others",
    )

    label_aliases = {
        "bug": ["type-bug", "type-crash", "type: Bug", "type: bug"],
    }

    def __init__(self, inquiry: GitHubInquiry):
        self.inquiry = inquiry
        self.session = GitHubHttpClient.session
        self.search = GitHubSearch.with_query_builder(
            self.session, GitHubAttentionQueryBuilder(inquiry=inquiry)
        )

    @property
    def items(self):
        """
        Return GitHub issues and PRs in scope of search constraints.
        """
        items = self.search.issues_and_prs()
        return sorted(munchify(items), key=attrgetter("created_at"))

    def has_relevant_label(self, item) -> t.Optional[Munch]:
        """
        Whether the given item includes a relevant label.
        """
        for label in item.labels:
            if label.name in self.label_section_map or label.name in self.label_aliases.get(
                label.name, []
            ):
                return label
        return None

    @property
    def markdown(self):
        """
        Render report in Markdown format.
        """
        mdc = MarkdownContent(labels=self.label_section_map)
        seen = {}
        for item in tqdm(self.items, leave=False):
            title = sanitize_title(
                f"{repository_name(item.repository_url, with_org=True)}: {item.title}"
            )
            link = f"[{title}]({item.html_url})"
            line = f"- {link}"
            # line = f"- {link} {', '.join(labels)}"
            if label := self.has_relevant_label(item):
                if item.html_url in seen:
                    continue
                seen[item.html_url] = True
                mdc.add(label.name, line)
            else:
                mdc.add("others", line)

        return f"""
# Attention report {self.inquiry.created or ""}

A report about important items that deserve your attention, bugs first.
Time range: {self.search.query_builder.timerange or "n/a"}
{mdc.render()}
        """.strip()  # noqa: E501
