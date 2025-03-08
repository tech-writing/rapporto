import os

import pytest
from click.testing import CliRunner


@pytest.fixture
def cli_runner() -> CliRunner:
    return CliRunner()


@pytest.fixture(autouse=True)
def reset_environment(monkeypatch):
    monkeypatch.delenv("GH_TOKEN", raising=False)
    if "GH_TOKEN_TEST" in os.environ:
        monkeypatch.setenv("GH_TOKEN", os.getenv("GH_TOKEN_TEST"))
