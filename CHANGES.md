# Change log

## In progress
- GitHub/Bugs: Also display `state==closed` items, formatting them
  using ~~strikethrough~~.
- Goof: Added wrapper around Slack conversations, available per
  CLI `goof slack send`.
- Shell (Reports/Daily+Weekly): Generate daily and weekly reports in
  Markdown or YAML formats, available per `rapporto report`.
- Shell (Slack/Weekly): Publish daily reports to Slack, in a per-week
  context, with hourly granularity, available per `rapporto notify`.
- Slack/Markdown: Fixed encoding link titles including square brackets

## v0.3.0, 2025-02-24
- Opsgenie: Added alert reporter. Thanks, @WalBah.
- Opsgenie: Added time interval parsing using Aika, i.e. `--when` option
- GitHub/API: Use `updated` instead of `created` to get the whole picture

## v0.2.0, 2025-02-24
- GitHub/CI: Fixed displaying failed workflow runs on pull requests
  which succeeded afterward
- GitHub/Bugs: Improved rendering of Markdown sections
- GitHub/Bugs: Also consider labels `stale` and `type: Bug` as relevant
- GitHub/Backup: Added wrapper around `github-backup`
- Options: Use `aika` for parsing time intervals.
  Also, rename command-line option `--timerange` to `--when`.
- Options: Added `--format=mrkdwn` option, improving Slack messages

## v0.1.0, 2025-02-20
- Started using `GH_TOKEN` environment variable instead of `GITHUB_TOKEN`,
  see [Authenticate to GitHub in GitHub Actions].
- Refactored codebase to become a real Python package
- CI: Added GHA workflow invoking `poe check`, and Dependabot configuration
- GitHub: Refactored current adapter code into `rapporto.github`, to accompany
  including other adapters
- Added documentation using Sphinx and PyData Sphinx Theme, and RTD.
  See [Rapporto Documentation].
- Slack: Added conversation exporter. Thanks, @WalBeh.
- Slack: Refactored CLI to use Click
- GitHub: Added `GitHubAttentionReport`, to report about important items
  that deserve your attention, bugs first.
- GitHub: Make options optional, to report about the complete corpus
- GitHub: Display full project names `<org>/<project>` within Markdown links

[Authenticate to GitHub in GitHub Actions]: https://josh-ops.com/posts/gh-auth-login-in-actions/
[Rapporto Documentation]: https://rapporto.readthedocs.io/

## v0.0.2, 2025-02-17
- Fixed link templating API vs. HTML
- Feature: Accept year-of-week time range format like `2025W06`
- Added subcommand "qa", for reporting about PR failures
- Added logging
- Fixed using GITHUB_TOKEN only if it's defined
- Improved documentation
- Markdown: Sanitized link titles that include `[]` brackets
- Report: Improved layout

## v0.0.1, 2025-01-21
- Added command-line interface (CLI).
- Added "top/significant changes" feature, roughly based on those PR attributes:
  ```
  comments	0
  review_comments	0
  commits	1
  additions	26
  deletions	25
  changed_files	2
  ```

## v0.0.0, 2025-01-20
- Made it work by translating GitHub search queries into Python code.
  ```text
  "org:python author:AA-Turner created:2025-01-01..2025-01-31 is:issue"
  "org:python author:AA-Turner created:2025-01-01..2025-01-31 is:pr"
  ```
  ```shell
  rapporto github activity --organization=python --author=AA-Turner --when="2025-01-01..2025-01-31"
  ```
