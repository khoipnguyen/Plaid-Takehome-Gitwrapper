from dataclasses import dataclass
import git
from .models import GitCleanResult, GitStatusResult
import typer

def get_repo():
    """ Attempt to get the git repository recursively up from the current directory. """
    try:
        return git.Repo(search_parent_directories=True)
    except git.exc.InvalidGitRepositoryError:
        return None
    
def get_untracked_files(repo: git.Repo):
    """Get a list of untracked files in the repository."""
    return repo.untracked_files

def git_clean(repo: git.Repo):
    try:
        repo.git.clean(f = True, d = True)
        return GitCleanResult(success = True, message = "Clean operation completed successfully.")
    except Exception as e:
        return GitCleanResult(success = False, message = f"Failed to clean untracked files: {e}.")

def git_status(repo: git.Repo):
    """Get the status of the repository."""
    result = GitStatusResult(success = False, message = "", staged_files = [], unstaged_files = [], untracked_files = [])
    
    try:
        status = repo.git.status('--porcelain=v1', '--untracked-files=all').splitlines()
    except Exception as e:
        result.message = f"Failed to retrieve status: {e}."
        return result

    for line in status:
        status_code = line[:2]
        filepath = line[3:]

        if status_code[0] == 'M':
            result.staged_files.append(filepath)
        if status_code[1] == 'M':
            result.unstaged_files.append(filepath)
        if status_code == '??':
            result.untracked_files.append(filepath)

    result.success = True
    result.message = "Status operation completed successfully."
    return result
