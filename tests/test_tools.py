from pathlib import Path

import pytest
from mcp_server_code_assist.tools.file_tools import FileTools


@pytest.fixture
def test_dir(tmp_path):
    dir_path = tmp_path / "test_files"
    dir_path.mkdir(exist_ok=True)
    return dir_path


@pytest.fixture
def file_tools(test_dir):
    return FileTools(allowed_paths=[str(test_dir)])


@pytest.mark.asyncio
async def test_create_file(file_tools, test_dir):
    file_path = test_dir / "test.txt"
    content = "test content"

    result = await file_tools.create_file(str(file_path), content)
    assert "Created file" in result
    assert file_path.exists()
    assert file_path.read_text() == content


@pytest.mark.asyncio
async def test_validate_path(file_tools, test_dir):
    file_path = test_dir / "test.txt"
    file_path.touch()

    # Valid path
    validated = await file_tools.validate_path(str(file_path))
    assert validated == file_path.resolve()

    # Invalid path
    with pytest.raises(ValueError):
        await file_tools.validate_path("/invalid/path")


@pytest.mark.asyncio
async def test_read_write_file(file_tools, test_dir):
    file_path = test_dir / "test.txt"
    content = "test content"

    await file_tools.write_file(str(file_path), content)
    assert file_path.exists()
    assert file_path.read_text() == content

    read_content = await file_tools.read_file(str(file_path))
    assert read_content == content


@pytest.mark.asyncio
async def test_read_multiple_files(file_tools, test_dir):
    files = {"file1.txt": "content1", "file2.txt": "content2"}

    for name, content in files.items():
        await file_tools.write_file(str(test_dir / name), content)

    paths = [str(test_dir / name) for name in files.keys()]
    results = await file_tools.read_multiple_files(paths)

    for path, content in results.items():
        assert content == files[Path(path).name]


@pytest.mark.asyncio
async def test_modify_file(file_tools, test_dir):
    file_path = test_dir / "test.txt"
    original = "Hello world\nThis is a test"
    await file_tools.write_file(str(file_path), original)

    replacements = {"Hello": "Hi", "test": "example"}

    diff = await file_tools.modify_file(str(file_path), replacements)
    content = await file_tools.read_file(str(file_path))

    assert "Hi world" in content
    assert "example" in content
    assert "-Hello world" in diff
    assert "+Hi world" in diff


@pytest.mark.asyncio
async def test_rewrite_file(file_tools, test_dir):
    file_path = test_dir / "test.txt"
    original = "original content"
    new_content = "new content"

    await file_tools.write_file(str(file_path), original)
    diff = await file_tools.rewrite_file(str(file_path), new_content)
    content = await file_tools.read_file(str(file_path))

    assert content == new_content
    assert "-original content" in diff
    assert "+new content" in diff
