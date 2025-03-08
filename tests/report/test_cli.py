import pytest

from rapporto.cli import cli


def test_cli_report_daily(cli_runner):
    """
    CLI test: Invoke `rapporto report daily`.
    """
    result = cli_runner.invoke(
        cli,
        args="report --gh-org=panodata daily",
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert "# CI failures report" in result.output
    assert "# Attention report" in result.output


@pytest.mark.xfail(strict=False)
def test_cli_report_weekly(cli_runner):
    """
    CLI test: Invoke `rapporto report weekly`.
    """
    result = cli_runner.invoke(
        cli,
        args="report --gh-org=panodata weekly",
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert "# CI failures report" in result.output
    assert "# Attention report" in result.output
