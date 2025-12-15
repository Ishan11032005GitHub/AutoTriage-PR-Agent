import requests
from config import GITHUB_TOKEN

HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

def pr_exists(owner: str, repo: str, issue_number: int) -> bool:
    """
    Returns True if an open PR already exists that fixes this issue.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls?state=open"
    res = requests.get(url, headers=HEADERS)

    if res.status_code != 200:
        raise RuntimeError(f"Failed to list PRs: {res.text}")

    prs = res.json()

    needle = f"Fixes #{issue_number}"

    for pr in prs:
        body = pr.get("body") or ""
        if needle in body:
            return True

    return False
