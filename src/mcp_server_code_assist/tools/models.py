from pathlib import Path

from pydantic import BaseModel


class FileCreate(BaseModel):
    path: str | Path
    content: str = ""


class FileDelete(BaseModel):
    path: str | Path


class FileModify(BaseModel):
    path: str | Path
    replacements: dict[str, str]


class FileRead(BaseModel):
    path: str | Path


class FileRewrite(BaseModel):
    path: str | Path
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
    base_branch: str | None = None


class GitCheckout(GitBase):
    branch_name: str


class GitShow(GitBase):
    revision: str


class GitLog(GitBase):
    max_count: int = 10


class ListDirectory(BaseModel):
    path: str | Path


class RepositoryOperation(BaseModel):
    path: str
    content: str | None = None
    replacements: dict[str, str] | None = None
