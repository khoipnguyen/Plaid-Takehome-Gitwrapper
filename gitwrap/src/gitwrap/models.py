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