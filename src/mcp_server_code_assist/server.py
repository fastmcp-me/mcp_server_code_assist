import os
from enum import Enum
from pathlib import Path
from typing import Any

import git
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from mcp_server_code_assist.tools.tools_manager import get_file_tools
from mcp_server_code_assist.tools.git_functions import git_diff, git_diff_staged, git_diff_unstaged, git_log, git_show, git_status
from mcp_server_code_assist.tools.models import (
    FileCreate,
    FileDelete,
    FileModify,
    FileRead,
    FileRewrite,
    GitAdd,
    GitBase,
    GitCheckout,
    GitCommit,
    GitCreateBranch,
    GitDiff,
    GitLog,
    GitShow,
    ListDirectory,
)


class CodeAssistTools(str, Enum):
    LIST_DIRECTORY = "list_directory"
    FILE_CREATE = "file_create"
    FILE_DELETE = "file_delete"
    FILE_MODIFY = "file_modify"
    FILE_REWRITE = "file_rewrite"
    FILE_READ = "file_read"
    GIT_STATUS = "git_status"
    GIT_DIFF_UNSTAGED = "git_diff_unstaged"
    GIT_DIFF_STAGED = "git_diff_staged"
    GIT_DIFF = "git_diff"
    GIT_COMMIT = "git_commit"
    GIT_ADD = "git_add"
    GIT_RESET = "git_reset"
    GIT_LOG = "git_log"
    GIT_CREATE_BRANCH = "git_create_branch"
    GIT_CHECKOUT = "git_checkout"
    GIT_SHOW = "git_show"


async def process_instruction(instruction: dict[str, Any], repo_path: Path) -> dict[str, Any]:
    file_tools = get_file_tools([str(repo_path)])
    try:
        match instruction["type"]:
            case "read_file":
                path = str(repo_path / instruction["path"])
                content = await file_tools.read_file(path)
                return {"content": content}

            case "read_multiple":
                paths = [str(repo_path / p) for p in instruction["paths"]]
                contents = await file_tools.read_multiple_files(paths)
                contents_dict = {os.path.basename(k): v for k, v in contents.items()}
                return {"contents": contents_dict}

            case "create_file":
                path = str(repo_path / instruction["path"])
                result = await file_tools.create_file(path, instruction.get("content", ""))
                return {"result": result}

            case "modify_file":
                path = str(repo_path / instruction["path"])
                result = await file_tools.modify_file(path, instruction["replacements"])
                return {"result": result}

            case "rewrite_file":
                path = str(repo_path / instruction["path"])
                result = await file_tools.rewrite_file(path, instruction["content"])
                return {"result": result}

            case "delete_file":
                path = str(repo_path / instruction["path"])
                result = await file_tools.delete_file(path)
                return {"result": result}

            case _:
                return {"error": "Invalid instruction type"}

    except Exception as e:
        return {"error": str(e)}


