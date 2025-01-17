import os
from pathlib import Path

import pytest
from mcp_server_code_assist.tools.file_tools import FileTools

TEST_DIR = Path(__file__).parent / "test_data"


@pytest.fixture
def file_tools():
    TEST_DIR.mkdir(exist_ok=True)
    tools = FileTools(allowed_paths=[str(TEST_DIR)])
    yield tools
    for item in TEST_DIR.glob("*"):
        if item.is_file():
            item.unlink()
        elif item.is_dir():
            import shutil

            shutil.rmtree(item)
    TEST_DIR.rmdir()


@pytest.mark.asyncio
async def test_validate_path(file_tools):
    valid_path = TEST_DIR / "test.txt"
    validated = await file_tools.validate_path(str(valid_path))
    assert os.path.normpath(validated) == os.path.normpath(str(valid_path))

    with pytest.raises(ValueError):
        await file_tools.validate_path("/invalid/path/outside")


@pytest.mark.asyncio
async def test_write_file(file_tools):
    test_file = TEST_DIR / "test.txt"
    content = "test content"
    await file_tools.write_file(str(test_file), content)
    assert test_file.exists()
    assert test_file.read_text() == content


@pytest.mark.asyncio
async def test_read_file(file_tools):
    test_file = TEST_DIR / "test.txt"
    content = "test content"
    test_file.write_text(content)
    assert await file_tools.read_file(str(test_file)) == content


@pytest.mark.asyncio
async def test_create_delete_file(file_tools):
    test_file = TEST_DIR / "new_file.txt"
    content = "new content"

    # Test create
    await file_tools.create_file(str(test_file), content)
    assert test_file.exists()
    assert test_file.read_text() == content

    # Test delete
    result = await file_tools.delete_file(str(test_file))
    assert "Moved file to trash" in result
    assert not test_file.exists()

    # Verify file is in trash
    trash_dir = TEST_DIR / ".mcp_server_code_assist_trash"
    assert trash_dir.exists()
    trash_files = list(trash_dir.glob("new_file.txt_*"))
    assert len(trash_files) == 1
    assert trash_files[0].read_text() == content


@pytest.mark.asyncio
async def test_modify_file(file_tools):
    test_file = TEST_DIR / "modify.txt"
    content = "Hello world!"
    await file_tools.write_file(str(test_file), content)

    replacements = {"world": "Python"}
    diff = await file_tools.modify_file(str(test_file), replacements)

    assert "Hello Python!" == await file_tools.read_file(str(test_file))
    assert "-Hello world!" in diff
    assert "+Hello Python!" in diff


@pytest.mark.asyncio
async def test_rewrite_file(file_tools):
    test_file = TEST_DIR / "rewrite.txt"
    original = "Original content"
    new_content = "New content"

    await file_tools.write_file(str(test_file), original)
    diff = await file_tools.rewrite_file(str(test_file), new_content)

    assert new_content == await file_tools.read_file(str(test_file))
    assert "-Original content" in diff
    assert "+New content" in diff


@pytest.mark.asyncio
async def test_file_tree(file_tools):
    # Create test structure
    (TEST_DIR / "dir1").mkdir()
    await file_tools.write_file(str(TEST_DIR / "dir1/file1.txt"), "content1")
    await file_tools.write_file(str(TEST_DIR / "dir1/file2.txt"), "content2")
    (TEST_DIR / "dir1/subdir").mkdir()
    await file_tools.write_file(str(TEST_DIR / "dir1/subdir/file3.txt"), "content3")

    tree = await file_tools.file_tree(str(TEST_DIR))

    assert "dir1" in tree
    assert "file1.txt" in tree
    assert "file2.txt" in tree
    assert "subdir" in tree
    assert "file3.txt" in tree
