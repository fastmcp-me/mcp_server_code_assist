"""Directory operations and utilities."""

import asyncio
import os
import sys
from pathlib import Path

from mcp_server_code_assist.base_tools import BaseTools


class DirTools(BaseTools):
    """Tools for directory operations."""

    def is_valid_operation(self, path: Path) -> bool:
        """Validate if operation can be performed on path.

        Args:
            path: Path to validate

        Returns:
            True if path exists and is a directory
        """
        return path.exists() and path.is_dir()

    async def validate_path(self, path: str) -> Path:
        """Validate and resolve path.

        Args:
            path: Path to validate

        Returns:
            Resolved Path object

        Raises:
            ValueError: If path is outside allowed directories
        """
        abs_path = os.path.abspath(path)
        if not any(abs_path.startswith(p) for p in self.allowed_paths):
            raise ValueError(f"Path {path} is outside allowed directories")
        return Path(abs_path)

    async def create_directory(self, path: str) -> str:
        """Create a new directory.

        Args:
            path: Directory path to create

        Returns:
            Success message
        """
        path = await self.validate_path(path)
        try:
            path.mkdir(parents=True, exist_ok=True)
            return f"Created directory: {path}"
        except Exception as e:
            self.handle_error(e, {"operation": "create_directory", "path": str(path)})

    async def list_directory(self, path: str) -> str:
        """List contents of a directory using system ls/dir command.

        Args:
            path: Directory path to list

        Returns:
            Raw command output as string
        """
        path = await self.validate_path(path)
        if not path.is_dir():
            raise ValueError(f"Path {path} is not a directory")

        if sys.platform == "win32":
            cmd = ["dir", path]
        else:
            cmd = ["ls", "-la", path]

        proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, _ = await proc.communicate()
        return stdout.decode()
