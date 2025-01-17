import pytest
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
async def test_invalid_instruction(test_repo):
    response = await process_instruction({"type": "invalid"}, test_repo)
    assert response["error"] == "Unknown instruction type: invalid"
