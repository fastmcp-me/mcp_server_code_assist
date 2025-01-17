"""Tools manager for maintaining singleton instances of tools."""

from typing import Optional
from mcp_server_code_assist.tools.file_tools import FileTools

_file_tools: Optional[FileTools] = None

def get_file_tools(allowed_paths: list[str]) -> FileTools:
    """Get or create FileTools instance with given allowed paths.
    
    Args:
        allowed_paths: List of paths that tools can operate on
        
    Returns:
        FileTools instance with updated paths
    """
    global _file_tools
    if not _file_tools or not all(path in _file_tools.allowed_paths for path in allowed_paths):
        _file_tools = FileTools(allowed_paths=allowed_paths)
    return _file_tools
