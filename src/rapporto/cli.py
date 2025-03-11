import click
from click_aliases import ClickAliasedGroup

from rapporto.animate.cli import cli as animate_cli
from rapporto.notify.cli import cli as notify_cli
from rapporto.report.cli import cli as report_cli
from rapporto.source.changes.cli import cli as changes_cli
from rapporto.source.github.cli import cli as github_cli
from rapporto.source.opsgenie.cli import cli as opsgenie_cli
from rapporto.source.slack.cli import cli as slack_cli
from rapporto.util import setup_logging


@click.group(cls=ClickAliasedGroup)
@click.option("--verbose", is_flag=True, required=False, help="Turn on logging")
@click.option("--debug", is_flag=True, required=False, help="Turn on logging with debug level")
@click.version_option()
@click.pass_context
def cli(ctx: click.Context, verbose: bool, debug: bool):
    setup_logging(verbose=verbose)


cli.add_command(github_cli, "github", aliases=["gh"])
cli.add_command(opsgenie_cli, "opsgenie")
cli.add_command(slack_cli, "slack")
cli.add_command(notify_cli, "notify")
cli.add_command(report_cli, "report")
cli.add_command(animate_cli, "animate")
cli.add_command(changes_cli, "changes")
