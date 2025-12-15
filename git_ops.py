from git import Repo
import uuid
import os


def create_branch_and_commit(repo_path, file_path, new_content, issue_number):
    repo = Repo(repo_path)

    # 1️⃣ Safe, traceable, unique branch name
    branch = f"auto-fix-{issue_number}-{uuid.uuid4().hex[:6]}"
    repo.git.checkout("-b", branch)

    # 2️⃣ Normalize paths
    repo_path_norm = os.path.normpath(repo_path)
    file_path_norm = os.path.normpath(file_path)

    # 3️⃣ Resolve absolute file path
    if os.path.isabs(file_path_norm):
        abs_path = file_path_norm
    else:
        if file_path_norm.startswith(repo_path_norm + os.sep):
            abs_path = file_path_norm
        else:
            abs_path = os.path.join(repo_path_norm, file_path_norm)

    abs_path = os.path.normpath(abs_path)

    # 4️⃣ Write fixed content
    with open(abs_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    # 5️⃣ Repo-relative path for git
    rel_path = os.path.relpath(abs_path, repo_path_norm).replace("\\", "/")

    repo.git.add(rel_path)
    repo.index.commit(f"Auto-fix: guard null access (issue #{issue_number})")

    # 6️⃣ Push branch
    repo.git.push("origin", branch)

    return branch
