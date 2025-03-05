import typing as t
from pathlib import Path

import click
from click_aliases import ClickAliasedGroup

from rapporto.option import format_option
from rapporto.source.github.actions import GitHubActionsReport
from rapporto.source.github.activity import GitHubActivityReport
from rapporto.source.github.attention import GitHubAttentionReport
from rapporto.source.github.backup import GitHubBackup
from rapporto.source.github.model import GitHubInquiry, GitHubMultiRepositoryInquiry, GitHubOptions
from rapporto.util import to_mrkdwn

organization_option = click.option("--organization", "--org", type=str, required=False)
author_option = click.option("--author", type=str, required=False)
when_option = click.option("--when", type=str, required=False, help="Time interval")
repository_option = click.option(
    "--repository",
    type=str,
    required=True,
    help="GitHub repository, single or path to file",
)


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
@when_option
@format_option
def actions(
    repository: t.Union[str, Path],
    when: t.Optional[str] = None,
    format_: t.Optional[str] = None,
):
    """
    CI/GHA failures.
    """
    options = GitHubOptions().add_repos(repository)
    inquiry = GitHubMultiRepositoryInquiry(repositories=options.repositories, created=when)
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
