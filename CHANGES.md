# Changelog

## In progress

## v0.6.0, 2025-03-11
- Shell/Notify: Split root message into root+preamble, including links
  to root message and producer.
- Documentation: Added dedicated pages about sandbox installation,
  and text vs. slack reports
- Source/Changes: Added change log aggregator from _Goof suite_

## v0.5.0, 2025-03-09
- GitHub/Attention: Compare labels per lower-case
- GitHub/Attention: Added label "incidents", considering as important
- GitHub/Attention: Improved labels processing
- GitHub/Attention: Added DIY inquiry links
- GitHub/Attention: Added idle notice
- GitHub/Activity: Accept inquiring multiple organizations and authors
- Shell/Notify: Fixed invocation without `--zap=`
- Shell/Notify: Improved preamble, adding "Producer" field
- Shell/Report: Made `--github-repository` option optional
- Shell/Animate: Added PyGource renderer from _Goof suite_

## v0.4.0, 2025-03-05
- GitHub/Attention: Also display `state==closed` items, formatting them
  using ~~strikethrough~~.
- Goof: Added wrapper around Slack conversations, available per
  CLI `goof slack send`.
- Shell (Reports/Daily+Weekly): Generate daily and weekly reports in
  Markdown or YAML formats, available per `rapporto report`.
- Shell (Slack/Weekly): Publish daily reports to Slack, in a per-week
  context, with hourly granularity, available per `rapporto notify`.
- Slack/Markdown: Fixed encoding link titles including square brackets
- Time Interval: Fixed `week_to_day_range`
- GitHub/Actions: Permitted commandeering the time interval per `--when` option
- GitHub/Actions: Added filtering duplicates
- GitHub/Activity: Added section about "Top issues"
- Shell/Daily: Interleaved Attention vs. CI reports

## v0.3.0, 2025-02-24
- Opsgenie: Added alert reporter. Thanks, @WalBah.
- Opsgenie: Added time interval parsing using Aika, i.e. `--when` option
- GitHub/API: Use `updated` instead of `created` to get the whole picture

## v0.2.0, 2025-02-24
- GitHub/Actions: Fixed displaying failed workflow runs on pull requests
  which succeeded afterward
- GitHub/Attention: Improved rendering of Markdown sections
- GitHub/Attention: Also consider labels `stale` and `type: Bug` as relevant
- GitHub/Backup: Added wrapper around `github-backup`
- Options: Use `aika` for parsing time intervals.
  Also, rename command-line option `--timerange` to `--when`.
- Slack/Options: Added `--format=mrkdwn` option, improving Slack messages

## v0.1.0, 2025-02-20
- GitHub: Started using `GH_TOKEN` environment variable instead of `GITHUB_TOKEN`,
  see [Authenticate to GitHub in GitHub Actions].
- Project: Refactored codebase to become a real Python package
- Project: Added CI/GHA workflow invoking `poe check`, and Dependabot configuration
- GitHub: Refactored current adapter code into `rapporto.github`, to accompany
  including other adapters
- Project: Added documentation using Sphinx and PyData Sphinx Theme, and RTD.
  See [Rapporto Documentation].
- Slack/Export: Added conversation exporter. Thanks, @WalBeh.
- Slack/Export: Refactored CLI to use Click
- GitHub/Attention: Added `GitHubAttentionReport`, to report about important items
  that deserve your attention, bugs first.
- GitHub: Make options optional, to report about the complete corpus
- GitHub: Display full project names `<org>/<project>` within Markdown links

[Authenticate to GitHub in GitHub Actions]: https://josh-ops.com/posts/gh-auth-login-in-actions/
[Rapporto Documentation]: https://rapporto.readthedocs.io/

## v0.0.2, 2025-02-17
- GitHub/API: Fixed link templating API vs. HTML
- UX: Accept year-of-week time range format like `2025W06`
- GitHub/Actions: Added subcommand "qa", for reporting about PR failures
- Infra: Added logging
- GitHub: Fixed using GITHUB_TOKEN only if it's defined
- Project: Improved documentation
- GitHub/Activity: Markdown: Sanitized link titles that include `[]` brackets
- GitHub/Activity: Improved report layout

## v0.0.1, 2025-01-21
- GitHub/Activity: Added command-line interface (CLI).
- GitHub/Activity: Added "top/significant changes" feature, roughly based on those PR attributes:
  ```
  comments	0
  review_comments	0
  commits	1
  additions	26
  deletions	25
  changed_files	2
  ```

## v0.0.0, 2025-01-20
- GitHub/Activity: Made it work by translating GitHub search queries into Python code.
  ```text
  "org:python author:AA-Turner created:2025-01-01..2025-01-31 is:issue"
  "org:python author:AA-Turner created:2025-01-01..2025-01-31 is:pr"
  ```
  ```shell
  rapporto github activity --organization=python --author=AA-Turner --when="2025-01-01..2025-01-31"
  ```
