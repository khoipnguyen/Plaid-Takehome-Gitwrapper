#!/usr/bin/env python3

import git
import os
import typer
import yaml

# Custom class to handle YAML indentation
class IndentDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)

app = typer.Typer()

def get_repo():
    """ Attempt to get the git repository recursively up from the current directory. """
    try:
        return git.Repo(search_parent_directories=True)
    except git.exc.InvalidGitRepositoryError:
        typer.echo("Not a git repository.")
        return None

@app.command()
def clean(dry_run: bool = False, yes: bool = False):
    """Clean up the repository by removing untracked files."""

    repo = get_repo()
    if not repo:
        return

    untracked_files = repo.untracked_files
    if not untracked_files:
        typer.echo("No untracked files found.")
        return

    if not dry_run:
        if not yes and not typer.confirm(f"This will delete {len(untracked_files)} untracked files. Continue? [y/N]:"):
            return
        repo.git.clean(f=True, d=True)
    
    yaml_output = {
        "dry_run": dry_run,
        "action": "clean",
        "files": untracked_files
    }

    typer.echo(yaml.dump(yaml_output, Dumper=IndentDumper, sort_keys=False))
    return

@app.command()
def status(dry_run: bool = False):
    """Show the status of the repository in YAML format."""
    repo = get_repo()
    if not repo:
        return

    yaml_output = {
        "action": "status",
        "branch": repo.active_branch.name
    }

    staged_files = [diff.a_path for diff in repo.index.diff(repo.head.commit)]
    unstaged_files = [unstaged.a_path for unstaged in repo.index.diff(None)]
    untracked_files = repo.untracked_files
    
    if staged_files:
        yaml_output["staged_files"] = staged_files
    
    if unstaged_files:
        yaml_output["unstaged_files"] = unstaged_files
    
    if untracked_files:
        yaml_output["untracked_files"] = untracked_files
    
    typer.echo(yaml.dump(yaml_output, Dumper=IndentDumper, sort_keys=False))
    return

if __name__ == "__main__":
    app()