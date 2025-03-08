# Backlog

## Iteration +1
- Docs about end-to-end automation
  Advise about GH tokens and caching, re. `http_cache.sqlite`
- Bugfixing and refactoring: Aika and Pueblo
- Absorb Manticore extensions as CLI utilities
  https://github.com/tech-writing/manticore-ext

## Iteration +2
- Options: Program currently understands `--slack-token=`, but lacks `--github-token=`
- Configuration: Per `[tool]` section in `pyproject.toml`
- General: Summaries, using the excellent `llm` package
- GitHub/Bugs: Add labels `blocked`, `blocked-by XXX`, `impediment`
- GitHub: Search items in specific columns (e.g. Blocked By) of specific boards
- GitHub: Search items with significant amounts of reactions
- GitHub: Search items with significant (amount or length of) comments
- GitHub: Search items with significant (amount or length of) inbound links
  Example: https://github.com/crate/crate/issues/10063
- GitHub: Search items with EPIC or other keywords in its titles
- GitHub: Search items with people assignments
- GitHub/API: On errors, the JSON response includes the reason as an
  error message. However, it isn't displayed, yet.
- GitHub: Report about stale issues
- Options: Make `limit=100` configurable? Is paging needed?
- `github-backup` can do "Exceeded rate limit of 5000 requests;
  waiting 77 seconds to reset". Do we also need it?
- UI/Console: Spice up Markdown output using `rich` and friends

## Iteration +3
- Data: Identify items with high conversation activity (comment frequency, etc.)
- Report: Consider more attributes for "top changes":
  body, created_at, closed_at, gravity (number of inbound links). 
- Backend: Add GitHub API authentication, to be able to include
  contributions to private repositories.
- Report: Wide vs. compressed reports, e.g. using link labels like `[#]` (issues)
  and `[P]`, per enumerated repository, referencing activity within the
  corresponding time range.
- Report: Make configurable if Rapporto shall only return a share of top changes,
  or each one. Currently, the default is 2/5, but 1/3 is also reasonable.
- https://github.com/slackapi/python-slack-events-api
- https://github.com/dizzbot/productivity
- Markdown rendering with nested offsets:
  https://github.com/executablebooks/MyST-Parser/blob/8a44f5d35197b19aab2f1fe35b6f1dce4960bce5/myst_parser/mdit_to_docutils/base.py#L283-L290
- Bring back `mrkdwn`?
  > #### Slack flavored Markdown
  >
  > The program can output two flavors of Markdown. Standard Markdown is default,
  > while the [Slack `mrkdwn` format] can be produced using the `--format=mrkdwn`
  > command-line option. Rapporto uses the [markdown-to-mrkdwn] package here.
  >
  > [markdown-to-mrkdwn]: https://pypi.org/project/markdown-to-mrkdwn/
  > [Slack `mrkdwn` format]: https://api.slack.com/reference/surfaces/formatting#basic-formatting
- UI/Slack: https://api.slack.com/messaging/files
- UI/Slack: chat_scheduleMessage

## Done
- Make it work.
- PPP: Add "top changes" feature.
- QA: Harvest GitHub Actions outcomes.
- Make it a real Python package
- Add CI checks
- Absorb https://github.com/WalBeh/slack-thread-exporter by @WalBeh
- Documentation: Baseline
- Added basic
- Options: Make options optional, to report about the complete corpus
- Publish package to PyPI
- Report: On the CI report, render sections only conditionally
- GitHub/CI: Can the retrieval process be optimized, not needing to iterate
  repositories manually? No: The GitHub API is per-repository.
- Report: On HTML links, always include the org name as prefix
- GitHub/Bugs: Add `stale` label
- GitHub/Bugs: More flexible processing of "labels" vs. "sections",
  i.e. improve grouping code, making it more maintainable.
- GitHub/Bugs: Add label `type: Bug`
- Documentation: Include breadcrumbs into static docs, not just README
- Opsgenie: Add subsystem
- Refactoring: Spread GitHub modules along the feature axis
- GitHub: Export conversations per GitHub Backup
- Options: Parse time intervals using `aika`
- Slack: Support for `mrkdwn` output
- GitHub: Process `created` + `updated`, not just `created`
- Shell '25: Introduce _daily_ and _weekly_ operation modes / interfaces
- Docs: Generic page about `--when` option
- Naming things: `source` vs. `sink` vs. Slack CLI domains
- Project layout and docs: Bring up to speed
- Docs: Caveats / Philosophy
- UI/Slack: Improve zapping
- GitHub/Actions: Currently lacks parameter `--when`
- GitHub/Activity: Section about "Top issues"
- Shell/Daily: Interleave CI reports
- GitHub/Activity: Permit running on multiple organizations
- `rapporto report` without `--github-repository` should iterate **all** repositories
- Absorb PyGource. https://github.com/cicerops/pygource
