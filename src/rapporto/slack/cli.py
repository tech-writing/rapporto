import click

from rapporto.slack.core import SlackThreadExporter


@click.group()
@click.pass_context
def cli(ctx: click.Context):
    """
    Harvest information from Slack.
    """
    pass


@cli.command()
@click.argument("url", type=str, required=True)
@click.option(
    "--slack-token", type=str, envvar="SLACK_TOKEN", required=False, help="Slack API token"
)
def export(url: str, slack_token: str):
    """
    Export a Slack thread into Markdown format.
    """
    if not slack_token:
        raise click.UsageError(
            "Missing option '--slack-token' or environment variable 'SLACK_TOKEN'."
        )

    exporter = SlackThreadExporter(slack_token)
    exporter.export_thread(url)
