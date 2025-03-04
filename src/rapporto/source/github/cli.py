import typing as t
from pathlib import Path

import click
from click_aliases import ClickAliasedGroup

from rapporto.source.github.actions import GitHubActionsReport, MultiRepositoryInquiry
from rapporto.source.github.activity import GitHubActivityReport
from rapporto.source.github.attention import GitHubAttentionReport
from rapporto.source.github.backup import GitHubBackup
from rapporto.source.github.model import GitHubInquiry
from rapporto.util import to_mrkdwn

organization_option = click.option("--organization", "--org", type=str, required=False)
author_option = click.option("--author", type=str, required=False)
when_option = click.option("--when", type=str, required=False, help="Time interval")
format_option = click.option("--format", "format_", type=str, required=False, default="markdown")
repository_option = click.option("--repository", type=str, required=False)
repositories_file_option = click.option("--repositories-file", type=Path, required=False)


@click.group(cls=ClickAliasedGroup)
@click.pass_context
def cli(ctx: click.Context):
    """
    Harvest information from GitHub.
    """
    pass


@cli.command(aliases=["ppp"])
@organization_option
@author_option
@when_option
@format_option
def activity(
    organization: t.Optional[str] = None,
    author: t.Optional[str] = None,
    when: t.Optional[str] = None,
    format_: t.Optional[str] = None,
):
    """
    Activities of individual authors.
    """
    inquiry = GitHubInquiry(organization=organization, author=author, updated=when)
    report = GitHubActivityReport(inquiry=inquiry)
    print_output(report, format_)


def print_output(report, format_):
    if format_ == "markdown":
        print(report.markdown)
    elif format_ == "mrkdwn":
        print(to_mrkdwn(report.markdown))
    else:
        raise NotImplementedError(f"Unknown output format: {format_}")


@cli.command(aliases=["ci"])
@repository_option
@repositories_file_option
@when_option
@format_option
def actions(
    repository: str,
    repositories_file: t.Optional[Path] = None,
    when: t.Optional[str] = None,
    format_: t.Optional[str] = None,
):
    """
    CI/GHA failures.
    """
    try:
        inquiry = MultiRepositoryInquiry.make(
            repository=repository, repositories_file=repositories_file, when=when
        )
    except ValueError as ex:
        click.echo(
            f"Please specify valid input for --repository or --repositories-file: {ex}", err=True
        )
        raise SystemExit(1) from ex
    report = GitHubActionsReport(inquiry=inquiry)
    print_output(report, format_)


@cli.command(aliases=["att"])
@organization_option
@when_option
@format_option
def attention(
    organization: t.Optional[str] = None,
    when: t.Optional[str] = None,
    format_: t.Optional[str] = None,
):
    """
    Important items that deserve attention.
    """
    inquiry = GitHubInquiry(organization=organization, updated=when)
    report = GitHubAttentionReport(inquiry=inquiry)
    print_output(report, format_)


@cli.command(
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True,
    )
)
@click.pass_context
def backup(ctx: click.Context):
    """
    Backup GitHub project.
    """
    backup = GitHubBackup()
    try:
        backup.run(ctx.args)
    except Exception as ex:
        click.echo(f"ERROR: {ex}", err=True)
        raise SystemExit(2) from ex
