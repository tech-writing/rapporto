# Rapporto

A program for harvesting information from GitHub.

## Usage

```shell
wget https://github.com/tech-writing/rapporto/raw/refs/heads/main/rapporto.py
uv run rapporto.py ppp --organization=python --author=AA-Turner --timerange="2025-01-01..2025-01-31"
uv run rapporto.py ppp --organization=python --author=AA-Turner --timerange="2025W04"
```

```shell
python rapporto.py qa --repository=acme/acme-examples
python rapporto.py qa --repositories-file=acme-repositories.txt
```


## Prior art
- https://github.com/saschpe/rapport
- https://github.com/nedbat/dinghy
- https://github.com/kneth/gh-utils
- https://github.com/slackapi/slack-github-action
- Many more.
