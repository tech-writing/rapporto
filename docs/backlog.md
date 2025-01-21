# Backlog

## Iteration +1
- [x] Make it work.
- [x] Add "top changes" feature.
- [o] Report: Consider more attributes for "top changes":
  body, created_at, closed_at, gravity (number of inbound links). 
- [o] Backend: Add GitHub API authentication, to be able to include
  contributions to private repositories.
- [o] Report: Wide vs. compressed reports, e.g. using link labels like `[#]` (issues)
  and `[P]`, per enumerated repository, referencing activity within the
  corresponding time range.
- [o] Report: Make configurable if Rapport shall only return a share of top changes,
  or each one. Currently, the default is 2/5, but 1/3 is also reasonable.

## Iteration +2
- [o] Make it a package, and publish to PyPI.
