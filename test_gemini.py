from google import genai
import os

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("GEMINI_API_KEY is not configured.")

client = genai.Client(
    api_key=api_key,
    http_options={
        "timeout": 30000,
    },
)

print("Connecting to Gemini...")

response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents="Say hello in one sentence."
)

print("\nGemini response:")
print(response.text)