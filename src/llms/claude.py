import os
import anthropic
from dotenv import load_dotenv

load_dotenv()  # Make sure environment variables are loaded

PRIMARY_API_KEY = os.getenv("ANTHROPIC_API_KEY")
BACKUP_API_KEY = os.getenv("ANTHROPIC_BACKUP_API_KEY")

if not PRIMARY_API_KEY and not BACKUP_API_KEY:
    raise ValueError("Neither ANTHROPIC_API_KEY nor ANTHROPIC_BACKUP_API_KEY is set in environment")

# Start with primary key
CURRENT_API_KEY = PRIMARY_API_KEY if PRIMARY_API_KEY else BACKUP_API_KEY
client = anthropic.Anthropic(api_key=CURRENT_API_KEY)

def get_claude_response(prompt: str, model: str = "claude-opus-4-1", max_tokens: int = 1024) -> str:
    global client, CURRENT_API_KEY
    
    try:
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
        
    except Exception as e:
        error_msg = str(e).lower()
        
        # Check if it's a credit/billing error and we have a backup key
        if ("credit" in error_msg or "billing" in error_msg or "quota" in error_msg or 
            "insufficient" in error_msg or "limit" in error_msg) and BACKUP_API_KEY and CURRENT_API_KEY != BACKUP_API_KEY:
            
            print(f"Primary API key failed due to credits/quota: {e}")
            print("Switching to backup API key...")
            
            # Switch to backup key
            CURRENT_API_KEY = BACKUP_API_KEY
            client = anthropic.Anthropic(api_key=CURRENT_API_KEY)
            
            try:
                response = client.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
                
            except Exception as backup_error:
                raise Exception(f"Both API keys failed. Primary: {str(e)}, Backup: {str(backup_error)}")
        
        # Re-raise original error if no backup or different error type
        raise e

def main():
    prompt = "Hello, world! Can you give me a fun fact?"
    answer = get_claude_response(prompt)
    print("Claude says:\n", answer)

if __name__ == "__main__":
    main()
