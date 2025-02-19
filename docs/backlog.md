# Backlog

## Iteration +1
- Publish package to PyPI

## Iteration +2
- Options: Make `limit=100` configurable. Is paging needed?
- Documentation: Recipes how to relay reports to messenger channels
- Data: Search items with significant reactions
- Data: Search items with EPIC or other keywords in its titles
- Data: Search for assignments
- Report: On the CI report, render sections only conditionally
- Report: On HTML links, always include the org name as prefix
- GitHub/CI: Can the retrieval process be optimized, not needing to iterate
  repositories manually?
- GitHub/Bugs: More flexible processing of "labels" vs. "sections",
  i.e. improve grouping code, making it more maintainable.
- GitHub/API: On errors, the JSON response includes the reason as an
  error message. However, it isn't displayed, yet.

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
