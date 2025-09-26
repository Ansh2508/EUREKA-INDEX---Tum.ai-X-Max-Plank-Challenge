# Deployment Instructions

## API Keys Required

### Essential APIs
- **ANTHROPIC_API_KEY**: https://console.anthropic.com/ (Primary Claude API key)
- **GROQ_API_KEY**: https://console.groq.com/keys
- **LOGIC_MILL_API_TOKEN**: https://logic-mill.net

### Backup/Fallback APIs
- **ANTHROPIC_BACKUP_API_KEY**: https://console.anthropic.com/ (Backup Claude API key - optional but recommended)

### Optional APIs (for enhanced features)
- None required - all web search handled by Claude Opus 4.1

## Railway Deployment

### Environment Variables
Set these in Railway dashboard under Variables:

```
NODE_ENV=production
ANTHROPIC_API_KEY=your_primary_anthropic_key_here
ANTHROPIC_BACKUP_API_KEY=your_backup_anthropic_key_here  # Optional but recommended
GROQ_API_KEY=your_groq_api_key_here
LOGIC_MILL_API_TOKEN=your_logic_mill_token_here
```

### Health Check Configuration
- **Path**: `/health`
- **Timeout**: 300 seconds
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

## Features

### Core Analysis
- Technology Readiness Level (TRL) assessment
- Market gap analysis
- Commercial indicators evaluation
- Patent and publication analysis

### AI-Powered Reports (NEW!)
- **Claude Opus 4.1** integration for comprehensive technology transfer reports
- **Anthropic web search** for current market information via Claude's built-in web search
- **Automatic API key fallback** - switches to backup key if primary fails due to credits/quota
- Real-time market trend analysis with up-to-date information
- Professional-grade reports for researchers and TT offices

### User Interface
- **Production Mode**: Clean interface with comprehensive analysis
- **Development Mode**: Full debug information and raw data
- **Responsive Design**: Works on desktop and mobile

## Dependencies

### Production (Railway)
Uses `requirements-minimal.txt` for stable deployment:
- FastAPI 0.104.1
- Uvicorn 0.24.0 
- Anthropic 0.34.0
- Groq 0.8.0
- Other essential packages

### Development (Local)
Uses `requirements.txt` for full feature set including:
- All production dependencies
- Enhanced ML libraries
- Development tools

## Usage

1. **Basic Analysis**: Enter technology title and abstract, click "Analyze Technology"
2. **AI Report Generation**: After analysis, click "Generate AI Report" for comprehensive assessment
3. **Enhanced Dashboard**: Visit `/dashboard` for advanced patent intelligence features

## Health Check
The application provides a health check endpoint at `/health` that returns:
```json
{"status": "healthy", "message": "Technology Assessment API is running"}
```

## Configuration Endpoint
The `/config` endpoint provides environment information to the frontend:
```json
{
  "environment": "production",
  "debug": false,
  "production": true,
  "features": {
    "enhanced_agents": true,
    "api_docs": false
  }
}
```