# claude_api.py
import os
import requests

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

def get_claude_response(prompt: str, model: str = "claude-sonnet-4-20250514", max_tokens: int = 1024) -> str:
    """
    Sends a prompt to the Claude API and returns the assistant's response.

    Args:
        prompt (str): The text prompt to send to Claude.
        model (str, optional): Model name. Defaults to "claude-sonnet-4-20250514".
        max_tokens (int, optional): Maximum tokens in the response. Defaults to 1024.

    Returns:
        str: The response text from Claude.
    """
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }

    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(ANTHROPIC_API_URL, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()

    # The API response structure may vary; usually it's in 'completion' field
    return data.get("completion") or data.get("response") or ""


@app.post("/claude")
def ask_claude(request: ClaudeRequest):
    """
    Dedicated endpoint to ask Claude.
    """
    try:
        response = get_claude_response(request.prompt)
    except Exception as e:
        response = f"Claude API error: {str(e)}"
    return {"response": response}

@app.get("/claude")
def claude_page():
    """
    Serve Claude HTML page.
    """
    return FileResponse(os.path.join("static", "claude.html"))


# Example usage
if __name__ == "__main__":
    resp = get_claude_response("Hello, world")
    print(resp)
