import typing as t
from collections import OrderedDict
from operator import attrgetter

from munch import Munch, munchify
from tqdm import tqdm

from rapporto.source.github.model import (
    GitHubInquiry,
    GitHubQueryBuilder,
    GitHubSearch,
    MarkdownContent,
)
from rapporto.source.github.util import GitHubHttpClient, repository_name
from rapporto.util import goosefeet, sanitize_title


class GitHubAttentionQueryBuilder(GitHubQueryBuilder):
    """
    Find all open issues and pull requests with labels "bug" or "important".
    """

    labels: t.ClassVar[t.List[str]] = [
        "bug",  # GitHub standard.
        "important",
        "incident",
        "stale",
        "type-bug",  # CPython
        "type-crash",  # CPython
        "type: bug",
        "type: incident",
    ]

    def query(self):
        self.add("org", self.inquiry.organization)
        self.add("updated", self.timeinterval.githubformat())
        self.add("label", ",".join(map(goosefeet, self.labels)))
        # self.add("state", "open")


class GitHubAttentionReport:
    """
    Report about important items that deserve your attention, bugs first.

    Find all issues and pull requests with labels "bug" or "important".
    """

    label_section_map: t.ClassVar[t.OrderedDict[str, str]] = OrderedDict(
        bug="Bugs",
        incident="Incidents",
        important="Important",
        stale="Stale",
        others="Others",
    )

    label_aliases: t.ClassVar[t.Dict[str, t.List[str]]] = {
        "bug": ["type-bug", "type-crash", "type: bug"],
        "incident": ["type: incident"],
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
            label_name = label.name.lower()
            for label_key in self.label_section_map.keys():
                label_key = label_key.lower()
                if label_name == label_key or label_name in self.label_aliases.get(label_key, []):
                    # It's easier for the downstream renderer when using canonical category labels.
                    label.category = label_key
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
            is_closed = item.state == "closed"
            title = sanitize_title(
                f"{repository_name(item.repository_url, with_org=True)}: {item.title}"
            )
            link = f"[{title}]({item.html_url})"
            if is_closed:
                line = f"- ~{link}~"
            else:
                line = f"- {link}"
            # line = f"- {link} {', '.join(labels)}"
            if label := self.has_relevant_label(item):
                if item.html_url in seen:
                    continue
                seen[item.html_url] = True
                mdc.add(label.category, line)
            else:
                mdc.add("others", line)

        return f"""
# Attention report {self.inquiry.updated or ""}

A report about important items that deserve your attention, bugs first.
Time range: {self.search.query_builder.timeinterval.githubformat() or "n/a"}
{mdc.render()}
        """.strip()
