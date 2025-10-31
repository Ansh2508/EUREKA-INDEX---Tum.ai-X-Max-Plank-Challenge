# LLM integrations module with error handling
available_llms = []

try:
    from .claude import get_claude_response
    available_llms.append("get_claude_response")
except ImportError as e:
    print(f"Warning: Claude LLM not available: {e}")

try:
    from .google_ai import get_google_ai_response
    available_llms.append("get_google_ai_response")
except ImportError as e:
    print(f"Warning: Google AI LLM not available: {e}")

try:
    from .grok import get_grok_response
    available_llms.append("get_grok_response")
except ImportError as e:
    print(f"Warning: Grok LLM not available: {e}")

try:
    from .groq import get_groq_response
    available_llms.append("get_groq_response")
except ImportError as e:
    print(f"Warning: Groq LLM not available: {e}")

try:
    from .huggingface import get_huggingface_response
    available_llms.append("get_huggingface_response")
except ImportError as e:
    print(f"Warning: HuggingFace LLM not available: {e}")

__all__ = available_llms

