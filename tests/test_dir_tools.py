"""Tests for directory operations."""

import pytest
from mcp_server_code_assist.tools.tools_manager import get_dir_tools


@pytest.fixture
def test_dir(tmp_path):
    dir_path = tmp_path / "test_dir"
    dir_path.mkdir(exist_ok=True)
    return dir_path


@pytest.fixture
def dir_tools(test_dir):
    return get_dir_tools([str(test_dir)])


@pytest.mark.asyncio
async def test_create_directory(dir_tools, test_dir):
    new_dir = test_dir / "new_dir"
    result = await dir_tools.create_directory(str(new_dir))
    assert "Created directory" in result
    assert new_dir.exists()
    assert new_dir.is_dir()


@pytest.mark.asyncio
async def test_list_directory(dir_tools, test_dir):
    # Create test files and directories
    (test_dir / "file1.txt").write_text("test1")
    (test_dir / "file2.txt").write_text("test2")
    (test_dir / "subdir").mkdir()

    # Test raw ls output
    result = await dir_tools.list_directory(str(test_dir))
    assert isinstance(result, str)
    assert "file1.txt" in result
    assert "file2.txt" in result
    assert "subdir" in result


@pytest.mark.asyncio
async def test_validate_path(dir_tools, test_dir):
    # Test valid path
    valid_path = test_dir / "valid"
    valid_path.mkdir()
    validated = await dir_tools.validate_path(str(valid_path))
    assert validated == valid_path.resolve()

    # Test invalid path
    with pytest.raises(ValueError):
        await dir_tools.validate_path("/invalid/path")


@pytest.mark.asyncio
async def test_is_valid_operation(dir_tools, test_dir):
    # Test directory
    dir_path = test_dir / "test_dir"
    dir_path.mkdir()
    assert dir_tools.is_valid_operation(dir_path)

    # Test file (should return False)
    file_path = test_dir / "test.txt"
    file_path.write_text("test")
    assert not dir_tools.is_valid_operation(file_path)
