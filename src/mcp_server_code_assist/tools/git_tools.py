"""Git operations and utilities."""

from pathlib import Path

import git

from mcp_server_code_assist.base_tools import BaseTools


class GitTools(BaseTools):
    """Tools for git operations."""

    def __init__(self, allowed_paths: list[str] | None = None):
        super().__init__(allowed_paths)
        # Validate that all paths are git repositories
        if allowed_paths:
            for path in allowed_paths:
                try:
                    git.Repo(path)
                except (git.exc.InvalidGitRepositoryError, git.exc.NoSuchPathError) as e:
                    raise ValueError(f"Invalid git repository path: {path}") from e

    async def status(self, repo_path: str) -> str:
        """Get git repository status."""
        repo = git.Repo(repo_path)
        return repo.git.status()

    async def diff(self, repo_path: str, target: str | None = None) -> str:
        """Show git diff."""
        repo = git.Repo(repo_path)
        return repo.git.diff(target) if target else repo.git.diff()

    async def log(self, repo_path: str, max_count: int = 10) -> str:
        """Show git commit history."""
        repo = git.Repo(repo_path)
        commits = list(repo.iter_commits(max_count=max_count))
        log = []
        for commit in commits:
            log.append(f"Commit: {commit.hexsha}\nAuthor: {commit.author}\nDate: {commit.authored_datetime}\nMessage: {commit.message}\n")
        return "\n".join(log)

    async def show(self, repo_path: str, revision: str | None = None, format_str: str | None = None) -> str:
        """Show various types of git objects.

        Args:
            repo_path: Path to git repository
            revision: Object to show (commit hash, tag, tree, etc.). Defaults to HEAD
            format_str: Optional format string for pretty-printing (e.g. 'oneline', 'short', 'medium', etc.)

        Returns:
            String output of git show command
        """
        repo = git.Repo(repo_path)
        args = []
        if format_str:
            args.extend([f"--format={format_str}"])
        if revision:
            args.append(revision)
        return repo.git.show(*args)

    async def is_valid_operation(self, path: Path) -> bool:
        """Validate if operation can be performed on path.

        Args:
            path: Path to validate

        Returns:
            True if path exists and is a git repository
        """
        try:
            git.Repo(path)
            return True
        except git.exc.InvalidGitRepositoryError:
            return False
