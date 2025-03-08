import logging

import click

from rapporto.option import (
    format_option,
    github_organization_option,
    github_repository_option,
)
from rapporto.report.model import DailyReport, ReportOptions, WeeklyReport
from rapporto.source.github.model import GitHubOptions

logger = logging.getLogger(__name__)


@click.group()
@github_organization_option
@github_repository_option
@format_option
@click.pass_context
def cli(ctx: click.Context, github_organization: str, github_repository: str, format_: str):
    """
    Generate reports.
    """
    ctx.meta["github_options"] = GitHubOptions(organization=github_organization).add_repos(
        github_repository
    )
    ctx.meta["report_options"] = ReportOptions(output_format=format_)


@cli.command()
@click.option("--day", type=str, required=False, help="Day in ISO format, e.g. 2025-03-03")
@click.pass_context
def daily(ctx: click.Context, day: str):
    """
    Daily report.
    """
    report = DailyReport(
        day=day,
        github_options=ctx.meta["github_options"],
        report_options=ctx.meta["report_options"],
    )
    report.process()
    print(report.render(report.report_options.output_format))


@cli.command()
@click.option("--week", type=str, required=False, help="Calendar week in ISO format, e.g. 2025W03")
@click.pass_context
def weekly(ctx: click.Context, week: str):
    """
    Weekly report.
    """
    report = WeeklyReport(
        week=week,
        github_options=ctx.meta["github_options"],
        report_options=ctx.meta["report_options"],
    )
    report.process()
    print(report.render(report.report_options.output_format))
