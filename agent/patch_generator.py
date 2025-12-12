import re
import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel("gemini-flash-latest")

# Pattern: return obj.mid.attr
RISKY_RETURN = re.compile(
    r'^(\s*)return\s+([a-zA-Z_]\w*)\.([a-zA-Z_]\w*)\.([a-zA-Z_]\w*)(?:\s+#.*)?\s*$'
)


def rule_based_fix(file_content: str) -> str | None:
    lines = file_content.splitlines()
    new_lines = []
    applied = False

    for line in lines:
        m = RISKY_RETURN.match(line)
        if m and not applied:
            indent, obj, mid, attr = m.groups()
            new_lines.append(f"{indent}if {obj}.{mid}:")
            new_lines.append(f"{indent}    return {obj}.{mid}.{attr}")
            new_lines.append(f"{indent}return None")
            applied = True
        else:
            new_lines.append(line)

    if applied:
        return "\n".join(new_lines) + "\n"

    return None


def generate_fixed_content(issue, file_content, file_name):
    # 1️⃣ Deterministic rule-based fix
    fixed = rule_based_fix(file_content)
    if fixed:
        print("🧠 Rule-based fix applied")
        return fixed

    # 2️⃣ Gemini fallback (OPTIONAL)
    file_snippet = "\n".join(file_content.splitlines()[:200])

    prompt = f"""Fix a LOW RISK bug.
Rules:
- Only null/undefined guards
- No refactors
- No logic change

Issue:
{issue['title']}
{issue.get('body', '')}

File:
{file_snippet}
"""

    try:
        resp = gemini_model.generate_content(
            prompt,
            generation_config={"temperature": 0, "max_output_tokens": 800}
        )
        text = resp.text.strip()
        return text if text else None
    except Exception:
        return None
