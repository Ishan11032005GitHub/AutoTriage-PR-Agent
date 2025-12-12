from git import Repo
import uuid
import os


def create_branch_and_commit(repo_path, file_path, new_content):
    repo = Repo(repo_path)

    branch = f"auto-fix-{uuid.uuid4().hex[:6]}"
    repo.git.checkout("-b", branch)

    # Normalize inputs
    repo_path_norm = os.path.normpath(repo_path)
    file_path_norm = os.path.normpath(file_path)

    # Determine absolute path for writing the file
    if os.path.isabs(file_path_norm):
        abs_path = file_path_norm
    else:
        # If `file_path` already contains the repo path, avoid joining twice
        if file_path_norm.startswith(repo_path_norm + os.sep) or repo_path_norm in file_path_norm:
            abs_path = file_path_norm
        else:
            abs_path = os.path.join(repo_path, file_path_norm)

    abs_path = os.path.normpath(abs_path)

    with open(abs_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    # Compute repository-relative path for git operations
    try:
        rel_path = os.path.relpath(abs_path, repo_path_norm)
    except Exception:
        rel_path = file_path_norm

    rel_path = rel_path.replace("\\", "/")

    repo.git.add(rel_path)
    repo.index.commit("Auto-fix: add null safety guard")

    # Push branch to remote
    repo.git.push("origin", branch)

    return branch
