import pytest
from mcp_server_code_assist.tools.file_tools import FileTools


@pytest.fixture
def file_tools(tmp_path):
    return FileTools(allowed_paths=[str(tmp_path)])


@pytest.mark.asyncio
async def test_read_write_file(file_tools, tmp_path):
    test_file = tmp_path / "test.txt"
    content = "test content"

    await file_tools.write_file(str(test_file), content)
    assert test_file.exists()

    read_content = await file_tools.read_file(str(test_file))
    assert read_content == content


@pytest.mark.asyncio
async def test_read_multiple_files(file_tools, tmp_path):
    files = {"file1.txt": "content1", "file2.txt": "content2"}

    for name, content in files.items():
        await file_tools.write_file(str(tmp_path / name), content)

    result = await file_tools.read_multiple_files([str(tmp_path / name) for name in files])

    assert all(result[str(tmp_path / name)] == content for name, content in files.items())


@pytest.mark.asyncio
async def test_create_file(file_tools, tmp_path):
    test_file = tmp_path / "new.txt"
    content = "new content"

    result = await file_tools.create_file(str(test_file), content)
    assert "Created file" in result
    assert test_file.exists()
    assert test_file.read_text() == content


def test_is_valid_operation(file_tools, tmp_path):
    test_file = tmp_path / "test.txt"
    test_file.touch()

    assert file_tools.is_valid_operation(test_file) is True
    assert file_tools.is_valid_operation(tmp_path) is False  # Directory
    assert file_tools.is_valid_operation(tmp_path / "nonexistent.txt") is False
