import logging

import click

from pueblo_goof.slack.conversation import SlackConversation
from pueblo_goof.slack.model import SlackOptions, slack_api_token_option, slack_channel_option
from pueblo_goof.util import Zapper
from rapporto.option import github_organization_option, github_repository_option
from rapporto.report.model import ReportOptions
from rapporto.report.slack import SlackWeekly
from rapporto.source.github.model import GitHubOptions

logger = logging.getLogger(__name__)


@click.group()
@github_organization_option
@github_repository_option
@slack_api_token_option
@slack_channel_option
@click.pass_context
def cli(
    ctx: click.Context,
    github_organization: str,
    github_repository: str,
    slack_token: str,
    slack_channel: str,
):
    """
    Notify humans and machines.
    """
    if not slack_token:
        raise click.UsageError(
            "Missing option '--slack-token' or environment variable 'SLACK_TOKEN'."
        )
    ctx.meta["github_options"] = GitHubOptions(organization=github_organization).add_repos(
        github_repository
    )
    ctx.meta["slack_options"] = SlackOptions(token=slack_token, channel=slack_channel)
    ctx.meta["report_options"] = ReportOptions(output_format="markdown")


@cli.command()
@click.option("--week", type=str, required=False, help="Calendar week")
@click.option("--zap", type=str, required=False, help="Zap message again")
@click.pass_context
def weekly(ctx: click.Context, week: str, zap: str):
    """
    Weekly report converged into Slack thread.
    """

    github_options: GitHubOptions = ctx.meta["github_options"]
    report_options: ReportOptions = ctx.meta["report_options"]
    slack_options: SlackOptions = ctx.meta["slack_options"]

    conversation = SlackConversation(options=slack_options)
    zapper = Zapper(when=zap, action=conversation.delete)

    section = SlackWeekly(
        week=week,
        github_options=github_options,
        report_options=report_options,
        conversation=conversation,
    )
    section.refresh()

    try:
        zapper.process()
    except Exception as e:
        raise click.ClickException(f"The 'zap' operation failed: {e}") from e
