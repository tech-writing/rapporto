from rapporto.cli import cli


def test_cli_ppp(cli_runner):
    """
    CLI test: Invoke `rapporto gh ppp`.
    """
    result = cli_runner.invoke(
        cli,
        args="gh ppp --organization=panodata --author=dependabot[bot] --timerange=2025W07",
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert "# PPP report for 2025W07" in result.output
    assert "Activity: aika, rex9" in result.output


def test_cli_ci(cli_runner):
    """
    CLI test: Invoke `rapporto gh ci`.
    """
    result = cli_runner.invoke(
        cli,
        args="gh ci --repository=panodata/rapporto",
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert "# CI failures report" in result.output


def test_cli_att(cli_runner):
    """
    CLI test: Invoke `rapporto gh att`.
    """
    result = cli_runner.invoke(
        cli,
        args="gh att --organization=tech-writing --timerange=2024W43",
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert "# Importance report 2024W43" in result.output
    assert "sphinx-design-elements" in result.output
