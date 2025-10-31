# EUREKA INDEX - Backend

FastAPI-based backend for the EUREKA INDEX Technology Transfer Analysis Platform.

## 📁 Structure

```
backend/
├── src/
│   ├── agents/                    # AI Agent Implementations
│   │   ├── semantic_alerts.py     # Semantic patent monitoring
│   │   ├── competitor_discovery.py # Competitor network analysis
│   │   ├── licensing_opportunities.py # Licensing potential analysis
│   │   └── enhanced_novelty.py    # Deep novelty assessment
│   │
│   ├── routes/                    # API Route Handlers
│   │   ├── llm_routes.py         # LLM-related endpoints
│   │   ├── openalex.py           # OpenAlex integration routes
│   │   ├── related_works.py      # Related works search
│   │   └── patent_intelligence.py # Patent intelligence routes
│   │
│   ├── services/                  # External Service Integrations
│   │   ├── ai_report_generator.py # AI report generation
│   │   ├── logic_mill.py         # Logic Mill API client
│   │   ├── openalex.py           # OpenAlex API client
│   │   ├── espacenet.py          # Espacenet integration
│   │   └── alexa_integration.py  # Alexa integration
│   │
│   ├── llms/                      # LLM Integrations
│   │   └── ...                   # LLM provider implementations
│   │
│   ├── analysis.py                # Core Analysis Logic (1300+ lines)
│   ├── search_logic_mill.py       # Logic Mill search implementation
│   ├── utils.py                   # Utility functions
│   └── market_data_config.py      # Market data configuration
│
├── main.py                        # Full-featured application
├── main_simple.py                 # Minimal deployment version
├── quick_check.py                 # Quick health check utility
├── requirements.txt               # Full dependencies
├── requirements-minimal.txt       # Minimal dependencies
├── Procfile                       # Railway deployment config
├── railway.toml                   # Railway build settings
└── .gitignore                     # Git ignore rules
```

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Installation

1. **Create and activate virtual environment:**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

2. **Install dependencies:**

```bash
# Full installation (recommended for development)
pip install -r requirements.txt

# Minimal installation (for production/testing)
pip install -r requirements-minimal.txt
```

3. **Set up environment variables:**

Create a `.env` file in the backend directory:

```env
# Required
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional
GROQ_API_KEY=your_groq_api_key_here
LOGIC_MILL_API_KEY=your_logic_mill_api_key_here
```

### Running the Application

#### Development Mode (Full Features)

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Production Mode (Minimal)

```bash
uvicorn main_simple:app --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

## 📡 API Endpoints

### Core Analysis

- **POST /analyze**
  - Analyze research title and abstract
  - Returns: TRL score, novelty assessment, market potential, IP strength

- **GET /health**
  - Health check endpoint
  - Returns: Service status

### Patent Intelligence

- **POST /patent-intelligence/semantic-alerts**
  - Semantic patent monitoring
  - Requires: sentence-transformers, sklearn

- **POST /patent-intelligence/competitor-discovery**
  - Competitor network analysis
  - Requires: networkx, pandas

- **POST /patent-intelligence/licensing-opportunities**
  - Licensing potential analysis

- **POST /patent-intelligence/enhanced-novelty**
  - Deep novelty assessment
  - Requires: sentence-transformers

### Intelligence Analysis

- **POST /results/intelligence_analysis**
  - Comprehensive patent intelligence analysis
  - Input: Publication and patent data (JSON)
  - Output: Key players, trends, opportunities

## 🔧 Configuration

### Deployment Modes

The backend supports two deployment modes:

1. **Full Mode (`main.py`)**: All features enabled, requires all dependencies
2. **Minimal Mode (`main_simple.py`)**: Basic functionality, minimal dependencies

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Anthropic Claude API key |
| `GROQ_API_KEY` | No | Groq API key for alternative LLM |
| `LOGIC_MILL_API_KEY` | No | Logic Mill patent search API key |
| `PORT` | No | Server port (default: 8000) |

## 🐛 Known Issues

### Critical Issues

1. **Missing ML Dependencies** (requirements-minimal.txt)
   - Missing: sentence-transformers, scikit-learn, networkx, pandas, numpy
   - Impact: All AI agents fail in minimal deployment
   - Fix: Add missing dependencies to requirements-minimal.txt

2. **Async/Sync Bug** (main.py:493)
   - Mixing synchronous and asynchronous code
   - Impact: Potential runtime errors
   - Fix: Use `await` for async functions or `asyncio.run()` for sync context

3. **Unregistered Routes** (main.py)
   - patent_intelligence routes not imported/registered
   - Impact: 404 errors for patent intelligence endpoints
   - Fix: Add `app.include_router(patent_intelligence.router)`

4. **Hardcoded Password** (main.py:180)
   - Admin password hardcoded as "admin123"
   - Impact: Security vulnerability
   - Fix: Use environment variable or secure secret management

5. **Duplicate Code** (enhanced_novelty.py)
   - 600+ lines of duplicate class definitions
   - Impact: Maintenance burden, potential bugs
   - Fix: Remove duplicate classes, keep only one version

See `docs/CRITICAL_ANALYSIS_REPORT.md` for complete issue list and fixes.

## 🧪 Testing

```bash
# Run tests (when implemented)
pytest

# Run with coverage
pytest --cov=src

# Quick health check
python quick_check.py
```

## 📦 Deployment

### Railway Deployment

The backend is configured for Railway deployment:

1. **Procfile** defines the start command
2. **railway.toml** configures build settings
3. **requirements.txt** lists dependencies

Deploy to Railway:

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy
railway up
```

### Docker Deployment

```bash
# Build image
docker build -t eureka-index-backend .

# Run container
docker run -p 8000:8000 --env-file .env eureka-index-backend
```

## 🔐 Security Considerations

1. **Never commit `.env` files** - Contains sensitive API keys
2. **Use environment variables** - For all secrets and configuration
3. **Implement rate limiting** - Prevent API abuse
4. **Add authentication** - Protect sensitive endpoints
5. **Validate input** - Prevent injection attacks

## 📚 Additional Documentation

- **DEPLOYMENT.md** - Detailed deployment instructions
- **ENVIRONMENT.md** - Environment setup guide
- **CI-CD-README.md** - CI/CD pipeline documentation
- **../docs/** - Project-wide documentation

## 🤝 Contributing

1. Follow PEP 8 style guide
2. Add type hints to functions
3. Write docstrings for classes and functions
4. Add tests for new features
5. Update documentation

## 📞 Support

For issues and questions:
- Check the documentation in `docs/`
- Review API docs at `/docs` endpoint
- Open an issue on GitHub

---

**Backend Version**: 1.0.0  
**FastAPI Version**: 0.115.6  
**Python Version**: 3.9+

