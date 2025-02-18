from rapporto.cli import cli


def test_cli_export_without_token(cli_runner):
    """
    CLI test: Invoke `rapporto slack export`.
    """
    result = cli_runner.invoke(
        cli,
        args="slack export https://acme.slack.com/archives/D018V8WDABA/p1738873838427919",
        catch_exceptions=False,
    )
    assert result.exit_code == 2
    assert (
        "Error: Missing option '--slack-token' or 'SLACK_TOKEN' environment variable."
        in result.output
    )


def test_cli_export_with_invalid_token(cli_runner, caplog):
    """
    CLI test: Invoke `rapporto slack export`.
    """
    result = cli_runner.invoke(
        cli,
        args="slack export https://acme.slack.com/archives/D018V8WDABA/p1738873838427919",
        env={"SLACK_TOKEN": "xoxb-your-slack-bot-token"},
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert "Error fetching channel info: invalid_auth" in caplog.messages
