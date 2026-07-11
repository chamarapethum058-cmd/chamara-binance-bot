import os
from google import genai

key = os.environ.get("GEMINI_API_KEY", "YOUR_API_KEY")
try:
    client = genai.Client(api_key=key)
    response = client.models.generate_content(
        model='gemini-3.5-flash',
        contents="Hello"
    )
    print("SUCCESS: Key is working now. Response:", response.text)
except Exception as e:
    print("FAILED:", str(e))
