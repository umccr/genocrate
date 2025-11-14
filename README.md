# genocrate

[![PyPI](https://img.shields.io/pypi/v/genocrate.svg)](https://pypi.org/project/genocrate/)
[![Changelog](https://img.shields.io/github/v/release/andrewpatto/genocrate?include_prereleases&label=changelog)](https://github.com/andrewpatto/genocrate/releases)
[![Tests](https://github.com/andrewpatto/genocrate/actions/workflows/test.yml/badge.svg)](https://github.com/andrewpatto/genocrate/actions/workflows/test.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/andrewpatto/genocrate/blob/master/LICENSE)

CLI suite

## Installation

Install this tool using `pip`:
```bash
pip install genocrate
```
## Usage

For help, run:
```bash
genocrate --help
```
You can also use:
```bash
python -m genocrate --help
```

## CLI Documentation

Detailed command-line documentation is available [in the CLI docs](./docs/cli.md).

## Development

To contribute to this tool, first checkout the code. Then create a new virtual environment:

```bash
uv venv
source .venv/bin/activate
```

Now install the dependencies and test dependencies:

```bash
pip install -e '.[test]'
```

To run the tests:

```bash
python -m pytest
```

To update the CLI docs:

```bash
python ./scripts/generate_cli_docs.py
```
