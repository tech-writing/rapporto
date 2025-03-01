import logging

import click

from rapporto.notify.slack.conversation import SlackConversation
from rapporto.notify.slack.weekly import SlackWeekly
from rapporto.util import Zapper

logger = logging.getLogger(__name__)

slack_api_token_option = click.option(
    "--slack-token", type=str, envvar="SLACK_TOKEN", required=False, help="Slack API token"
)
slack_channel_option = click.option(
    "--slack-channel", "-c", type=str, envvar="SLACK_CHANNEL", required=False, help="Slack channel"
)


@click.group()
@slack_api_token_option
@slack_channel_option
@click.pass_context
def cli(ctx: click.Context, slack_token: str, slack_channel: str):
    """
    Notify humans and machines.
    """
    if not slack_token:
        raise click.UsageError(
            "Missing option '--slack-token' or environment variable 'SLACK_TOKEN'."
        )
    ctx.meta.update({"slack_token": slack_token})
    ctx.meta.update({"slack_channel": slack_channel})


@cli.command()
@click.option("--week", type=str, required=False, help="Calendar week")
@click.option("--zap", type=str, required=False, help="Zap message again")
@click.pass_context
def weekly(ctx: click.Context, week: str, zap: str):
    """
    Weekly report converged into Slack thread.
    """

    zapper = Zapper(zap)
    zapper.check()

    conversation = SlackConversation(
        api_token=ctx.meta["slack_token"], channel=ctx.meta["slack_channel"]
    )
    section = SlackWeekly(conversation=conversation, week=week)
    section.refresh()

    try:
        if zapper.process():
            conversation.delete()
    except ValueError as e:
        click.echo(f"ERROR: {e}", err=True)
        raise SystemExit(1) from e
