# gitwrap

`gitwrap` is a simple git wrapper command-line tool. It leverages [Typer](https://typer.tiangolo.com/) for an easy-to-use CLI interface, [GitPython](https://gitpython.readthedocs.io/) for Git interactions, and [PyYAML](https://pyyaml.org/) for output formatting.

---

## Features

- Clean untracked files in a Git repository (with dry-run support)
- Show repository status including staged, unstaged, and untracked files
- YAML-formatted output for easy wrapping or scripting
- Interactive confirmation before destructive actions

---

## Installation

You can install `gitwrap` in editable/development mode. From the root gitwrap directory:

```bash
pip install -e .