async def serve(working_dir: Path | None) -> None:
    server = Server("mcp-code-assist")
    allowed_paths = [str(working_dir)] if working_dir else []

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name=CodeAssistTools.LIST_DIRECTORY,
                description="Lists contents of a directory",
                inputSchema=ListDirectory.schema(),
            ),
            Tool(
                name=CodeAssistTools.FILE_CREATE,
                description="Creates a new file with content",
                inputSchema=FileCreate.schema(),
            ),
            Tool(
                name=CodeAssistTools.FILE_DELETE,
                description="Deletes a file",
                inputSchema=FileDelete.schema(),
            ),
            Tool(
                name=CodeAssistTools.FILE_MODIFY,
                description="Modifies file content using search/replace",
                inputSchema=FileModify.schema(),
            ),
            Tool(
                name=CodeAssistTools.FILE_REWRITE,
                description="Rewrites entire file content",
                inputSchema=FileRewrite.schema(),
            ),
            Tool(
                name=CodeAssistTools.FILE_READ,
                description="Reads contents of a file",
                inputSchema=FileRead.schema(),
            ),
            Tool(
                name=CodeAssistTools.GIT_STATUS,
                description="Shows the working tree status",
                inputSchema=GitBase.schema(),
            ),
            Tool(
                name=CodeAssistTools.GIT_DIFF_UNSTAGED,
                description="Shows changes in the working directory that are not yet staged",
                inputSchema=GitBase.schema(),
            ),
            Tool(
                name=CodeAssistTools.GIT_DIFF_STAGED,
                description="Shows changes that are staged for commit",
                inputSchema=GitBase.schema(),
            ),
            Tool(
                name=CodeAssistTools.GIT_DIFF,
                description="Shows differences between branches or commits",
                inputSchema=GitDiff.schema(),
            ),
            Tool(
                name=CodeAssistTools.GIT_COMMIT,
                description="Records changes to the repository",
                inputSchema=GitCommit.schema(),
            ),
            Tool(
                name=CodeAssistTools.GIT_ADD,
                description="Adds file contents to the staging area",
                inputSchema=GitAdd.schema(),
            ),
            Tool(
                name=CodeAssistTools.GIT_RESET,
                description="Unstages all staged changes",
                inputSchema=GitBase.schema(),
            ),
            Tool(
                name=CodeAssistTools.GIT_LOG,
                description="Shows the commit logs",
                inputSchema=GitLog.schema(),
            ),
            Tool(
                name=CodeAssistTools.GIT_CREATE_BRANCH,
                description="Creates a new branch from an optional base branch",
                inputSchema=GitCreateBranch.schema(),
            ),
            Tool(
                name=CodeAssistTools.GIT_CHECKOUT,
                description="Switches branches",
                inputSchema=GitCheckout.schema(),
            ),
            Tool(
                name=CodeAssistTools.GIT_SHOW,
                description="Shows the contents of a commit",
                inputSchema=GitShow.schema(),
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        repo_path = arguments.get("repo_path", "")
        paths = [repo_path] if repo_path else allowed_paths
        file_tools = get_file_tools(paths)
        
        match name:
            case CodeAssistTools.LIST_DIRECTORY:
                result = await file_tools.list_directory(arguments["path"])
                return [TextContent(type="text", text=result)]

            case CodeAssistTools.FILE_CREATE:
                result = await file_tools.create_file(arguments["path"], arguments.get("content", ""))
                return [TextContent(type="text", text=result)]

            case CodeAssistTools.FILE_DELETE:
                result = await file_tools.delete_file(arguments["path"])
                return [TextContent(type="text", text=result)]

            case CodeAssistTools.FILE_MODIFY:
                result = await file_tools.modify_file(arguments["path"], arguments["replacements"])
                return [TextContent(type="text", text=result)]

            case CodeAssistTools.FILE_REWRITE:
                result = await file_tools.rewrite_file(arguments["path"], arguments["content"])
                return [TextContent(type="text", text=result)]

            case CodeAssistTools.FILE_READ:
                content = await file_tools.read_file(arguments["path"])
                return [TextContent(type="text", text=content)]

            case CodeAssistTools.GIT_STATUS:
                repo = git.Repo(arguments["repo_path"])
                status = git_status(repo)
                return [TextContent(type="text", text=f"Repository status:\n{status}")]

            case CodeAssistTools.GIT_DIFF_UNSTAGED:
                repo = git.Repo(arguments["repo_path"])
                diff = git_diff_unstaged(repo)
                return [TextContent(type="text", text=f"Unstaged changes:\n{diff}")]

            case CodeAssistTools.GIT_DIFF_STAGED:
                repo = git.Repo(arguments["repo_path"])
                diff = git_diff_staged(repo)
                return [TextContent(type="text", text=f"Staged changes:\n{diff}")]

            case CodeAssistTools.GIT_DIFF:
                repo = git.Repo(arguments["repo_path"])
                diff = git_diff(repo, arguments["target"])
                return [TextContent(type="text", text=f"Diff with {arguments['target']}:\n{diff}")]

            case CodeAssistTools.GIT_COMMIT:
                repo = git.Repo(arguments["repo_path"])
                result = git_commit(repo, arguments["message"])
                return [TextContent(type="text", text=result)]

            case CodeAssistTools.GIT_ADD:
                repo = git.Repo(arguments["repo_path"])
                result = git_add(repo, arguments["files"])
                return [TextContent(type="text", text=result)]

            case CodeAssistTools.GIT_RESET:
                repo = git.Repo(arguments["repo_path"])
                result = git_reset(repo)
                return [TextContent(type="text", text=result)]

            case CodeAssistTools.GIT_LOG:
                repo = git.Repo(arguments["repo_path"])
                log = git_log(repo, arguments.get("max_count", 10))
                return [TextContent(type="text", text="Commit history:\n" + "\n".join(log))]

            case CodeAssistTools.GIT_CREATE_BRANCH:
                repo = git.Repo(arguments["repo_path"])
                result = git_create_branch(repo, arguments["branch_name"], arguments.get("base_branch"))
                return [TextContent(type="text", text=result)]

            case CodeAssistTools.GIT_CHECKOUT:
                repo = git.Repo(arguments["repo_path"])
                result = git_checkout(repo, arguments["branch_name"])
                return [TextContent(type="text", text=result)]

            case CodeAssistTools.GIT_SHOW:
                repo = git.Repo(arguments["repo_path"])
                result = git_show(repo, arguments["revision"])
                return [TextContent(type="text", text=result)]

            case _:
                raise ValueError(f"Unknown tool: {name}")

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)
