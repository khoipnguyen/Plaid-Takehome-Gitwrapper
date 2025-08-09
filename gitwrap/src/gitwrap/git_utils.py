from dataclasses import dataclass
import git
import typer

@dataclass
class GitCleanResult:
    """Dataclass to hold the result of a git clean operation."""
    success: bool
    message: str

@dataclass
class GitStatusResult:
    """Dataclass to hold the result of a git status operation."""
    success: bool
    message: str
    staged_files: list
    unstaged_files: list
    untracked_files: list

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
        result.staged_files = [diff.a_path for diff in repo.index.diff(repo.head.commit)]
        result.unstaged_files = [unstaged.a_path for unstaged in repo.index.diff(None)]
        result.untracked_files = get_untracked_files(repo)
        result.success = True
        result.message = "Status operation completed successfully."
        return result
    except Exception as e:
        result.message = f"Failed to retrieve status: {e}."
        return result
