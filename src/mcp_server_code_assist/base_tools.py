from abc import ABC, abstractmethod
from pathlib import Path


class BaseTools(ABC):
    def __init__(self, allowed_paths: list[str] | None = None):
        self.allowed_paths = allowed_paths or []

    def validate_path(self, path: str | Path) -> Path:
        path = Path(path).resolve()
        if not self.allowed_paths or any(path.is_relative_to(Path(allowed).resolve()) for allowed in self.allowed_paths):
            return path
        raise ValueError(f"Path {path} is not in allowed paths: {self.allowed_paths}")

    @abstractmethod
    def is_valid_operation(self, path: Path) -> bool:
        """Validate if operation can be performed on path"""
        pass

    def handle_error(self, error: Exception, context: dict) -> None:
        """Handle operation errors with context"""
        error_type = type(error).__name__
        error_msg = str(error)
        context_str = ", ".join(f"{k}={v}" for k, v in context.items())
        raise type(error)(f"{error_type} in {self.__class__.__name__}: {error_msg} | Context: {context_str}")
