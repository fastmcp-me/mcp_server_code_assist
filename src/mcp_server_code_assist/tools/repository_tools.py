from pathlib import Path
from git import Repo
import aiofiles
from typing import Optional

class RepositoryTools:
    def __init__(self, repo_path: str):
        self.path = Path(repo_path).resolve()
        if not self.path.exists():
            raise ValueError(f"Invalid repository path: {repo_path}")
        self.repo = Repo(self.path)

    async def read_file(self, path: str) -> str:
        file_path = self.path / path
        async with aiofiles.open(file_path, 'r') as f:
            return await f.read()
            
    async def read_multiple(self, paths: list[str]) -> dict[str, str]:
        contents = {}
        for path in paths:
            contents[path] = await self.read_file(path)
        return contents
        
    async def create_file(self, path: str, content: str = '') -> None:
        file_path = self.path / path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(file_path, 'w') as f:
            await f.write(content)
            
    async def modify_file(self, path: str, replacements: dict[str, str]) -> None:
        file_path = self.path / path
        content = await self.read_file(path)
        for old, new in replacements.items():
            content = content.replace(old, new)
        await self.rewrite_file(path, content)
            
    async def rewrite_file(self, path: str, content: str) -> None:
        file_path = self.path / path
        async with aiofiles.open(file_path, 'w') as f:
            await f.write(content)
            
    async def delete_file(self, path: str) -> None:
        file_path = self.path / path
        file_path.unlink()
        
    def status(self) -> str:
        return self.repo.git.status()
        
    def add(self, files: list[str]) -> str:
        return self.repo.git.add(files)
        
    def commit(self, message: str) -> str:
        return self.repo.git.commit('-m', message)

    def diff_unstaged(self) -> str:
        return self.repo.git.diff()
    
    def diff_staged(self) -> str:
        return self.repo.git.diff('--cached')
    
    def diff(self, target: str) -> str:
        return self.repo.git.diff(target)
        
    def checkout(self, branch_name: str) -> str:
        return self.repo.git.checkout(branch_name)
        
    def create_branch(self, branch_name: str, base_branch: Optional[str] = None) -> str:
        if base_branch:
            return self.repo.git.branch(branch_name, base_branch)
        return self.repo.git.branch(branch_name)

    def log(self, max_count: int = 10) -> str:
        return self.repo.git.log(f'-n {max_count}')

    def show(self, revision: str) -> str:
        return self.repo.git.show(revision)