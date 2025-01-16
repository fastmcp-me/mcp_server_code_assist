import os
import pytest
from pathlib import Path
from mcp_server_code_assist.tools.file_tools import FileTools

TEST_DIR = Path(__file__).parent / "test_data"

@pytest.fixture(autouse=True)
def setup_test_dir():
    TEST_DIR.mkdir(exist_ok=True)
    FileTools.init_allowed_paths([str(TEST_DIR)])
    yield
    for item in TEST_DIR.glob("*"):
        if item.is_file():
            item.unlink()
        elif item.is_dir():
            import shutil
            shutil.rmtree(item)
    TEST_DIR.rmdir()

@pytest.mark.asyncio
async def test_validate_path():
    valid_path = TEST_DIR / "test.txt"
    validated = await FileTools.validate_path(str(valid_path))
    assert os.path.normpath(validated) == os.path.normpath(str(valid_path))

    with pytest.raises(ValueError):
        await FileTools.validate_path("/invalid/path/outside")

@pytest.mark.asyncio
async def test_read_write_file():
    test_file = TEST_DIR / "test.txt"
    content = "test content"
    await FileTools.write_file(str(test_file), content)
    assert await FileTools.read_file(str(test_file)) == content

@pytest.mark.asyncio
async def test_read_multiple_files():
    files = {
        "file1.txt": "content1",
        "file2.txt": "content2"
    }
    for name, content in files.items():
        await FileTools.write_file(str(TEST_DIR / name), content)
    
    paths = [str(TEST_DIR / name) for name in files.keys()]
    results = await FileTools.read_multiple_files(paths)
    
    for path, content in results.items():
        assert content == files[os.path.basename(path)]

@pytest.mark.asyncio
async def test_list_directory():
    # Create test structure
    (TEST_DIR / "dir1").mkdir()
    (TEST_DIR / "dir1" / "file1.txt").write_text("content1")
    (TEST_DIR / "dir1" / "file2.txt").write_text("content2")
    (TEST_DIR / "dir1" / "subdir").mkdir()
    (TEST_DIR / "dir1" / "subdir" / "file3.txt").write_text("content3")
    (TEST_DIR / ".hidden_dir").mkdir()
    (TEST_DIR / ".hidden_file").write_text("hidden")

    # Test basic listing
    result = await FileTools.list_directory(str(TEST_DIR / "dir1"), recursive=False, include_hidden=False)
    assert len(result) == 3
    assert any(item["name"] == "file1.txt" and item["type"] == "file" for item in result)
    assert any(item["name"] == "file2.txt" and item["type"] == "file" for item in result)
    assert any(item["name"] == "subdir" and item["type"] == "directory" for item in result)

    # Test recursive listing
    result = await FileTools.list_directory(str(TEST_DIR / "dir1"), recursive=True, include_hidden=False)
    assert len(result) == 3
    subdir = next(item for item in result if item["name"] == "subdir")
    assert "children" in subdir
    assert len(subdir["children"]) == 1
    assert subdir["children"][0]["name"] == "file3.txt"

    # Test hidden files
    result = await FileTools.list_directory(str(TEST_DIR), recursive=False, include_hidden=True)
    assert any(item["name"].startswith(".hidden") for item in result)

    # Test error on non-directory
    with pytest.raises(ValueError):
        await FileTools.list_directory(str(TEST_DIR / "dir1" / "file1.txt"))

@pytest.mark.asyncio
async def test_directory_tree():
    structure = {
        "file1.txt": "content1",
        "dir1": {
            "file2.txt": "content2",
            "dir2": {
                "file3.txt": "content3"
            }
        }
    }
    
    def create_structure(base_path: Path, struct: dict):
        for name, content in struct.items():
            path = base_path / name
            if isinstance(content, dict):
                path.mkdir()
                create_structure(path, content)
            else:
                path.write_text(content)
    
    create_structure(TEST_DIR, structure)
    
    tree_output, dir_count, file_count = await FileTools.directory_tree(str(TEST_DIR))
    
    assert "├── dir1" in tree_output
    assert "│   ├── dir2" in tree_output
    assert "│   │   └── file3.txt" in tree_output
    assert "│   └── file2.txt" in tree_output
    assert "└── file1.txt" in tree_output
    assert dir_count == 2
    assert file_count == 3

@pytest.mark.asyncio
async def test_gitignore():
    gitignore_content = """
# Python
__pycache__/
*.py[cod]

# Node
node_modules/

# Custom
*.log
temp/
"""
    await FileTools.write_file(str(TEST_DIR / ".gitignore"), gitignore_content)
    
    # Create test structure
    (TEST_DIR / "__pycache__").mkdir()
    await FileTools.write_file(str(TEST_DIR / "__pycache__/test.pyc"), "cached")
    
    (TEST_DIR / "node_modules").mkdir()
    await FileTools.write_file(str(TEST_DIR / "node_modules/package.json"), "{}")
    
    (TEST_DIR / "temp").mkdir()
    await FileTools.write_file(str(TEST_DIR / "temp/data.txt"), "temp data")
    
    await FileTools.write_file(str(TEST_DIR / "app.py"), "code")
    await FileTools.write_file(str(TEST_DIR / "debug.log"), "log")
    await FileTools.write_file(str(TEST_DIR / "data.txt"), "visible data")
    
    # Test tree output
    tree_output, dir_count, file_count = await FileTools.directory_tree(str(TEST_DIR))
    
    assert "__pycache__" not in tree_output
    assert "node_modules" not in tree_output
    assert "temp" not in tree_output
    assert "debug.log" not in tree_output
    assert "app.py" in tree_output
    assert "data.txt" in tree_output
    
    # Test search
    results = await FileTools.search_files(str(TEST_DIR), ".txt")
    assert len(results) == 1
    assert "data.txt" in results[0]
    assert "temp/data.txt" not in results

@pytest.mark.asyncio
async def test_search_files():
    files = ["test1.txt", "test2.txt", "other.txt"]
    for name in files:
        await FileTools.write_file(str(TEST_DIR / name), "content")
    
    results = await FileTools.search_files(str(TEST_DIR), "test")
    assert len(results) == 2
    assert all("test" in result for result in results)