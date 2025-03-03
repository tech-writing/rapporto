import click
from click_aliases import ClickAliasedGroup

from rapporto.github.cli import cli as github_cli
from rapporto.notify.cli import cli as notify_cli
from rapporto.opsgenie.cli import cli as opsgenie_cli
from rapporto.report.cli import cli as report_cli
from rapporto.slack.cli import cli as slack_cli
from rapporto.util import setup_logging


@click.group(cls=ClickAliasedGroup)
@click.option("--verbose", is_flag=True, required=False, help="Turn on logging")
@click.option("--debug", is_flag=True, required=False, help="Turn on logging with debug level")
@click.version_option()
@click.pass_context
def cli(ctx: click.Context, verbose: bool, debug: bool):
    setup_logging(verbose=verbose)


cli.add_command(github_cli, "gh")
cli.add_command(opsgenie_cli, "opsgenie")
cli.add_command(slack_cli, "slack")
cli.add_command(notify_cli, "notify")
cli.add_command(report_cli, "report")
