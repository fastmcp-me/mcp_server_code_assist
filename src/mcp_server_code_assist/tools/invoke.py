"""Function invocation helper."""
from typing import Dict, Any

def invoke_git(function: str, params: Dict[str, Any]) -> str:
    """Invokes a git function with given parameters."""
    # Functions will be invoked via the assistant
    return f"git_{function}({', '.join(f'{k}={v!r}' for k,v in params.items())})"