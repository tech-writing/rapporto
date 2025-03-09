(sandbox)=
# Sandbox

## About

How to install Rapporto for hacking on it.

## Walkthrough

Acquire sources.
```shell
git clone https://github.com/tech-writing/rapporto
cd rapporto
```

Create Python virtualenv.
```shell
uv venv --python 3.12 --seed .venv
source .venv/bin/activate
```

Install project in development mode.
```shell
uv pip install --editable='.[develop,test]'
```

Invoke software tests.
```shell
poe check
```

A few tests are inactive by default, as they need a non-vanilla software
environment. In order to invoke them, use this command.
```shell
pytest -m nondefault
```
