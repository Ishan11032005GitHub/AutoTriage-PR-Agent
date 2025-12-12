import os
import subprocess

def search_repo(keywords, repo_path):
    candidates = {}

    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith((".py", ".js", ".ts", ".java")):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", errors="ignore") as f:
                        text = f.read()
                        for kw in keywords:
                            if kw.lower() in text.lower():
                                candidates[path] = candidates.get(path, 0) + 1
                except:
                    pass

    return max(candidates, key=candidates.get) if candidates else None
