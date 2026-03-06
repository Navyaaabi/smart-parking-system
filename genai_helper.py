from dotenv import load_dotenv
import os
from google import genai

load_dotenv()

print("API KEY FOUND:", bool(os.getenv("GEMINI_API_KEY")))

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def ai_reply(context, user_message):
    try:
        prompt = f"""
You are a smart parking assistant.

Context:
{context}

User Question:
{user_message}

Answer briefly and clearly.
Avoid unwanted details. If the question is unrelated, politely guide the user back to parking-related topics.
While Greeting only greet back and do not provide parking information. If the user asks for parking info, provide it based on the context above.
if asked about high profile customers arrival time, tell integrated in future
"""

        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt
        )

        return response.text.strip()

    except Exception as e:
        print("AI ERROR:", e)
        return "⚠️ AI service is temporarily unavailable."
