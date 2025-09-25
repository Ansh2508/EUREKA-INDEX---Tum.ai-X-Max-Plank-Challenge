import os
import anthropic
from dotenv import load_dotenv

load_dotenv()  # Make sure environment variables are loaded

API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not API_KEY:
    raise ValueError("ANTHROPIC_API_KEY not set in environment")

client = anthropic.Anthropic(api_key=API_KEY)

def get_claude_response(prompt: str, model: str = "claude-sonnet-4-20250514", max_tokens: int = 1024) -> str:
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text

def main():
    prompt = "Hello, world! Can you give me a fun fact?"
    answer = get_claude_response(prompt)
    print("Claude says:\n", answer)

if __name__ == "__main__":
    main()
