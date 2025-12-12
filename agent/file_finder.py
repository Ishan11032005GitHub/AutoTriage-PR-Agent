import os

SKIP_DIRS = {".git", "venv", "__pycache__", "node_modules"}


def search_repo(keywords, repo_path):
    candidates = {}

    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for file in files:
            if not file.endswith((".py", ".js", ".ts", ".java")):
                continue

            path = os.path.join(root, file)
            try:
                with open(path, "r", errors="ignore") as f:
                    text = f.read(2000)  # cap read size

                hits = sum(1 for kw in keywords if kw.lower() in text.lower())
                if hits:
                    candidates[path] = hits
                    if hits >= 3:
                        return path
            except:
                pass

    return max(candidates, key=candidates.get) if candidates else None
