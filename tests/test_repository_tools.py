import pytest
from pathlib import Path
from git import Repo
from mcp_server_code_assist.tools.repository_tools import RepositoryTools

@pytest.fixture
def repo_path(tmp_path):
    repo = tmp_path / "test_repo"
    repo.mkdir()
    Repo.init(repo)
    return repo

@pytest.fixture
def repo_tools(repo_path):
    return RepositoryTools(str(repo_path))

class TestRepositoryTools:
    def test_init_invalid_path(self, tmp_path):
        with pytest.raises(ValueError):
            RepositoryTools(str(tmp_path / "nonexistent"))

    def test_status(self, repo_tools, repo_path):
        (repo_path / "test.txt").write_text("test")
        status = repo_tools.status()
        assert "Untracked files:" in status
        assert "test.txt" in status

    def test_add_commit(self, repo_tools, repo_path):
        file_path = repo_path / "test.txt"
        file_path.write_text("test")
        
        repo_tools.add([str(file_path)])
        assert "Changes to be committed:" in repo_tools.status()
        
        repo_tools.commit("test commit")
        assert "nothing to commit" in repo_tools.status()

    def test_diff(self, repo_tools, repo_path):
        file_path = repo_path / "test.txt"
        file_path.write_text("test")
        
        repo_tools.add([str(file_path)])
        repo_tools.commit("initial")
        
        file_path.write_text("modified")
        diff = repo_tools.diff_unstaged()
        assert "-test" in diff
        assert "+modified" in diff

    def test_branch_operations(self, repo_tools, repo_path):
        (repo_path / "test.txt").write_text("test")
        repo_tools.add(["test.txt"])
        repo_tools.commit("initial")
        
        repo_tools.create_branch("dev")
        repo_tools.checkout("dev")
        assert "dev" in repo_tools.status()

    def test_log_show(self, repo_tools, repo_path):
        (repo_path / "test.txt").write_text("test")
        repo_tools.add(["test.txt"])
        repo_tools.commit("test commit")
        
        log = repo_tools.log(1)
        assert "test commit" in log
        
        show = repo_tools.show("HEAD")
        assert "test commit" in show