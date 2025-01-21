# Change log

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
  uv run rapporto.py --organization=python --author=AA-Turner --timerange="2025-01-01..2025-01-31"
  ```
