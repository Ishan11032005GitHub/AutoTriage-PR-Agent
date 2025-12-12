import sys
import os
import subprocess
from agent.issue_reader import fetch_bug_issues
from agent.file_finder import search_repo
from agent.patch_generator import generate_patch
from agent.pr_creator import create_pr
from git_ops import create_branch_and_apply_patch
from config import GITHUB_TOKEN

def parse_repo():
    if len(sys.argv) != 2:
        raise RuntimeError("Usage: python main.py OWNER/REPO")

    owner, repo = sys.argv[1].split("/")
    return owner, repo

def prepare_repo(owner, repo):
    path = f"./repos/{owner}__{repo}"

    clone_url = f"https://{GITHUB_TOKEN}@github.com/{owner}/{repo}.git"

    if not os.path.exists(path):
        print(f"📥 Cloning {owner}/{repo}")
        subprocess.run(
            ["git", "clone", clone_url, path],
            check=True
        )
    else:
        print(f"🔄 Updating {owner}/{repo}")
        subprocess.run(
            ["git", "-C", path, "pull"],
            check=True
        )

    return path


def run():
    owner, repo = parse_repo()
    print(f"🔍 Running agent for repo: {owner}/{repo}")

    repo_path = prepare_repo(owner, repo)

    bugs = fetch_bug_issues(owner, repo)
    print(f"🐞 Bugs found: {len(bugs)}")

    for issue in bugs:
        print(f"➡️ Processing issue #{issue['number']}")

        keywords = issue["title"].split()
        file = search_repo(keywords, repo_path)

        if not file:
            print("❌ Cannot locate relevant file. Skipping issue.")
            continue

        with open(file, "r", errors="ignore") as f:
            content = f.read()

        patch = generate_patch(issue, content)
        if not patch:
            print("❌ Unsafe or invalid patch. Skipping issue.")
            continue

        branch = create_branch_and_apply_patch(repo_path, patch)
        create_pr(owner, repo, branch, issue)

        print(f"✅ PR created for issue #{issue['number']}")


if __name__ == "__main__":
    run()
