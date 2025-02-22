import pytest

from rapporto.cli import cli


@pytest.fixture(autouse=True)
def reset_environment(monkeypatch):
    monkeypatch.delenv("OPSGENIE_API_KEY", raising=False)


def test_cli_export_without_token(cli_runner, caplog):
    """
    CLI test: Invoke `rapporto opsgenie export-alerts`.
    """
    result = cli_runner.invoke(
        cli,
        args="opsgenie export-alerts",
        catch_exceptions=False,
    )
    assert result.exit_code == 2
    assert (
        "Error: Missing option '--api-key' or environment variable 'OPSGENIE_API_KEY'."
        in result.output
    )


def test_cli_export_with_invalid_token(cli_runner, caplog):
    """
    CLI test: Invoke `rapporto opsgenie export-alerts`.
    """
    result = cli_runner.invoke(
        cli,
        args="opsgenie export-alerts",
        env={"OPSGENIE_API_KEY": "your-api-key"},
        catch_exceptions=False,
    )
    assert result.exit_code == 1
    assert (
        "Opsgenie configuration error: Unprocessable Entity: "
        "Semantic errors in request body; Key format is not valid!" in caplog.messages
    )
