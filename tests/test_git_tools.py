import pytest
from git import Repo
from mcp_server_code_assist.tools.git_tools import GitTools


@pytest.fixture
def repo_path(tmp_path):
    repo = tmp_path / "test_repo"
    repo.mkdir()
    Repo.init(repo)
    return repo


@pytest.fixture
def git_tools(repo_path):
    return GitTools([str(repo_path)])


class TestGitTools:
    def test_init_invalid_path(self, tmp_path):
        with pytest.raises(ValueError):
            GitTools([str(tmp_path / "nonexistent")])

    @pytest.mark.asyncio
    async def test_status(self, git_tools, repo_path):
        (repo_path / "test.txt").write_text("test")
        status = await git_tools.status(str(repo_path))
        assert "Untracked files:" in status
        assert "test.txt" in status

    @pytest.mark.asyncio
    async def test_diff(self, git_tools, repo_path):
        repo = Repo(repo_path)
        file_path = repo_path / "test.txt"
        file_path.write_text("test")
        repo.index.add(["test.txt"])
        repo.index.commit("initial")

        file_path.write_text("modified")
        diff = await git_tools.diff(str(repo_path))
        assert "-test" in diff
        assert "+modified" in diff

    @pytest.mark.asyncio
    async def test_log(self, git_tools, repo_path):
        repo = Repo(repo_path)
        (repo_path / "test.txt").write_text("test")
        repo.index.add(["test.txt"])
        repo.index.commit("test commit")

        log = await git_tools.log(str(repo_path), 1)
        assert "test commit" in log

    @pytest.mark.asyncio
    async def test_show(self, git_tools, repo_path):
        repo = Repo(repo_path)

        # Create a test file and commit it
        (repo_path / "test.txt").write_text("initial content")
        repo.index.add(["test.txt"])
        _ = repo.index.commit("initial commit")

        # Modify the file and create another commit
        (repo_path / "test.txt").write_text("modified content")
        repo.index.add(["test.txt"])
        modified_commit = repo.index.commit("modified commit")

        # Test showing specific commit with diff
        show_output = await git_tools.show(str(repo_path), modified_commit.hexsha)
        assert "modified commit" in show_output
        assert "modified content" in show_output
        assert "-initial content" in show_output
        assert "+modified content" in show_output

        # Test showing commit with format
        oneline_output = await git_tools.show(str(repo_path), modified_commit.hexsha, format_str="oneline")
        assert modified_commit.hexsha[:7] in oneline_output
        assert "modified commit" in oneline_output

        # Test showing HEAD (latest commit)
        head_output = await git_tools.show(str(repo_path))
        assert "modified commit" in head_output
