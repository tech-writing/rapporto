# Rapporto

Harvest information from GitHub and Slack,
and create reports in Markdown format. [DWIM].

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
    Talk to GitHub and Slack, and easily extend it for other services.
:Flexibility:
    Use as a standalone program or as a library in your own programs.
:Interoperability:
    The output is using Markdown format across the board, so you can
    use it on many services like Discord, Discourse, GitHub, Slack,
    and many more.

## Synopsis

### GitHub

::::{tab-set}

:::{tab-item} Actions
```{code-block} shell
:caption: Report about CI failures on [GHA].
rapporto gh actions --repository=acme/acme-examples
```
:::

:::{tab-item} Activity
```{code-block} shell
:caption: Report about user activity on [GitHub] in [PPP] format.
rapporto gh activity --organization=python --author=AA-Turner --when="2025W04"
```
:::

:::{tab-item} Attention
```{code-block} shell
:caption: Report about bugs and similar important items on [GitHub].
rapporto gh attention --organization=python --when="2025W07"
```
:::

:::{tab-item} Backup
```{code-block} shell
:caption: Full GitHub project backup using [github-backup].
rapporto gh backup --all --pull-details --prefer-ssh --token="${GH_TOKEN}" --repository=kotori daq-tools
```
:::

::::

### Slack

::::{tab-set}

:::{tab-item} Export conversation
```{code-block} shell
:caption: Export [Slack] conversation thread.
rapporto slack export https://acme.slack.com/archives/D018V8WDABA/p1738873838427919
```
:::

::::



```{include} readme.md
:start-line: 15
```

## Contribute

Contributions are very much welcome. The program is still in its infancy,
and needs all support it can get. It is [managed on GitHub].


[DWIM]: https://en.wikipedia.org/wiki/DWIM
[GHA]: https://github.com/features/actions
[GitHub]: https://en.wikipedia.org/wiki/GitHub
[github-backup]: https://pypi.org/project/github-backup/
[managed on GitHub]: https://github.com/tech-writing/rapporto
[PPP]: https://weekdone.com/resources/plans-progress-problems
[Slack]: https://en.wikipedia.org/wiki/Slack_(software)
