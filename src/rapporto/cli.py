import click
from pueblo.util.cli import boot_click

from rapporto.github.cli import cli as github_cli
from rapporto.slack.cli import cli as slack_cli


@click.group()
@click.option("--verbose", is_flag=True, required=False, help="Turn on logging")
@click.option("--debug", is_flag=True, required=False, help="Turn on logging with debug level")
@click.version_option()
@click.pass_context
def cli(ctx: click.Context, verbose: bool, debug: bool):
    return boot_click(ctx, verbose, debug)


cli.add_command(github_cli, "gh")
cli.add_command(slack_cli, "slack")
