import logging
import sys
import typing as t
from pathlib import Path

import click
from slack_sdk.errors import SlackApiError

from pueblo_goof.slack.conversation import SlackConversation
from pueblo_goof.slack.model import slack_api_token_option
from pueblo_goof.util import Zapper

logger = logging.getLogger(__name__)


@click.group()
@click.pass_context
def cli(ctx: click.Context):
    """
    Goofing. Yeah.
    """
    pass


@cli.group()
@slack_api_token_option
@click.pass_context
def slack(ctx: click.Context, slack_token: str):
    """
    Send information to Slack.
    """
    if not slack_token:
        raise click.UsageError(
            "Missing option '--slack-token' or environment variable 'SLACK_TOKEN'."
        )
    ctx.meta.update({"slack_token": slack_token})


@slack.command()
@click.option(
    "--message",
    "-m",
    type=str,
    multiple=True,
    required=True,
    help="Text of the message in Markdown format",
)
@click.option("--channel", "-c", type=str, required=False, help="Target channel (name, ID, or URL)")
@click.option("--reply-to", "-r", type=str, required=False, help="Message to reply to (ID or URL)")
@click.option("--update", "-u", type=str, required=False, help="Message to update (ID or URL)")
@click.option("--zap", "-z", type=str, required=False, help="Zap message again")
@click.pass_context
def send(
    ctx: click.Context, channel: str, reply_to: str, update: str, message: t.List[str], zap: str
) -> None:
    """
    Send one or multiple Slack messages in Markdown format.
    """

    if not (channel or update or reply_to):
        raise click.UsageError("Please provide either 'channel' or 'update' or 'reply_to'")

    channel = channel or update or reply_to

    conversation = SlackConversation(api_token=ctx.meta["slack_token"], channel=channel)
    zapper = Zapper(when=zap, action=conversation.delete)

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
        zapper.process()
    except Exception as e:
        raise click.ClickException(f"The 'zap' operation failed: {e}") from e


@slack.command()
@click.option("--channel", "-c", type=str, required=False, help="Target channel (name, ID, or URL)")
@click.option(
    "--id",
    "identifiers",
    type=str,
    multiple=True,
    required=True,
    help="Message to delete (ID or URL)",
)
@click.pass_context
def delete(ctx: click.Context, channel: str, identifiers: t.List[str]):
    """
    Delete individual Slack message by ID or URL, also multiple ones.
    """
    if not (channel or identifiers):
        raise click.UsageError("Please provide either 'channel' and/or 'identifiers'")

    # TODO: Currently, when no channel is provided, but fully-qualified message identifiers,
    #       conveyed through Slack URLs, the channel is derived from the first identifier.
    #       To make it work in all situations, this code will need to iterate all identifiers,
    #       and consider each one individually, as it might concern different channels.
    channel = channel or identifiers[0]

    conversation = SlackConversation(api_token=ctx.meta["slack_token"], channel=channel)
    had_errors = False
    for identifier in identifiers:
        try:
            conversation.delete_message(identifier=identifier)
        except SlackApiError as ex:
            msg = f"Deleting message failed: {ex}"
            logger.error(msg)
            had_errors = True
    if had_errors:
        raise click.ClickException(
            "The 'delete' operation failed or was not completely successful."
        )
