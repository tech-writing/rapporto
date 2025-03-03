import pytest

from pueblo_goof.cli import cli
from pueblo_goof.slack.model import SlackUrl


def test_url_channel():
    url = SlackUrl.from_url("https://acme.slack.com/archives/C08EF2NGZGB")
    assert url.channel_id == "C08EF2NGZGB"
    assert url.thread_ts is None
    assert url.cid is None
    assert url.ts is None


def test_url_message_threaded():
    url = SlackUrl.from_url(
        "https://acme.slack.com/archives/C08EF2NGZGB/p1740478361323219?thread_ts=1740421750.904349&cid=C08EF2NGZGB"
    )
    assert url.channel_id == "C08EF2NGZGB"
    assert url.thread_ts == "1740421750.904349"
    assert url.cid == "C08EF2NGZGB"
    assert url.ts == "1740478361.323219"


def test_cli_send_without_token(cli_runner):
    """
    CLI test: Invoke `goof slack send`.
    """
    result = cli_runner.invoke(
        cli,
        args='slack send --channel="testdrive" --message="**Hello, world.**"',
        catch_exceptions=False,
    )
    assert result.exit_code == 2
    assert (
        "Error: Missing option '--slack-token' or environment variable 'SLACK_TOKEN'."
        in result.output
    )


def test_cli_send_with_invalid_token(cli_runner, capsys):
    """
    CLI test: Invoke `goof slack send`.
    """
    import slack_sdk.errors

    with pytest.raises(slack_sdk.errors.SlackApiError) as ex:
        cli_runner.invoke(
            cli,
            args='slack send --channel="testdrive" --message="**Hello, world.**"',
            env={"SLACK_TOKEN": "xoxb-your-slack-bot-token"},
            catch_exceptions=False,
        )
    assert ex.match("The request to the Slack API failed")
    assert ex.match("The server responded with: {'ok': False, 'error': 'invalid_auth'}")
