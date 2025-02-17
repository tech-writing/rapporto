from rapporto.cli import cli


def test_cli_version(cli_runner):
    """
    CLI test: Invoke `rapporto --version`.
    """
    result = cli_runner.invoke(
        cli,
        args="--version",
        catch_exceptions=False,
    )
    assert result.exit_code == 0
