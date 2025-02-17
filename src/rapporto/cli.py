from pathlib import Path

import click
from pueblo.util.cli import boot_click

from rapporto.core import GitHubActionsReport, GitHubActivityReport
from rapporto.model import ActionsInquiry, ActivityInquiry


@click.group()
@click.option("--verbose", is_flag=True, required=False, help="Turn on logging")
@click.option("--debug", is_flag=True, required=False, help="Turn on logging with debug level")
@click.version_option()
@click.pass_context
def cli(ctx: click.Context, verbose: bool, debug: bool):
    return boot_click(ctx, verbose, debug)


@cli.command()
@click.option("--organization", type=str, required=True)
@click.option("--author", type=str, required=True)
@click.option("--timerange", type=str, required=True)
def ppp(organization: str, author: str, timerange: str):
    """
    Generate PPP report.
    """
    inquiry = ActivityInquiry(organization=organization, author=author, created=timerange)
    report = GitHubActivityReport(inquiry=inquiry)
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
    report = GitHubActionsReport(inquiry=inquiry)
    report.print()
