# Rapporto

A program for harvesting information from GitHub and Slack, [DWIM].

```{toctree}
:maxdepth: 1
:hidden:

install
guide/index
project
```

## Features

:DWIM:
    Harvest, report, summarize, and notify like you always wanted to.
:Polyglot:
    Talk to GitHub and Slack, and extend it easily for other services.
:Flexibility:
    Use as a standalone program or as a library in your own programs.

## Synopsis

::::{tab-set}

:::{tab-item} GitHub: PPP
```{code-block} shell
:caption: Report about user activity in [PPP] format.
rapporto gh ppp --organization=python --author=AA-Turner --timerange="2025W04"
```

:::

:::{tab-item} GitHub: QA/CI
```{code-block} shell
:caption: Report about CI failures on [GHA].
rapporto gh qa --repository=acme/acme-examples
```
:::

:::{tab-item} Slack: Export thread
```{code-block} shell
:caption: Export Slack conversation / thread.
rapporto slack export https://acme.slack.com/archives/D018V8WDABA/p1738873838427919
```
:::

::::



[DWIM]: https://en.wikipedia.org/wiki/DWIM
[GHA]: https://github.com/features/actions
[PPP]: https://weekdone.com/resources/plans-progress-problems
