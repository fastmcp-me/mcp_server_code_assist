import git

def git_status(repo: git.Repo) -> str:
    return repo.git.status()

def git_diff_unstaged(repo: git.Repo) -> str:
    return repo.git.diff()

def git_diff_staged(repo: git.Repo) -> str:
    return repo.git.diff("--cached")

def git_diff(repo: git.Repo, target: str) -> str:
    return repo.git.diff(target)

def git_log(repo: git.Repo, max_count: int = 10) -> str:
    commits = list(repo.iter_commits(max_count=max_count))
    log = []
    for commit in commits:
        log.append(f"Commit: {commit.hexsha}\nAuthor: {commit.author}\nDate: {commit.authored_datetime}\nMessage: {commit.message}\n")
    return "\n".join(log)

def git_show(repo: git.Repo, revision: str) -> str:
    commit = repo.commit(revision)
    output = [f"Commit: {commit.hexsha}\nAuthor: {commit.author}\nDate: {commit.authored_datetime}\nMessage: {commit.message}\n"]
    return "".join(output)