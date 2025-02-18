# Backlog

## Iteration +1
- Rename subcommand `qa` to `qa-ci`
- Add TagFinder, used by `qa-bugs`
- Publish package to PyPI

## Iteration +2
- Documentation: Baseline
- Documentation: Recipes how to relay reports to messenger channels

## Iteration +3
- Report: Consider more attributes for "top changes":
  body, created_at, closed_at, gravity (number of inbound links). 
- Backend: Add GitHub API authentication, to be able to include
  contributions to private repositories.
- Report: Wide vs. compressed reports, e.g. using link labels like `[#]` (issues)
  and `[P]`, per enumerated repository, referencing activity within the
  corresponding time range.
- Report: Make configurable if Rapporto shall only return a share of top changes,
  or each one. Currently, the default is 2/5, but 1/3 is also reasonable.

## Done
- Make it work.
- PPP: Add "top changes" feature.
- QA: Harvest GitHub Actions outcomes.
- Make it a real Python package
- Add CI checks
- Absorb https://github.com/WalBeh/slack-thread-exporter by @WalBeh
