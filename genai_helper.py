from dotenv import load_dotenv
import os
from google import genai

# Load .env file
load_dotenv()

# Debug check (optional)
print("API KEY FOUND:", bool(os.getenv("GEMINI_API_KEY")))

# Create Gemini client
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
"""

        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt
        )

        return response.text.strip()

    except Exception as e:
        print("AI ERROR:", e)
        return "⚠️ AI service is temporarily unavailable."
