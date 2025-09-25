import os
import requests

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

def get_claude_response(prompt: str, model: str = "claude-sonnet-4-20250514", max_tokens: int = 1024) -> str:
    """
    Send a prompt to Claude and return the response text.
    """
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }

    payload = {
        "model": model,
        "max_tokens": max_tokens,  # <-- corrected field name
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(ANTHROPIC_API_URL, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()

    return data.get("completion", str(data))
