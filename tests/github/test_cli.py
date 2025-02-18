from rapporto.cli import cli


def test_cli_ppp(cli_runner):
    """
    CLI test: Invoke `rapporto gh ppp`.
    """
    result = cli_runner.invoke(
        cli,
        args='gh ppp --organization=panodata --author=dependabot[bot] --timerange="2025W07"',
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert "# PPP report for 2025W07" in result.output
    assert "Activity: aika, rex9" in result.output


def test_cli_qa(cli_runner):
    """
    CLI test: Invoke `rapporto gh qa`.
    """
    result = cli_runner.invoke(
        cli,
        args="gh qa --repository=panodata/rapporto",
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert "# QA report" in result.output
