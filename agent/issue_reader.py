import requests
from config import GITHUB_TOKEN

HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

def fetch_bug_issues(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    res = requests.get(url, headers=HEADERS)

    if res.status_code != 200:
        raise RuntimeError(f"GitHub API error {res.status_code}: {res.text}")

    data = res.json()
    if not isinstance(data, list):
        raise RuntimeError(f"Unexpected response: {data}")

    bugs = []
    for i in data:
        if "pull_request" in i:
            continue
        labels = [l["name"] for l in i.get("labels", [])]
        if "bug" in labels:
            bugs.append(i)

    return bugs
