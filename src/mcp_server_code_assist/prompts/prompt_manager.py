"""Prompt manager for maintaining singleton instances of prompts."""

from mcp.types import GetPromptResult, Prompt, PromptMessage, TextContent

from mcp_server_code_assist.prompts.git_prompt import git_prompts, handle_git_prompt

PROMPTS = {
    **git_prompts,
}


def get_prompts() -> list[Prompt]:
    """Get available prompts."""
    return list(PROMPTS.values())


async def handle_prompt(name: str, arguments: dict[str, str] | None = None) -> GetPromptResult:
    """Handle prompt request.

    Args:
        name: Prompt name
        arguments: Optional arguments

    Returns:
        Prompt result

    Raises:
        ValueError: If prompt not found
    """
    if name not in PROMPTS:
        raise ValueError(f"Prompt not found: {name}")

    if name.startswith("git-"):
        return await handle_git_prompt(name, arguments)

    return GetPromptResult(messages=[PromptMessage(role="user", content=TextContent(text=f"Unhandled prompt: {name}"))])
