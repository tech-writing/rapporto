# Installation

We recommend to use the [uv] package manager for installing or running Rapporto.
```shell
{apt,brew,pip,zypper} install uv
```

## Persistent

Install package from [PyPI] as a [tool].
```shell
uv tool install --upgrade rapporto
```

## Ephemeral

Soft-install package from GitHub.

Use the development head.
```shell
alias rapporto="uvx --with 'rapporto @ https://github.com/tech-writing/rapporto/archive/refs/heads/main.zip' -- rapporto"
```

Use a specific version.
```shell
alias rapporto="uvx --with 'rapporto @ https://github.com/tech-writing/rapporto/archive/refs/tags/v0.0.2.zip' -- rapporto"
```

## non-uv

If you can't use `uv`, use the [pipx] package manager.
```shell
{apt,brew,pip,zypper} install pipx
```
```shell
pipx install rapporto
```


[pipx]: https://pipx.pypa.io/
[PyPI]: https://en.wikipedia.org/wiki/Pypi
[tool]: https://docs.astral.sh/uv/guides/tools/
[uv]: https://docs.astral.sh/uv/
