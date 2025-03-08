import click

from rapporto.animate.git import render


@click.group()
@click.pass_context
def cli(
    ctx: click.Context,
):
    """
    Animate time series information from different sources.
    """
    pass


@cli.command(
    context_settings=dict(
        ignore_unknown_options=True,
    )
)
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def git(ctx: click.Context, args):
    """
    Render video of VCS repository commit history.
    """
    render(list(args))
