from typing import Union, Optional
from pydantic import BaseModel
from pathlib import Path

class FileCreate(BaseModel):
    path: Union[str, Path]
    content: str = ""

class FileDelete(BaseModel):
    path: Union[str, Path]

class FileModify(BaseModel):
    path: Union[str, Path]
    replacements: dict[str, str]

class FileRewrite(BaseModel):
    path: Union[str, Path]
    content: str

class GitBase(BaseModel):
    repo_path: str

class GitAdd(GitBase):
    files: list[str]

class GitCommit(GitBase):
    message: str

class GitDiff(GitBase):
    target: str

class GitCreateBranch(GitBase):
    branch_name: str
    base_branch: Optional[str] = None

class GitCheckout(GitBase):
    branch_name: str

class GitShow(GitBase):
    revision: str

class GitLog(GitBase):
    max_count: int = 10

class RepositoryOperation(BaseModel):
    path: str
    content: Optional[str] = None
    replacements: Optional[dict[str, str]] = None