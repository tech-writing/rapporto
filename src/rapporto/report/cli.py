import logging

import click

from rapporto.option import github_organization_option
from rapporto.report.model import DailyReport, ReportOptions, WeeklyReport

logger = logging.getLogger(__name__)

format_option = click.option("--format", "format_", type=str, required=True, default="markdown")


@click.group()
@github_organization_option
@format_option
@click.pass_context
def cli(ctx: click.Context, github_organization: str, format_: str):
    """
    Generate reports.
    """
    ctx.meta["options"] = ReportOptions(
        github_organization=github_organization, output_format=format_
    )


@cli.command()
@click.option("--when", type=str, required=False, help="Point in time")
@click.pass_context
def daily(ctx: click.Context, when: str):
    """
    Daily report.
    """
    report = DailyReport(
        day=when,
        options=ctx.meta["options"],
    )
    report.process()
    print(report.render(report.options.output_format))


@cli.command()
@click.option("--when", type=str, required=False, help="Point in time")
@click.pass_context
def weekly(ctx: click.Context, when: str):
    """
    Weekly report.
    """
    report = WeeklyReport(
        week=when,
        options=ctx.meta["options"],
    )
    report.process()
    print(report.render(report.options.output_format))
