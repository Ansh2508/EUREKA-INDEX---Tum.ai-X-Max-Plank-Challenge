# Railway Deployment Guide

## Umgebungsvariablen in Railway konfigurieren:

```
LOGIC_MILL_API_TOKEN=your_logic_mill_token_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here  
GROQ_API_KEY=your_groq_api_key_here
```

## API-Keys erhalten:

- **Logic Mill**: https://logic-mill.net/identity/api-token
- **Groq**: https://console.groq.com/keys
- **Anthropic**: https://console.anthropic.com/settings/keys

## Deployment:

Railway sollte automatisch das Deployment mit `railway.toml` konfigurieren.

**Start-Kommando:**
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

**Health Check:**
- Endpoint: `/health`
- Timeout: 100s

## Dependencies:

Alle benötigten Pakete sind in `requirements.txt` definiert und werden automatisch installiert.
