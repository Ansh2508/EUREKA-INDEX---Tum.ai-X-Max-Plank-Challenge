import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")

def get_groq_response(prompt: str, model: str = "llama-3.3-70b-versatile", max_tokens: int = 1024) -> str:
    """
    Get response from Groq API
    Available models:
    - llama-3.3-70b-versatile (recommended, fast)
    - llama-3.1-70b-versatile
    - mixtral-8x7b-32768
    - gemma2-9b-it
    """
    
    if not API_KEY:
        return "Error: GROQ_API_KEY not set in environment"
    
    try:
        client = Groq(api_key=API_KEY)
        
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant specialized in technology transfer and patent analysis."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model=model,
            temperature=0.7,
            max_tokens=max_tokens,
        )
        
        return chat_completion.choices[0].message.content
            
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    prompt = "Explain the difference between a patent and a research paper."
    answer = get_groq_response(prompt)
    print("Groq says:\n", answer)

if __name__ == "__main__":
    main()

