import logging

import click

from pueblo_goof.slack.model import slack_api_token_option
from rapporto.slack.core import SlackThreadExporter

logger = logging.getLogger(__name__)


@click.group()
@slack_api_token_option
@click.pass_context
def cli(ctx: click.Context, slack_token: str):
    """
    Harvest information from Slack.
    """
    if not slack_token:
        raise click.UsageError(
            "Missing option '--slack-token' or environment variable 'SLACK_TOKEN'."
        )
    ctx.meta.update({"slack_token": slack_token})


@cli.command()
@click.argument("url", type=str, required=True)
@click.pass_context
def export(ctx: click.Context, url: str):
    """
    Export a Slack thread into Markdown format.
    """
    exporter = SlackThreadExporter(ctx.meta["slack_token"])
    exporter.export_thread(url)
