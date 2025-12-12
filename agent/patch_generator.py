import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

gemini_model = genai.GenerativeModel("gemini-1.5-flash")


def gemini_generate_patch(prompt: str) -> str | None:
    try:
        resp = gemini_model.generate_content(
            prompt,
            generation_config={
                "temperature": 0,
                "max_output_tokens": 800
            }
        )
        return resp.text.strip()
    except Exception as e:
        print(f"❌ Gemini error: {e}")
        return None
