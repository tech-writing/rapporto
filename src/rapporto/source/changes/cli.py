import typing as t

import click

from rapporto.source.changes.core import aggregate


@click.command(context_settings=dict(ignore_unknown_options=True))
@click.argument("input", type=click.UNPROCESSED, required=False, nargs=-1)
@click.option("--output", type=str, required=False, help="Output path")
@click.option(
    "--format",
    "format_",
    type=click.Choice(["md", "rst", "text"]),
    required=False,
    default="rst",
    help="Output format: 'md' for markdown, 'rst' for reStructuredText, 'text' for terminal output",
)
@click.pass_context
def cli(ctx: click.Context, input: t.List[str], output: str, format_: str) -> None:  # noqa: A002
    """
    Aggregate change log files.
    """
    aggregate(input[0], output)
