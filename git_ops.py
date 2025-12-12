from git import Repo
import uuid

def create_branch_and_apply_patch(repo_path, patch):
    repo = Repo(repo_path)
    origin = repo.remote(name="origin")

    branch = f"auto-fix-{uuid.uuid4().hex[:6]}"
    repo.git.checkout("-b", branch)

    repo.git.apply("--whitespace=fix", patch)
    repo.git.add(A=True)
    repo.index.commit("Auto-fix: add null safety check")

    origin.push(branch)  # 🔥 REQUIRED

    return branch
