import git
import gitwrap
from gitwrap.models import ResponseMessage
import unittest
from unittest.mock import patch, MagicMock
import yaml

class TestGitWrap(unittest.TestCase):
    def init_repo(self, staged=False, unstaged=False, untracked=False):
        repo = MagicMock(active_branch=MagicMock())
        repo.active_branch.name = "main"
        if staged:
            repo.index.diff.return_value = [MagicMock(a_path="staged.txt")]
        if unstaged:
            repo.index.diff.side_effect = [
                [MagicMock(a_path="staged.txt")],   # staged
                [MagicMock(a_path="unstaged.txt")]  # unstaged
            ]
        if untracked:
            repo.untracked_files = ["untracked.txt"]
        else:
            repo.untracked_files = []
        return repo

    @patch("gitwrap.gitwrap.get_repo", return_value=None)
    @patch("gitwrap.gitwrap.typer.echo")
    def test_clean_no_repo(self, mock_echo, mock_get_repo):
        result = gitwrap.clean()
        mock_echo.assert_called_with(ResponseMessage.NO_REPO.value)
        self.assertEqual(result.status, gitwrap.gitwrap.GitWrapStatus.FAILURE)
        self.assertEqual(ResponseMessage.NO_REPO.value, result.status_message)
    
    @patch("gitwrap.gitwrap.get_untracked_files", return_value=[])
    @patch("gitwrap.gitwrap.get_repo")
    @patch("gitwrap.gitwrap.typer.echo")
    def test_clean_no_untracked_files(self, mock_echo, mock_get_repo, mock_get_untracked_files):
        mock_get_repo.return_value = self.init_repo()

        result = gitwrap.clean()
        mock_echo.assert_called_with(ResponseMessage.NO_UNTRACKED_FILES.value)
        self.assertEqual(result.status, gitwrap.gitwrap.GitWrapStatus.NO_ACTION)
        self.assertEqual(ResponseMessage.NO_UNTRACKED_FILES.value, result.status_message)
    
    @patch("gitwrap.gitwrap.get_untracked_files", return_value=["untracked.txt"])
    @patch("gitwrap.gitwrap.get_repo")
    @patch("gitwrap.gitwrap.typer.echo")
    def test_clean_dry_run(self, mock_echo, mock_get_repo, mock_get_untracked_files):
        mock_get_repo.return_value = self.init_repo(untracked=True)
        expected_yaml = gitwrap.gitwrap.yaml_dump({
            "dry_run": True,
            "action": "clean",
            "files": ["untracked.txt"]
        })
        expected_response = gitwrap.gitwrap.GitWrapResponse(
            status = gitwrap.gitwrap.GitWrapStatus.NO_ACTION,
            status_message = "",
            dry_run = True,
            action = "clean",
            yaml_output = expected_yaml
        )

        result = gitwrap.clean(dry_run=True)
        mock_echo.assert_called_with(expected_yaml)
        self.assertEqual(expected_response, result)
    
    @patch("gitwrap.gitwrap.get_untracked_files", return_value=["untracked.txt"])
    @patch("gitwrap.gitwrap.get_repo")
    @patch("gitwrap.gitwrap.typer.confirm", return_value=True)
    @patch("gitwrap.gitwrap.typer.echo")
    def test_clean_with_untracked_files_confirm_yes(self, mock_echo, mock_confirm, mock_get_repo, mock_get_untracked_files):
        mock_get_repo.return_value = self.init_repo(untracked=True)
        expected_yaml = gitwrap.gitwrap.yaml_dump({
            "dry_run": False,
            "action": "clean",
            "files": ["untracked.txt"]
        })
        expected_response = gitwrap.gitwrap.GitWrapResponse(
            status = gitwrap.gitwrap.GitWrapStatus.SUCCESS,
            status_message = ResponseMessage.SUCCESS.value,
            dry_run = False,
            action = "clean",
            yaml_output = expected_yaml
        )

        result = gitwrap.clean()
        mock_echo.assert_called_with(expected_yaml)
        self.assertEqual(expected_response, result)
    
    @patch("gitwrap.gitwrap.get_untracked_files", return_value=["untracked.txt"])
    @patch("gitwrap.gitwrap.get_repo")
    @patch("gitwrap.gitwrap.typer.confirm", return_value=False)
    @patch("gitwrap.gitwrap.typer.echo")
    def test_clean_with_untracked_files_confirm_no(self, mock_echo, mock_confirm, mock_get_repo, mock_get_untracked_files):
        mock_get_repo.return_value = self.init_repo(untracked=True)
        expected_response = gitwrap.gitwrap.GitWrapResponse(
            status = gitwrap.gitwrap.GitWrapStatus.NO_ACTION,
            status_message = ResponseMessage.OPERATION_CANCELLED.value,
            dry_run = False,
            action = "clean",
            yaml_output = ""
        )

        result = gitwrap.clean()
        self.assertEqual(expected_response, result)
    
    @patch("gitwrap.gitwrap.get_untracked_files", return_value=["untracked.txt"])
    @patch("gitwrap.gitwrap.get_repo")
    @patch("gitwrap.gitwrap.typer.echo")
    def test_clean_with_untracked_files_yes_flag(self, mock_echo, mock_get_repo, mock_get_untracked_files):
        mock_get_repo.return_value = self.init_repo(untracked=True)
        expected_yaml = gitwrap.gitwrap.yaml_dump({
            "dry_run": False,
            "action": "clean",
            "files": ["untracked.txt"]
        })
        expected_response = gitwrap.gitwrap.GitWrapResponse(
            status = gitwrap.gitwrap.GitWrapStatus.SUCCESS,
            status_message = ResponseMessage.SUCCESS.value,
            dry_run = False,
            action = "clean",
            yaml_output = expected_yaml
        )

        result = gitwrap.clean(yes = True)
        mock_echo.assert_called_with(expected_yaml)
        self.assertEqual(expected_response, result)
    
    @patch("gitwrap.gitwrap.git_clean", return_value=MagicMock(success = False, message = f"Failed to clean untracked files: ."))
    @patch("gitwrap.gitwrap.get_untracked_files", return_value=["untracked.txt"])
    @patch("gitwrap.gitwrap.get_repo")
    @patch("gitwrap.gitwrap.typer.echo")
    def test_clean_failure(self, mock_echo, mock_get_repo, mock_get_untracked_files, mock_git_clean):
        mock_get_repo.return_value = self.init_repo(untracked=True)
        expected_response = gitwrap.gitwrap.GitWrapResponse(
            status = gitwrap.gitwrap.GitWrapStatus.FAILURE,
            status_message = "Failed to clean untracked files: .",
            dry_run = False,
            action = "clean",
            yaml_output = ""
        )

        result = gitwrap.clean(yes=True)
        mock_echo.assert_called_with("Failed to clean untracked files: .")
        self.assertEqual(expected_response, result)

    @patch("gitwrap.gitwrap.get_repo", return_value=None)
    @patch("gitwrap.gitwrap.typer.echo")
    def test_status_no_repo(self, mock_echo, mock_get_repo):
        result = gitwrap.status()
        mock_echo.assert_called_with(ResponseMessage.NO_REPO.value)
        self.assertEqual(result.status, gitwrap.gitwrap.GitWrapStatus.FAILURE)
        self.assertIn(ResponseMessage.NO_REPO.value, result.status_message)
    
    @patch("gitwrap.gitwrap.git_status", return_value=MagicMock(success=True, message=ResponseMessage.SUCCESS.value, staged_files=[], unstaged_files=[], untracked_files=[]))
    @patch("gitwrap.gitwrap.get_repo")
    @patch("gitwrap.gitwrap.typer.echo")
    def test_status_no_changes(self, mock_echo, mock_get_repo, mock_git_status):
        mock_get_repo.return_value = self.init_repo()
        expected_yaml = gitwrap.gitwrap.yaml_dump({
            "action": "status",
            "branch": "main"
        })
        expected_response = gitwrap.gitwrap.GitWrapResponse(
            status = gitwrap.gitwrap.GitWrapStatus.SUCCESS,
            status_message = ResponseMessage.SUCCESS.value,
            dry_run = False,
            action = "status",
            yaml_output = expected_yaml
        )

        result = gitwrap.status()
        mock_echo.assert_called_with(expected_yaml)
        self.assertEqual(expected_response, result)
    
    @patch("gitwrap.gitwrap.git_status", return_value=MagicMock(success=True, message=ResponseMessage.SUCCESS.value, staged_files=["staged.txt"], unstaged_files=["unstaged.txt"], untracked_files=["untracked.txt"]))
    @patch("gitwrap.gitwrap.get_repo")
    @patch("gitwrap.gitwrap.typer.echo")
    def test_status_with_all_files(self, mock_echo, mock_get_repo, mock_git_status):
        mock_get_repo.return_value = self.init_repo(staged=True, unstaged=True, untracked=True)
        expected_yaml = gitwrap.gitwrap.yaml_dump({
            "action": "status",
            "branch": "main",
            "staged_files": ["staged.txt"],
            "unstaged_files": ["unstaged.txt"],
            "untracked_files": ["untracked.txt"]
        })
        expected_response = gitwrap.gitwrap.GitWrapResponse(
            status = gitwrap.gitwrap.GitWrapStatus.SUCCESS,
            status_message = ResponseMessage.SUCCESS.value,
            dry_run = False,
            action = "status",
            yaml_output = expected_yaml
        )

        result = gitwrap.status()
        mock_echo.assert_called_with(expected_yaml)
        self.assertEqual(expected_response, result)

    @patch("gitwrap.gitwrap.git_status", return_value=MagicMock(success=False, message="Failed to get status."))
    @patch("gitwrap.gitwrap.get_repo")
    @patch("gitwrap.gitwrap.typer.echo")
    def test_status_failure(self, mock_echo, mock_get_repo, mock_git_status):
        mock_get_repo.return_value = self.init_repo()
        expected_response = gitwrap.gitwrap.GitWrapResponse(
            status = gitwrap.gitwrap.GitWrapStatus.FAILURE,
            status_message = "Failed to get status.",
            dry_run = False,
            action = "status",
            yaml_output = ""
        )

        result = gitwrap.status()
        mock_echo.assert_called_with("Failed to get status.")
        self.assertEqual(expected_response, result)

if __name__ == "__main__":
    unittest.main()