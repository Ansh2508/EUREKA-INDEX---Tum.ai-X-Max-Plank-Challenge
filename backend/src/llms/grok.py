import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GROK_API_KEY")
GROK_API_URL = "https://api.x.ai/v1/chat/completions"

def get_grok_response(prompt: str, model: str = "grok-4-latest", max_tokens: int = 1024) -> str:
    """
    Get response from Grok (xAI) API
    Available models:
    - grok-4-latest (most capable)
    - grok-beta (beta version)
    """
    
    if not API_KEY:
        return "Error: GROK_API_KEY not set in environment"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    payload = {
        "messages": [
            {
                "role": "system",
                "content": "You are Grok, a helpful AI assistant with deep reasoning capabilities."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "model": model,
        "stream": False,
        "temperature": 0.7,
        "max_tokens": max_tokens
    }
    
    try:
        response = requests.post(GROK_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        
        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"]
        else:
            return f"Unexpected response format: {data}"
            
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    prompt = "Explain the philosophical implications of artificial consciousness and whether current AI systems like yourself could be considered conscious."
    answer = get_grok_response(prompt)
    print("Grok says:\n", answer)

if __name__ == "__main__":
    main()