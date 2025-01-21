#
# PPP report support program.
# https://github.com/tech-writing/rapporto
#
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "click",
#     "requests-cache",
# ]
# ///
import urllib
import click
from pathlib import Path
import requests_cache
import dataclasses
from textwrap import dedent


class Address:
    template_api = "https://api.github.com/search/issues?q={query}&per_page=100&sort=created&order=asc"
    template_html = "https://github.com/search?q={query}&per_page=100&s=created&o=asc"

    def for_api(self, query):
        return self.template_api.format(query=urllib.parse.quote(query))

    def for_html(self, query):
        return self.template_html.format(query=urllib.parse.quote(query))


@dataclasses.dataclass
class GitHubInquiry:
    organization: str
    author: str
    created: str


class GitHubReport:

    def __init__(self, inquiry: GitHubInquiry):
        self.inquiry = inquiry
        self.session = requests_cache.CachedSession(backend="sqlite")

        self.query = f"org:{self.inquiry.organization} author:{self.inquiry.author} created:{self.inquiry.created}"
        self.query_issues = f"{self.query} is:issue"
        self.query_pulls = f"{self.query} is:pr"

        self.address = Address()
        self.url_issues_api = self.address.for_api(self.query_issues)
        self.url_pulls_api = self.address.for_api(self.query_pulls)
        self.url_issues_html = self.address.for_html(self.query_issues)
        self.url_pulls_html = self.address.for_html(self.query_pulls)

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
        return list(sorted(set(names)))

    @property
    def markdown(self):
        link_issues = f"[Issues]"
        link_pulls = f"[Pull requests]"
        buffer = dedent(f"""
        # PPP report for {self.inquiry.created}
        **Progress:**
        - Bugfixes, Documentation, Guidance, Planning, Support
        - {", ".join(self.repository_names)}
        - {link_issues}, {link_pulls}
        **Plans:** Dito.
        **Problems:** n/a
     
        [Issues]: {self.url_issues_html}
        [Pull requests]: {self.url_pulls_html}
        """)

        return buffer

@click.command()
@click.option("--organization", type=str, required=True)
@click.option("--author", type=str, required=True)
@click.option("--timerange", type=str, required=True)
def cli(organization: str, author: str, timerange: str):
    inquiry = GitHubInquiry(organization=organization, author=author, created=timerange)
    report = GitHubReport(inquiry=inquiry)
    print(report.markdown)


def main():
    cli()


if __name__ == "__main__":
    main()
