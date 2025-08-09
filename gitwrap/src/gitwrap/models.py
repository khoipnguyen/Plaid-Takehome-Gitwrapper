from dataclasses import dataclass
from enum import Enum
from typing import Optional

class GitWrapStatus(Enum):
    """Enum for gitwrap status"""
    SUCCESS = "success"
    FAILURE = "failure"
    NO_ACTION = "no_action"

@dataclass
class GitWrapResponse:
    """Dataclass for gitwrap responses."""
    status: GitWrapStatus
    status_message: Optional[str] # Optional message for the status
    dry_run: bool
    action: str
    yaml_output: Optional[str]

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