import typing as t
from pathlib import Path

import click
from click_aliases import ClickAliasedGroup

from rapporto.github.core import GitHubActionsReport, GitHubActivityReport, GitHubAttentionReport
from rapporto.github.model import ActivityInquiry, MultiRepositoryInquiry

organization_option = click.option("--organization", "--org", type=str, required=False)
author_option = click.option("--author", type=str, required=False)
timerange_option = click.option("--timerange", type=str, required=False)
repository_option = click.option("--repository", type=str, required=False)
repositories_file_option = click.option("--repositories-file", type=Path, required=False)


@click.group(cls=ClickAliasedGroup)
@click.pass_context
def cli(ctx: click.Context):
    """
    Harvest information from GitHub.
    """
    pass


@cli.command()
@organization_option
@author_option
@timerange_option
def ppp(
    organization: t.Optional[str] = None,
    author: t.Optional[str] = None,
    timerange: t.Optional[str] = None,
):
    """
    Activity: Report about activities of individual authors.
    """
    inquiry = ActivityInquiry(organization=organization, author=author, created=timerange)
    report = GitHubActivityReport(inquiry=inquiry)
    report.print()


@cli.command()
@repository_option
@repositories_file_option
def ci(repository: str, repositories_file: Path = None):
    """
    QA: Report about CI failures.
    """
    try:
        inquiry = MultiRepositoryInquiry.make(
            repository=repository, repositories_file=repositories_file
        )
    except ValueError as ex:
        click.echo(
            f"Please specify valid input for --repository or --repositories-file: {ex}", err=True
        )
        raise SystemExit(1) from ex
    report = GitHubActionsReport(inquiry=inquiry)
    report.print()


@cli.command(aliases=["att"])
@organization_option
@timerange_option
def attention(organization: t.Optional[str] = None, timerange: t.Optional[str] = None):
    """
    QA: Report about important items that deserve attention.
    """
    inquiry = ActivityInquiry(organization=organization, created=timerange)
    report = GitHubAttentionReport(inquiry=inquiry)
    report.print()
