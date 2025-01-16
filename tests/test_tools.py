import pytest
from pathlib import Path
from mcp_server_code_assist.tools.file_tools import FileTools

@pytest.fixture
def test_dir(tmp_path):
    dir_path = tmp_path / "test_files"
    dir_path.mkdir(exist_ok=True)
    FileTools.init_allowed_paths([str(dir_path)])
    return dir_path

@pytest.mark.asyncio
async def test_create_file(test_dir):
    file_path = test_dir / "test.txt"
    content = "test content"
    await FileTools.write_file(str(file_path), content)
    
    assert file_path.exists()
    assert file_path.read_text() == content

@pytest.mark.asyncio
async def test_validate_path(test_dir):
    file_path = test_dir / "test.txt"
    valid_path = await FileTools.validate_path(str(file_path))
    assert Path(valid_path) == file_path.absolute()
    
    with pytest.raises(ValueError):
        await FileTools.validate_path("/invalid/path")

@pytest.mark.asyncio
async def test_read_write_file(test_dir):
    file_path = test_dir / "test.txt"
    content = "test content"
    
    await FileTools.write_file(str(file_path), content)
    read_content = await FileTools.read_file(str(file_path))
    
    assert read_content == content

@pytest.mark.asyncio
async def test_read_multiple_files(test_dir):
    files = {
        "file1.txt": "content1",
        "file2.txt": "content2"
    }
    for name, content in files.items():
        await FileTools.write_file(str(test_dir / name), content)
    
    paths = [str(test_dir / name) for name in files.keys()]
    results = await FileTools.read_multiple_files(paths)
    
    for path, content in results.items():
        assert content == files[Path(path).name]

@pytest.mark.asyncio  
async def test_modify_file(test_dir):
    file_path = test_dir / "test.txt"
    original = "Hello world\nThis is a test"
    await FileTools.write_file(str(file_path), original)
    
    replacements = {
        "Hello": "Hi",
        "test": "example"
    }
    
    diff = await FileTools.modify_file(str(file_path), replacements)
    content = await FileTools.read_file(str(file_path))
    
    assert "Hi world" in content
    assert "example" in content
    assert "-Hello world" in diff
    assert "+Hi world" in diff

@pytest.mark.asyncio
async def test_rewrite_file(test_dir):
    file_path = test_dir / "test.txt"
    original = "original content"
    new_content = "new content"
    
    await FileTools.write_file(str(file_path), original)
    diff = await FileTools.rewrite_file(str(file_path), new_content)
    content = await FileTools.read_file(str(file_path))
    
    assert content == new_content
    assert "-original content" in diff
    assert "+new content" in diff