import click

from rapporto.opsgenie.core import OpsgenieAlertsClient, OpsgenieAlertsReport


@click.group()
@click.pass_context
def cli(ctx: click.Context):
    """
    Harvest information from Opsgenie.
    """
    pass


@cli.command()
@click.option(
    "--api-key", type=str, envvar="OPSGENIE_API_KEY", required=False, help="Opsgenie API key"
)
@click.option(
    "--start-time", type=str, required=False, help="Start time in format dd-mm-yyyyTHH:MM:SS"
)
@click.option("--days", type=int, required=False, help="Number of days from start time")
@click.option(
    "--format",
    "format_",
    type=click.Choice(["md", "text"]),
    required=False,
    default="md",
    help="Output format: 'md' for markdown, 'text' for nicely formatted terminal output",
)
@click.pass_context
def export_alerts(ctx: click.Context, api_key: str, start_time: str, days: int, format_: str):
    """
    Report about alerts in Opsgenie.
    """
    if not api_key:
        raise click.UsageError(
            "Missing option '--api-key' or environment variable 'OPSGENIE_API_KEY'."
        )

    client = OpsgenieAlertsClient(
        api_key=api_key, query=OpsgenieAlertsClient.query_from_cli_options(ctx)
    )
    report = OpsgenieAlertsReport(client=client)

    try:
        report.process()
    except (ValueError, IOError) as e:
        raise SystemExit(1) from e

    if format_ == "md":
        print(report.to_markdown())
    else:
        print(report.to_text())
