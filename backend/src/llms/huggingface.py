import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("HUGGINGFACE_API_KEY")
HF_API_URL = "https://api-inference.huggingface.co/models"

def get_huggingface_response(prompt: str, model: str = "microsoft/DialoGPT-medium", max_tokens: int = 1024) -> str:
    """
    Get response from Hugging Face Inference API
    Popular free models:
    - microsoft/DialoGPT-medium
    - facebook/blenderbot-400M-distill
    - microsoft/DialoGPT-large
    """
    
    if not API_KEY:
        return "Error: HUGGINGFACE_API_KEY not set in environment"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": max_tokens,
            "temperature": 0.7,
            "return_full_text": False
        }
    }
    
    try:
        response = requests.post(f"{HF_API_URL}/{model}", headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        
        if isinstance(data, list) and len(data) > 0:
            return data[0].get("generated_text", str(data))
        else:
            return str(data)
            
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    prompt = "Hello, how are you today?"
    answer = get_huggingface_response(prompt)
    print("Hugging Face says:\n", answer)

if __name__ == "__main__":
    main()