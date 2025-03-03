import click

github_organization_option = click.option(
    "--github-organization", "--gh-org", type=str, required=True
)
