"""Git prompts for advanced git operations."""

import platform

from mcp.types import GetPromptResult, Prompt, PromptArgument, PromptMessage, TextContent

from mcp_server_code_assist.tools.git_tools import GitTools

git_prompts = {
    "git-advanced": Prompt(
        name="git-advanced",
        description="Handle advanced git operations with verification",
        arguments=[
            PromptArgument(
                name="operation",
                description="Git operation to perform",
                required=True,
            ),
            PromptArgument(
                name="repo_path",
                description="Repository path",
                required=True,
            ),
        ],
    ),
}


def handle_git_prompt(name: str, arguments: dict[str, str] | None = None) -> GetPromptResult:
    """Handle git prompts.

    Args:
        name: Name of the prompt
        arguments: Dictionary of prompt arguments

    Returns:
        GetPromptResult with messages

    Raises:
        ValueError: If prompt not found or required arguments missing
    """
    if name not in git_prompts:
        raise ValueError(f"Prompt not found: {name}")

    if not arguments:
        raise ValueError("Arguments required")

    operation = arguments.get("operation")
    repo_path = arguments.get("repo_path")

    if not operation or not repo_path:
        raise ValueError("Operation and repo_path are required")

    git_tools = GitTools([repo_path])

    system_info = f"{platform.system()} {platform.machine()}"

    before_status = git_tools.status(repo_path)
    user_prompt = (
        f"Please help with the following git operation in {repo_path}:\n{operation}\n\n"
        f"Current status:\n{before_status}\n\n"
        f"System info:\n{system_info}\n\n"
        "After you provide the commands and I execute them, I'll respond with 'done'. Then use git_tools to verify the changes."
    )

    return GetPromptResult(messages=[PromptMessage(role="user", content=TextContent(text=user_prompt))])
