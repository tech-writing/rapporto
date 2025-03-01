from rapporto.notify.slack.model import SlackUrl


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
