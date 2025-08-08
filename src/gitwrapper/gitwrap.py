import git
import os
import typer
from typing_extensions import Annotated

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
        
    typer.echo(f"dry_run: {dry_run}\naction: clean\nfiles:")
    for file in untracked_files:
        typer.echo(f"  - {file}")

    return

@app.command()
def status(dry_run: bool = False):
    repo = get_repo()
    if not repo:
        return

    typer.echo(f"action: status\nbranch: {repo.active_branch.name}\n")

    unstaged_files = repo.index.diff(repo.head.commit)
    staged_files = [diff.a_path for diff in unstaged_files]
    untracked_files = repo.untracked_files
    
    typer.echo("staged_files:")
    for staged in staged_files:
        typer.echo(f"  - {staged}")
    
    typer.echo("unstaged_files:")
    for unstaged in unstaged_files:
        typer.echo(f"  - {unstaged.a_path}")
    
    typer.echo("untracked_files:")
    for untracked in untracked_files:
        typer.echo(f"  - {untracked}")

if __name__ == "__main__":
    app()