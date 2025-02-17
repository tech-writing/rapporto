# Rapporto

A program for harvesting information from GitHub.

## Setup

Soft-install the program from GitHub.
```shell
brew install uv
rapporto() { uv run https://github.com/tech-writing/rapporto/raw/refs/heads/main/rapporto.py -- "$@"; }
```

For not exhausting the API rate limit too quickly,
please provide a valid GitHub token. This one is invalid.
```shell
export GH_TOKEN=ghp_600VEZtdzinvalid7K2R86JTiKJAAp1wNwVP
```

## Usage

### PPP reports
Report about activities of individual authors.
```shell
rapporto ppp --organization=python --author=AA-Turner --timerange="2025-01-01..2025-01-31"
rapporto ppp --organization=python --author=AA-Turner --timerange="2025W04"
```

### QA/CI reports
Report about activities of GitHub Actions workflow runs.
```shell
rapporto qa --repository=acme/acme-examples
rapporto qa --repositories-file=acme-repositories.txt
```


## Prior art
- https://github.com/saschpe/rapport
- https://github.com/nedbat/dinghy
- https://github.com/kneth/gh-utils
- https://github.com/slackapi/slack-github-action
- Many more.
