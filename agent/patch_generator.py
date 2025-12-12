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


def generate_patch(issue, file_content, file_name):
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

    except RateLimitError:
        print("❌ OpenAI quota/billing issue.")
        return None
    except APIStatusError as e:
        print(f"❌ OpenAI API error: {e.status_code}")
        return None

    if not is_safe_patch(patch):
        return None

    return patch.replace("a/file.py", f"a/{file_name}") \
                 .replace("b/file.py", f"b/{file_name}")
