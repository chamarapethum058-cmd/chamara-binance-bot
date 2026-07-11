import os
from google import genai

key = os.environ.get("GEMINI_API_KEY", "YOUR_API_KEY")

print("--- Testing gemini-2.0-flash ---")
try:
    client = genai.Client(api_key=key)
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents="Hello"
    )
    print("SUCCESS (2.0):", response.text)
except Exception as e:
    print("FAILED (2.0):", str(e))

print("\n--- Testing gemini-1.5-flash ---")
try:
    client = genai.Client(api_key=key)
    response = client.models.generate_content(
        model='gemini-1.5-flash',
        contents="Hello"
    )
    print("SUCCESS (1.5):", response.text)
except Exception as e:
    print("FAILED (1.5):", str(e))
