import json
from google import genai
from app.config import GEMINI_API_KEY


INTENT_PROMPT = """
You are an intent extraction system.

Extract structured JSON from the user's question.

Return ONLY valid JSON in this format:

{
  "sector": string or null,
  "year": integer or null,
  "quarter": integer (1-4) or null,
  "metric": "pipeline_summary" or "revenue_service"
}

Rules:
- If user asks about revenue, billed, collected, receivable, AR → revenue_summary
- Otherwise → pipeline_summary
- If sector not mentioned → null
- If quarter not mentioned → null
- If year not mentioned → null
- Do NOT include explanations
- Do NOT include markdown
- Output ONLY JSON
"""


def llm_intent_parser(question: str):
    try:
        print("LLM INTENT PARSER CALLED")

        client = genai.Client(api_key=GEMINI_API_KEY)

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=INTENT_PROMPT + f"\nUser question: {question}",
        )

        text = response.text.strip()

        print("=== GEMINI RAW OUTPUT ===")
        print(text)
        print("=========================")

        start = text.find("{")
        end = text.rfind("}") + 1

        if start == -1 or end == -1:
            return None

        json_str = text[start:end]
        parsed = json.loads(json_str)

        return parsed

    except Exception as e:
        print("Gemini Error:", e)
        return None