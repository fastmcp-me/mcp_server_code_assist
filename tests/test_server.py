import pytest
from pathlib import Path
from git import Repo
from mcp_server_code_assist.server import process_instruction

@pytest.fixture
def test_repo(tmp_path):
    repo = tmp_path / "test_repo"
    repo.mkdir()
    Repo.init(repo)
    test_file = repo / "test.txt"
    test_file.write_text("test")
    return repo

@pytest.mark.asyncio
async def test_read_file(test_repo):
    response = await process_instruction({
        'type': 'read_file',
        'path': 'test.txt'
    }, test_repo)
    assert response['content'] == 'test'

@pytest.mark.asyncio
async def test_read_multiple(test_repo):
    other_file = test_repo / "other.txt"
    other_file.write_text("other")
    
    response = await process_instruction({
        'type': 'read_multiple',
        'paths': ['test.txt', 'other.txt']
    }, test_repo)
    assert response['contents']['test.txt'] == 'test'
    assert response['contents']['other.txt'] == 'other'

@pytest.mark.asyncio
async def test_create_file(test_repo):
    response = await process_instruction({
        'type': 'create_file',
        'path': 'new.txt',
        'content': 'new content'
    }, test_repo)
    assert response['result'] == 'Created file: ' + str(test_repo / 'new.txt')
    assert (test_repo / "new.txt").read_text() == 'new content'

@pytest.mark.asyncio
async def test_modify_file(test_repo):
    response = await process_instruction({
        'type': 'modify_file',
        'path': 'test.txt',
        'replacements': {'test': 'modified'}
    }, test_repo)
    assert response['result'].startswith('--- original')
    assert (test_repo / "test.txt").read_text() == 'modified'

@pytest.mark.asyncio
async def test_rewrite_file(test_repo):
    response = await process_instruction({
        'type': 'rewrite_file',
        'path': 'test.txt', 
        'content': 'rewritten'
    }, test_repo)
    assert response['result'].startswith('--- original')
    assert (test_repo / "test.txt").read_text() == 'rewritten'

@pytest.mark.asyncio
async def test_delete_file(test_repo):
    response = await process_instruction({
        'type': 'delete_file',
        'path': 'test.txt'
    }, test_repo)
    assert response['result'] == 'Deleted file: ' + str(test_repo / 'test.txt')
    assert not (test_repo / "test.txt").exists()

@pytest.mark.asyncio
async def test_invalid_instruction(test_repo):
    response = await process_instruction({
        'type': 'invalid'
    }, test_repo)
    assert response['error'] == 'Invalid instruction type'