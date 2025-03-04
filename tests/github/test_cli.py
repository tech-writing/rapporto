import os

import pytest

from rapporto.cli import cli


@pytest.fixture(autouse=True)
def reset_environment(monkeypatch):
    monkeypatch.setenv("GH_TOKEN", os.getenv("GH_TOKEN_TEST"))


def test_cli_activity(cli_runner):
    """
    CLI test: Invoke `rapporto github activity`.
    """
    result = cli_runner.invoke(
        cli,
        args="github activity --organization=panodata --author=dependabot[bot] --when=2025W07",
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert "# Activity report for 2025W07" in result.output
    assert "Activity: aika, rex9" in result.output


def test_cli_ci(cli_runner):
    """
    CLI test: Invoke `rapporto github actions`.
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
    CLI test: Invoke `rapporto github attention`.
    """
    result = cli_runner.invoke(
        cli,
        args="gh att --organization=tech-writing --when=2025W08",
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert "# Attention report 2025W08" in result.output
    assert "sphinx-design-elements" in result.output


def test_cli_backup_unauthorized(cli_runner, capfd):
    """
    CLI test: Invoke `rapporto github backup`.
    """
    result = cli_runner.invoke(
        cli,
        args="gh backup --repository=rapporto tech-writing",
        catch_exceptions=False,
    )
    assert result.exit_code == 2
    assert "ERROR: Command" in result.output

    out, err = capfd.readouterr()
    assert "API request returned HTTP 401: Unauthorized" in err
