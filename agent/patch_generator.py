from openai import OpenAI
from openai import RateLimitError, APIStatusError

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

def generate_patch(issue, file_content):
    prompt = f"""Return a unified diff ONLY.
Rules:
- Only null/undefined guards
- No refactors
- No logic change

Issue:
{issue['title']}
{issue.get('body','')}

File:
{file_content}
"""

    try:
        resp = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt
        )
        patch = resp.output_text.strip()

    except RateLimitError as e:
        print("❌ OpenAI quota/billing issue (429). Fix billing and rerun.")
        return None
    except APIStatusError as e:
        print(f"❌ OpenAI API error: {e.status_code} - {e.message}")
        return None

    # keep your is_safe_patch() check here
    if not is_safe_patch(patch):
        return None

    return patch
