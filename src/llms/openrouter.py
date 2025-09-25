import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

API_KEY = os.getenv("OPENROUTER_API_KEY")
if not API_KEY:
    raise ValueError("OPENROUTER_API_KEY not set in environment")

API_URL = "https://openrouter.ai/api/v1/chat/completions"

def get_openrouter_response(prompt: str, model: str = "openai/gpt-4o") -> str:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        # Optional headers for OpenRouter ranking:
        # "HTTP-Referer": "<YOUR_SITE_URL>",
        # "X-Title": "<YOUR_SITE_NAME>",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
    response.raise_for_status()
    data = response.json()

    # Usually the response text is under choices[0].message.content
    if "choices" in data and len(data["choices"]) > 0:
        return data["choices"][0]["message"]["content"]
    
    return str(data)

def main():
    prompt = "What is the meaning of life?"
    answer = get_openrouter_response(prompt)
    print("OpenRouter says:\n", answer)

if __name__ == "__main__":
    main()
