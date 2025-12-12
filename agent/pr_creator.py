import requests
from config import GITHUB_TOKEN, BASE_BRANCH

HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

def create_pr(owner, repo, branch, issue):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls"

    payload = {
        "title": f"Fix: {issue['title']}",
        "head": f"{owner}:{branch}",
        "base": BASE_BRANCH,
        "body": f"Fixes #{issue['number']}\n\nAuto-generated low-risk fix."
    }

    res = requests.post(url, headers=HEADERS, json=payload)

    if res.status_code not in (200, 201):
        raise RuntimeError(f"PR creation failed: {res.text}")
