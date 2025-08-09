#!/usr/bin/env python3
import git
import typer
from .models import GitWrapResponse, GitWrapStatus
from .git_utils import get_repo, get_untracked_files, git_clean, git_status
from .yaml_utils import yaml_dump

app = typer.Typer()

@app.command()
def clean(dry_run: bool = False, yes: bool = False):
    """Clean up the repository by removing untracked files."""
    response = GitWrapResponse(status=GitWrapStatus.NO_ACTION, status_message= "", dry_run=dry_run, action="clean", yaml_output="")

    repo = get_repo()
    if not repo:
        response.status_message = "No git repository found."
        response.status = GitWrapStatus.FAILURE
        typer.echo(response.status_message)
        return response

    untracked_files = get_untracked_files(repo)
    if not untracked_files:
        response.status_message = "No untracked files found."
        typer.echo(response.status_message)
        return response

    if not dry_run:
        if not yes and not typer.confirm(f"This will delete {len(untracked_files)} untracked files. Continue? [y/N]:"):
            response.status_message = "Operation cancelled by user."
            return response

        clean_result = git_clean(repo)
        response.status_message = clean_result.message
        if not clean_result.success:
            typer.echo(response.status_message)
            response.status = GitWrapStatus.FAILURE
            return response
        response.status = GitWrapStatus.SUCCESS
    
    yaml_output = {
        "dry_run": dry_run,
        "action": "clean",
        "files": untracked_files
    }

    response.yaml_output = yaml_dump(yaml_output)
    typer.echo(response.yaml_output)
    return response

@app.command()
def status(dry_run: bool = False):
    """Show the status of the repository in YAML format."""
    response = GitWrapResponse(status=GitWrapStatus.NO_ACTION, status_message="", dry_run=dry_run, action="status", yaml_output="")

    repo = get_repo()
    if not repo:
        response.status_message = "No git repository found."
        response.status = GitWrapStatus.FAILURE
        typer.echo(response.status_message)
        return response

    status_result = git_status(repo)
    if not status_result.success:
        response.status_message = result.message
        response.status = GitWrapStatus.FAILURE
        typer.echo(response.status_message)
        return response

    yaml_output = {
        "action": "status",
        "branch": repo.active_branch.name
    }
    if status_result.staged_files:
        yaml_output["staged_files"] = status_result.staged_files
    if status_result.unstaged_files:
        yaml_output["unstaged_files"] = status_result.unstaged_files
    if status_result.untracked_files:
        yaml_output["untracked_files"] = status_result.untracked_files
    
    response.status = GitWrapStatus.SUCCESS
    response.yaml_output = yaml_dump(yaml_output)
    response.status_message = "Status operation completed."
    typer.echo(response.yaml_output)
    return response

if __name__ == "__main__":
    app()