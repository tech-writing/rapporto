import logging

import click

from rapporto.report.model import DailyReport, ReportOptions, WeeklyReport

logger = logging.getLogger(__name__)

github_organization_option = click.option(
    "--github-organization", "--gh-org", type=str, required=True
)


@click.group()
@github_organization_option
@click.pass_context
def cli(ctx: click.Context, github_organization: str):
    """
    Generate reports.
    """
    ctx.meta["options"] = ReportOptions(github_organization=github_organization)


@cli.command()
@click.option("--when", type=str, required=False, help="Point in time")
@click.pass_context
def daily(ctx: click.Context, when: str):
    """
    Daily report.
    """
    daily = DailyReport(
        day=when,
        options=ctx.meta["options"],
    )
    daily.process()
    # print(daily.to_json())
    print(daily.to_markdown())


@cli.command()
@click.option("--when", type=str, required=False, help="Point in time")
@click.pass_context
def weekly(ctx: click.Context, when: str):
    """
    Weekly report.
    """
    weekly = WeeklyReport(
        week=when,
        options=ctx.meta["options"],
    )
    weekly.process()
    # print(weekly.to_yaml())
    print(weekly.to_markdown())
