# Rapporto

A program for harvesting information from GitHub and Slack.

```{toctree}
:maxdepth: 1
:hidden:

guide/index
project
```

## Features

:DWIM:
    Harvest, report, summarize, and notify like you always wanted to.
:Polyglot:
    Talk to GitHub and Slack, and extensible for other services.
:Flexibility:
    Use as a standalone project or as a library in your own programs.

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

::::

## Information

```{include} readme.md
:start-line: 3
```


[DWIM]: https://en.wikipedia.org/wiki/DWIM
[GHA]: https://github.com/features/actions
[PPP]: https://weekdone.com/resources/plans-progress-problems
