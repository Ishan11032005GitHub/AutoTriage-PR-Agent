from openai import OpenAI
client = OpenAI()

def is_safe_patch(patch: str) -> bool:
    if not patch.startswith("diff --git"):
        return False

    forbidden = [
        "rm -rf",
        "DROP TABLE",
        "ALTER USER",
        "DELETE FROM",
        "TRUNCATE",
        "chmod 777",
    ]

    return not any(f in patch for f in forbidden)


def generate_patch(issue, file_content):
    prompt = f"""
You are fixing a LOW RISK bug.

Rules:
- Only add null/undefined checks
- Do not refactor
- Do not change logic
- Return a unified diff ONLY

Issue:
{issue['title']}
{issue.get('body', '')}

File:
{file_content}
"""

    resp = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    patch = resp.output_text.strip()

    if not is_safe_patch(patch):
        return None

    return patch
