from pathlib import Path
import os
import shutil
import difflib
import fnmatch
import json
from typing import Union, Dict, Tuple, Optional, Set
import git

class FileTools:
    _allowed_paths: list[str] = []

    @classmethod
    def init_allowed_paths(cls, paths: list[str]):
        cls._allowed_paths = [os.path.abspath(p) for p in paths]

    @classmethod
    async def validate_path(cls, path: str) -> str:
        abs_path = os.path.abspath(path)
        if not any(abs_path.startswith(p) for p in cls._allowed_paths):
            raise ValueError(f"Path {path} is outside allowed directories")
        return abs_path

    @classmethod
    async def read_file(cls, path: str) -> str:
        path = await cls.validate_path(path)
        return Path(path).read_text()

    @classmethod
    async def write_file(cls, path: str, content: str) -> None:
        path = await cls.validate_path(path)
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(content)

    @classmethod
    async def read_multiple_files(cls, paths: list[str]) -> Dict[str, str]:
        result = {}
        for path in paths:
            try:
                content = await cls.read_file(path)
                result[path] = content
            except Exception as e:
                result[path] = str(e)
        return result

    @classmethod
    async def create_file(cls, path: str, content: str = "") -> str:
        await cls.write_file(path, content)
        return f"Created file: {path}"
        
    @classmethod
    async def delete_file(cls, path: str) -> str:
        path = await cls.validate_path(path)
        path_obj = Path(path)
        if path_obj.is_file():
            path_obj.unlink()
            return f"Deleted file: {path}"
        elif path_obj.is_dir():
            shutil.rmtree(path)
            return f"Deleted directory: {path}"
        return f"Path not found: {path}"

    @classmethod
    async def modify_file(cls, path: str, replacements: Dict[str, str]) -> str:
        path = await cls.validate_path(path)
        content = await cls.read_file(path)
        original = content
        
        for old, new in replacements.items():
            content = content.replace(old, new)
            
        await cls.write_file(path, content)
        return cls.generate_diff(original, content)

    @classmethod
    async def rewrite_file(cls, path: str, content: str) -> str:
        path = await cls.validate_path(path)
        original = await cls.read_file(path) if Path(path).exists() else ""
        await cls.write_file(path, content)
        return cls.generate_diff(original, content)

    @staticmethod
    def generate_diff(original: str, modified: str) -> str:
        diff = difflib.unified_diff(
            original.splitlines(keepends=True),
            modified.splitlines(keepends=True),
            fromfile='original',
            tofile='modified'
        )
        return ''.join(diff)

    @classmethod
    async def list_directory(cls, path: str) -> list[str]:
        path = await cls.validate_path(path)
        entries = []
        for item in Path(path).iterdir():
            entries.append(str(item))
        return entries

    @classmethod
    async def create_directory(cls, path: str) -> None:
        path = await cls.validate_path(path)
        Path(path).mkdir(parents=True, exist_ok=True)

    @classmethod
    def _load_gitignore(cls, path: str) -> list[str]:
        gitignore_path = os.path.join(path, ".gitignore")
        patterns = []
        if os.path.exists(gitignore_path):
            with open(gitignore_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        patterns.append(line)
        return patterns

    @classmethod
    def _get_tracked_files(cls, repo_path: str) -> Optional[Set[str]]:
        try:
            repo = git.Repo(repo_path)
            return set(repo.git.ls_files().splitlines())
        except git.exc.InvalidGitRepositoryError:
            return None

    @classmethod
    async def directory_tree(cls, path: str) -> Tuple[str, int, int]:
        path = await cls.validate_path(path)
        base_path = Path(path)

        # Try git tracking first
        tracked_files = cls._get_tracked_files(path)
        gitignore = cls._load_gitignore(path) if tracked_files is None else []
        
        def gen_tree(path: Path, prefix: str = "") -> Tuple[list[str], int, int]:
            entries = []
            dir_count = 0
            file_count = 0
            
            items = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name))
            for i, item in enumerate(items):
                rel_path = str(item.relative_to(base_path))

                # Skip if file should be ignored
                if tracked_files is not None:
                    if rel_path not in tracked_files and not any(str(p.relative_to(base_path)) in tracked_files for p in item.rglob("*") if p.is_file()):
                        continue
                else:  
                    # Use gitignore
                    if cls._should_ignore(rel_path, gitignore):
                        continue
                    
                is_last = i == len(items) - 1
                curr_prefix = "└── " if is_last else "├── "
                curr_line = prefix + curr_prefix + item.name
                
                if item.is_dir():
                    next_prefix = prefix + ("    " if is_last else "│   ")
                    subtree, sub_dirs, sub_files = gen_tree(item, next_prefix)
                    if tracked_files is not None and not subtree:
                        continue
                    entries.extend([curr_line] + subtree)
                    dir_count += 1 + sub_dirs
                    file_count += sub_files
                else:
                    if tracked_files is not None and rel_path not in tracked_files:
                        continue
                    entries.append(curr_line)
                    file_count += 1
                    
            return entries, dir_count, file_count
            
        tree_lines, total_dirs, total_files = gen_tree(Path(path))
        return "\n".join(tree_lines), total_dirs, total_files

    @classmethod
    def _should_ignore(cls, path: str, patterns: list[str]) -> bool:
        if not patterns:
            return False

        parts = Path(path).parts
        for pattern in patterns:
            pattern = pattern.strip()
            if not pattern or pattern.startswith('#'):
                continue

            if pattern.endswith('/'):
                pattern = pattern.rstrip('/')
                if pattern in parts:
                    return True
            else:
                if fnmatch.fnmatch(parts[-1], pattern):  # Match basename
                    return True
                # Match full path
                if fnmatch.fnmatch(path, pattern):
                    return True

        return False

    @classmethod
    async def search_files(cls, path: str, pattern: str, excludes: Optional[list[str]] = None) -> list[str]:
        path = await cls.validate_path(path)
        gitignore = cls._load_gitignore(path)
        if excludes:
            gitignore.extend(excludes)
            
        results = []
        for root, _, files in os.walk(path):
            rel_root = os.path.relpath(root, path)
            if rel_root != "." and cls._should_ignore(rel_root, gitignore):
                continue
                
            for file in files:
                rel_path = os.path.join(rel_root, file)
                if rel_path != "." and cls._should_ignore(rel_path, gitignore):
                    continue
                    
                if pattern in file or fnmatch.fnmatch(file, pattern):
                    results.append(os.path.join(root, file))
                    
        return results