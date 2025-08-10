import git
from gitwrap import git_utils
import unittest
from unittest.mock import patch, MagicMock

class TestGitUtils(unittest.TestCase):
    def init_repo(self, staged = False, unstaged = False, untracked = False):
        repo = MagicMock(active_branch = MagicMock())
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

    @patch("gitwrap.git_utils.get_repo", return_value=None)
    def test_get_repo_no_repo(self, mock_get_repo):
        result = git_utils.get_repo()
        self.assertIsNone(result)
    
    @patch("git.Repo")
    def test_get_repo(self, mock_get_repo):
        mock_repo = self.init_repo()
        mock_get_repo.return_value = mock_repo

        repo = git_utils.get_repo()
        self.assertEqual(repo, mock_repo)

    def test_get_untracked_files(self):
        mock_repo = self.init_repo(untracked = True)

        untracked_files = git_utils.get_untracked_files(mock_repo)
        self.assertEqual(untracked_files, ["untracked.txt"])

    def test_git_clean_success(self):
        mock_repo = self.init_repo(untracked = True)
        mock_repo.git.clean = MagicMock(return_value = None)
        
        result = git_utils.git_clean(mock_repo)
        self.assertTrue(result.success)
        self.assertEqual(result.message, "Clean operation completed successfully.")
    
    def test_git_clean_failure(self):
        mock_repo = self.init_repo(untracked = True)
        mock_repo.git.clean = MagicMock(side_effect = Exception("Clean failed"))

        result = git_utils.git_clean(mock_repo)
        self.assertFalse(result.success)
        self.assertEqual(result.message, "Failed to clean untracked files: Clean failed.")
    
    def test_git_status_success(self):
        mock_repo = MagicMock()
        mock_repo.git.status.return_value = (
            "M  staged.txt\n"  
            " M unstaged.txt\n" 
            "?? untracked.txt\n"
        )

        result = git_utils.git_status(mock_repo)
        self.assertTrue(result.success)
        self.assertEqual(result.message, "Status operation completed successfully.")
        self.assertIn("staged.txt", result.staged_files)
        self.assertIn("unstaged.txt", result.unstaged_files)
        self.assertIn("untracked.txt", result.untracked_files)
    
    def test_git_status_no_changes(self):
        mock_repo = self.init_repo()

        result = git_utils.git_status(mock_repo)
        self.assertTrue(result.success)
        self.assertEqual(result.message, "Status operation completed successfully.")
        self.assertEqual(result.staged_files, [])
        self.assertEqual(result.unstaged_files, [])
        self.assertEqual(result.untracked_files, [])
    
    def test_git_status_failure(self):
        mock_repo = MagicMock()
        mock_repo.git.status.side_effect = Exception("Status failed")

        result = git_utils.git_status(mock_repo)
        self.assertFalse(result.success)
        self.assertIn("Failed to retrieve status: Status failed.", result.message)
        self.assertEqual(result.staged_files, [])
        self.assertEqual(result.unstaged_files, [])
        self.assertEqual(result.untracked_files, [])

if __name__ == "__main__":
    unittest.main()