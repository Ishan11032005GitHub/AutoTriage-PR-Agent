import sys
import os
import subprocess
import time

from agent.issue_reader import fetch_bug_issues
from agent.file_finder import search_repo
from agent.patch_generator import generate_fixed_content
from agent.pr_creator import create_pr
from git_ops import create_branch_and_commit
from config import GITHUB_TOKEN

DRY_RUN = False   # set True to disable PR creation


def parse_repo():
    if len(sys.argv) != 2:
        raise RuntimeError("Usage: python main.py OWNER/REPO")
    return sys.argv[1].split("/")


def prepare_repo(owner, repo):
    path = f"./repos/{owner}__{repo}"
    clone_url = f"https://{GITHUB_TOKEN}@github.com/{owner}/{repo}.git"

    if not os.path.exists(path):
        print(f"📥 Cloning {owner}/{repo}")
        subprocess.run(["git", "clone", clone_url, path], check=True)
    else:
        print(f"🔄 Updating {owner}/{repo}")
        subprocess.run(["git", "-C", path, "fetch"], check=True)
        subprocess.run(["git", "-C", path, "checkout", "main"], check=True)
        subprocess.run(["git", "-C", path, "reset", "--hard", "origin/main"], check=True)

    return path


def confidence_score(file_found, patch_generated, file_lines):
    score = 0.0
    if file_found:
        score += 0.4
    if patch_generated:
        score += 0.4
    if file_lines < 300:
        score += 0.2
    return score


def run():
    owner, repo = parse_repo()
    print(f"🔍 Running agent for repo: {owner}/{repo}")

    repo_path = prepare_repo(owner, repo)

    t0 = time.time()
    bugs = fetch_bug_issues(owner, repo)
    print(f"⏱️ fetch issues: {time.time() - t0:.2f}s")
    print(f"🐞 Bugs found: {len(bugs)}")

    for issue in bugs:
        issue_t0 = time.time()
        print(f"➡️ Processing issue #{issue['number']}")

        keywords = issue["title"].split()
        file_path = search_repo(keywords, repo_path)
        print(f"📄 File candidate: {file_path}")

        if not file_path:
            print("❌ Cannot locate relevant file. Skipping.")
            continue

        with open(file_path, "r", errors="ignore") as f:
            content = f.read()

        new_content = generate_fixed_content(issue, content, os.path.basename(file_path))
        if not new_content:
            print("❌ No safe fix produced. Skipping.")
            continue

        score = confidence_score(True, True, len(content.splitlines()))
        if score < 0.7:
            print(f"⚠️ Low confidence ({score:.2f}). Skipping PR.")
            continue

        if DRY_RUN:
            print("🧪 DRY RUN: PR not created")
            continue

        branch = create_branch_and_commit(repo_path, file_path, new_content)
        create_pr(owner, repo, branch, issue)

        print(f"✅ PR created for issue #{issue['number']}")
        print(f"⏱️ issue processed in {time.time() - issue_t0:.2f}s")


if __name__ == "__main__":
    run()
