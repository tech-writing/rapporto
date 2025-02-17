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


def test_cli_ppp(cli_runner):
    """
    CLI test: Invoke `rapporto ppp`.
    """
    result = cli_runner.invoke(
        cli,
        args='ppp --organization=panodata --author=dependabot[bot] --timerange="2025W07"',
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert "# PPP report for 2025W07" in result.output
    assert "Activity: aika, rex9" in result.output


def test_cli_qa(cli_runner):
    """
    CLI test: Invoke `rapporto qa`.
    """
    result = cli_runner.invoke(
        cli,
        args="qa --repository=panodata/rapporto",
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert "# QA report" in result.output
