from enum import Enum
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from mcp_server_code_assist.tools.git_functions import git_diff, git_log, git_show, git_status
from mcp_server_code_assist.tools.models import FileCreate, FileDelete, FileModify, FileRead, FileRewrite, GitDiff, GitLog, GitShow, GitStatus, ListDirectory
from mcp_server_code_assist.tools.tools_manager import get_dir_tools, get_file_tools


class CodeAssistTools(str, Enum):
    # Directory operations
    LIST_DIRECTORY = "list_directory"
    CREATE_DIRECTORY = "create_directory"

    # File operations
    CREATE_FILE = "create_file"
    DELETE_FILE = "delete_file"
    MODIFY_FILE = "modify_file"
    REWRITE_FILE = "rewrite_file"
    READ_FILE = "read_file"
    FILE_TREE = "file_tree"

    # Git operations
    GIT_STATUS = "git_status"
    GIT_DIFF = "git_diff"
    GIT_LOG = "git_log"
    GIT_SHOW = "git_show"
    GIT_COMMIT = "git_commit"
    GIT_ADD = "git_add"
    GIT_RESET = "git_reset"
    GIT_CREATE_BRANCH = "git_create_branch"
    GIT_CHECKOUT = "git_checkout"


async def process_instruction(instruction: dict[str, Any], repo_path: Path) -> dict[str, Any]:
    file_tools = get_file_tools([str(repo_path)])
    dir_tools = get_dir_tools([str(repo_path)])
    try:
        match instruction["type"]:
            case "read_file":
                return {"content": await file_tools.read_file(instruction["path"])}
            case "read_multiple":
                return {"contents": await file_tools.read_multiple_files(instruction["paths"])}
            case "create_file":
                return {"message": await file_tools.create_file(instruction["path"], instruction["content"])}
            case "modify_file":
                return {"diff": await file_tools.modify_file(instruction["path"], instruction["replacements"])}
            case "rewrite_file":
                return {"diff": await file_tools.rewrite_file(instruction["path"], instruction["content"])}
            case "delete_file":
                return {"message": await file_tools.delete_file(instruction["path"])}
            case "file_tree":
                tree, dirs, files = await file_tools.file_tree(instruction["path"])
                return {"tree": tree, "directories": dirs, "files": files}
            case "list_directory":
                return {"content": await dir_tools.list_directory(instruction["path"])}
            case "git_status":
                return {"status": git_status(repo_path)}
            case "git_diff":
                return {"diff": git_diff(repo_path)}
            case "git_log":
                return {"log": git_log(repo_path)}
            case "git_show":
                return {"show": git_show(repo_path, instruction["commit"])}
            case _:
                raise ValueError(f"Unknown instruction type: {instruction['type']}")
    except Exception as e:
        return {"error": str(e)}


async def serve(working_dir: Path | None) -> None:
    server = Server("mcp-code-assist")
    allowed_paths = [str(working_dir)] if working_dir else []

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            # Directory operations
            Tool(
                name=CodeAssistTools.LIST_DIRECTORY,
                description="Lists directory contents using system ls/dir command",
                inputSchema=ListDirectory.model_json_schema(),
            ),
            Tool(
                name=CodeAssistTools.CREATE_DIRECTORY,
                description="Creates a new directory",
                inputSchema=ListDirectory.model_json_schema(),
            ),
            # File operations
            Tool(
                name=CodeAssistTools.CREATE_FILE,
                description="Creates a new file with content",
                inputSchema=FileCreate.model_json_schema(),
            ),
            Tool(
                name=CodeAssistTools.DELETE_FILE,
                description="Deletes a file",
                inputSchema=FileDelete.model_json_schema(),
            ),
            Tool(
                name=CodeAssistTools.MODIFY_FILE,
                description="Modifies parts of a file using string replacements",
                inputSchema=FileModify.model_json_schema(),
            ),
            Tool(
                name=CodeAssistTools.REWRITE_FILE,
                description="Rewrites entire file content",
                inputSchema=FileRewrite.model_json_schema(),
            ),
            Tool(
                name=CodeAssistTools.READ_FILE,
                description="Reads file content",
                inputSchema=FileRead.model_json_schema(),
            ),
            Tool(
                name=CodeAssistTools.FILE_TREE,
                description="Lists directory tree structure with git tracking support",
                inputSchema=ListDirectory.model_json_schema(),
            ),
            # Git operations
            Tool(
                name=CodeAssistTools.GIT_STATUS,
                description="Shows git repository status",
                inputSchema=GitStatus.model_json_schema(),
            ),
            Tool(
                name=CodeAssistTools.GIT_DIFF,
                description="Shows git diff",
                inputSchema=GitDiff.model_json_schema(),
            ),
            Tool(
                name=CodeAssistTools.GIT_LOG,
                description="Shows git commit history",
                inputSchema=GitLog.model_json_schema(),
            ),
            Tool(
                name=CodeAssistTools.GIT_SHOW,
                description="Shows git commit details",
                inputSchema=GitShow.model_json_schema(),
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        repo_path = arguments.get("repo_path", "")
        paths = [repo_path] if repo_path else allowed_paths
        file_tools = get_file_tools(paths)
        dir_tools = get_dir_tools(paths)

        match name:
            # Directory operations
            case CodeAssistTools.LIST_DIRECTORY:
                result = await dir_tools.list_directory(arguments["path"])
                return [TextContent(result)]
            case CodeAssistTools.FILE_TREE:
                tree, dirs, files = await file_tools.file_tree(arguments["path"])
                return [TextContent(f"{tree}\n\nTotal: {dirs} directories, {files} files")]
            case CodeAssistTools.CREATE_DIRECTORY:
                result = await dir_tools.create_directory(arguments["path"])
                return [TextContent(result)]

            # File operations
            case CodeAssistTools.READ_FILE:
                result = await file_tools.read_file(arguments["path"])
                return [TextContent(result)]
            case CodeAssistTools.CREATE_FILE:
                result = await file_tools.create_file(arguments["path"], arguments["content"])
                return [TextContent(result)]
            case CodeAssistTools.MODIFY_FILE:
                result = await file_tools.modify_file(arguments["path"], arguments["replacements"])
                return [TextContent(result)]
            case CodeAssistTools.REWRITE_FILE:
                result = await file_tools.rewrite_file(arguments["path"], arguments["content"])
                return [TextContent(result)]
            case CodeAssistTools.DELETE_FILE:
                result = await file_tools.delete_file(arguments["path"])
                return [TextContent(result)]

            # Git operations
            case CodeAssistTools.GIT_STATUS:
                result = git_status(arguments["repo_path"])
                return [TextContent(result)]
            case CodeAssistTools.GIT_DIFF:
                result = git_diff(arguments["repo_path"])
                return [TextContent(result)]
            case CodeAssistTools.GIT_LOG:
                result = git_log(arguments["repo_path"])
                return [TextContent(result)]
            case CodeAssistTools.GIT_SHOW:
                result = git_show(arguments["repo_path"], arguments["commit"])
                return [TextContent(result)]
            case _:
                raise ValueError(f"Unknown tool: {name}")

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)
