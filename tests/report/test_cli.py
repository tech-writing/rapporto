import os

import pytest

from rapporto.cli import cli


@pytest.fixture(autouse=True)
def reset_environment(monkeypatch):
    monkeypatch.setenv("GH_TOKEN", os.getenv("GH_TOKEN_TEST"))


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
