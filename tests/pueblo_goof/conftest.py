import pytest


@pytest.fixture(autouse=True)
def reset_environment(monkeypatch):
    monkeypatch.delenv("SLACK_TOKEN", raising=False)
