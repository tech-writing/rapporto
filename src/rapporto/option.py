import click

github_organization_option = click.option(
    "--github-organization", "--gh-org", type=str, required=True, help="GitHub organization name"
)
github_repository_option = click.option(
    "--github-repository",
    "--gh-repo",
    type=str,
    required=True,
    help="GitHub repository, single or path to file",
)
format_option = click.option(
    "--format",
    "format_",
    type=str,
    required=False,
    default="markdown",
    help="Output format. Default: markdown",
)
when_option = click.option("--when", type=str, required=False, help="Point in time")
