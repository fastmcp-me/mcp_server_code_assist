from pathlib import Path

import pytest
from mcp_server_code_assist.base_tools import BaseTools


class ConcreteTools(BaseTools):
    def is_valid_operation(self, path: Path) -> bool:
        return path.exists()


def test_path_validation(tmp_path):
    tools = ConcreteTools(allowed_paths=[str(tmp_path)])
    test_file = tmp_path / "test.txt"
    test_file.touch()

    # Valid path
    assert tools.validate_path(test_file) == test_file.resolve()

    # Invalid path
    with pytest.raises(ValueError, match="not in allowed paths"):
        tools.validate_path("/invalid/path")


def test_error_handling():
    tools = ConcreteTools()
    error = ValueError("test error")
    context = {"operation": "test", "path": "/test/path"}

    with pytest.raises(ValueError) as exc:
        tools.handle_error(error, context)
    assert "ValueError in ConcreteTools" in str(exc.value)
    assert "Context: operation=test, path=/test/path" in str(exc.value)


def test_is_valid_operation(tmp_path):
    tools = ConcreteTools()
    test_file = tmp_path / "test.txt"
    test_file.touch()

    assert tools.is_valid_operation(test_file) is True
    assert tools.is_valid_operation(tmp_path / "nonexistent.txt") is False
