import logging
import sys
import typing as t
from pathlib import Path

import click
from slack_sdk.errors import SlackApiError

from rapporto.notify.slack.conversation import SlackConversation
from rapporto.slack.core import SlackThreadExporter
from rapporto.util import Zapper

logger = logging.getLogger(__name__)

slack_api_token_option = click.option(
    "--slack-token", type=str, envvar="SLACK_TOKEN", required=False, help="Slack API token"
)


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


@cli.command()
@click.option("--channel", "-c", type=str, required=False, help="Slack channel")
@click.option("--reply-to", "-r", type=str, required=False, help="Message to reply to")
@click.option("--update", type=str, required=False, help="Message to update")
@click.option("--message", "-m", type=str, multiple=True, required=True, help="Message text")
@click.option("--zap", type=str, required=False, help="Zap message again")
@click.pass_context
def send(
    ctx: click.Context, channel: str, reply_to: str, update: str, message: t.List[str], zap: str
) -> None:
    """
    Send a Slack message in Markdown format.

    https://acme.slack.com/archives/C08EF2NGZGB/p1740421750904349
    https://acme.slack.com/archives/C08EF2NGZGB/p1740437309683889?thread_ts=1740421750.904349&cid=C08EF2NGZGB
    """

    zapper = Zapper(zap)
    zapper.check()

    if not (channel or update or reply_to):
        raise click.UsageError("Please provide either 'channel' or 'update' or 'reply_to'")

    channel = channel or update or reply_to

    conversation = SlackConversation(api_token=ctx.meta["slack_token"], channel=channel)
    message_ids = []
    for msg in message:
        if msg == "-":
            msg = sys.stdin.read()
        elif Path(msg).exists():
            msg = Path(msg).read_text()
        if update:
            response = conversation.update(ts=update, markdown=msg)
        else:
            response = conversation.send(markdown=msg, reply_to=reply_to)
        message_id = response["ts"]
        message_ids.append(message_id)

    try:
        if zapper.process():
            conversation.delete()
    except ValueError as e:
        click.echo(f"ERROR: {e}", err=True)
        raise SystemExit(1) from e


@cli.command()
@click.option("--channel", "-c", type=str, required=False, help="Slack channel")
@click.option(
    "--id",
    "identifiers",
    type=str,
    multiple=True,
    required=True,
    help="Slack message ID, optionally multiple ones",
)
@click.pass_context
def delete(ctx: click.Context, channel: str, identifiers: t.List[str]):
    """
    Delete individual Slack messages by IDs or URLs.
    """
    if not (channel or identifiers):
        raise click.UsageError("Please provide either 'channel' and/or 'identifiers'")
    channel = channel or identifiers[0]
    conversation = SlackConversation(api_token=ctx.meta["slack_token"], channel=channel)
    for identifier in identifiers:
        try:
            conversation.delete_message(identifier=identifier)
        except SlackApiError as ex:
            msg = f"Deleting message failed: {ex}"
            logger.error(msg)
            # raise click.ClickException(msg)
