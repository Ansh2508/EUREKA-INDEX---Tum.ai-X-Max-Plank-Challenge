import os
import requests
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

API_KEY = os.getenv("GROQ_API_KEY")
if not API_KEY:
    raise ValueError("GROQ_API_KEY not set in environment")

GROQ_API_URL = "https://api.groq.com/openai/v1/responses"

#  = "openai/gpt-oss-20b")
def get_groq_response(prompt: str, model: str = "llama-3.3-70b-versatile") -> str:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "input": prompt
    }
    response = requests.post(GROQ_API_URL, headers=headers, json=payload)
    response.raise_for_status()  # Raise an exception for HTTP errors
    data = response.json()

    # Look for the first message output
    for item in data.get("output", []):
        if item.get("type") == "message":
            content_list = item.get("content", [])
            if content_list:
                return content_list[0].get("text", "")
    
    # Fallback
    return str(data)

def main():
    prompt = "Explain the importance of fast language models"
    answer = get_groq_response(prompt)
    print("Groq says:\n", answer)

if __name__ == "__main__":
    main()
