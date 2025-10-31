# EUREKA INDEX

> AI-Powered Technology Transfer Analysis Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Node.js](https://img.shields.io/badge/Node.js-18+-green.svg)](https://nodejs.org/)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-red.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org/)

EUREKA INDEX is an intelligent platform that analyzes research potential, assesses patent landscapes, and provides actionable insights for technology transfer decisions. Built with AI-powered analysis engines and modern web technologies.

## ✨ Features

### 🔬 Research Analysis
- **Technology Readiness Level (TRL) Assessment** - Automated evaluation of research maturity
- **Novelty Assessment** - AI-powered analysis of innovation uniqueness
- **Market Potential Analysis** - Commercial viability scoring
- **IP Strength Evaluation** - Patent landscape and protection analysis

### 🤖 AI-Powered Intelligence
- **Semantic Patent Monitoring** - Real-time patent alerts using advanced NLP
- **Competitor Discovery** - Network analysis of competitive landscape
- **Licensing Opportunity Mapping** - Identification of commercialization paths
- **Enhanced Novelty Assessment** - Deep learning-based innovation analysis

### 📊 Patent Intelligence Dashboard
- Interactive patent landscape visualization
- Technology trend analysis
- Key player identification
- Market opportunity insights

## 🏗️ Architecture

```
eureka-index/
├── frontend/          # React + Vite frontend
│   ├── src/
│   │   ├── pages/     # Home, Analysis, Dashboard
│   │   └── components/ # Reusable UI components
│   └── dist/          # Production build
│
├── backend/           # FastAPI backend
│   ├── src/
│   │   ├── agents/    # AI analysis agents
│   │   ├── routes/    # API endpoints
│   │   ├── services/  # External integrations
│   │   └── llms/      # LLM providers
│   └── main.py        # Application entry point
│
└── docs/              # Documentation
```

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.9+ and pip
- **API Keys** (see Configuration section)

### 1. Clone Repository

```bash
git clone https://github.com/your-org/eureka-index.git
cd eureka-index
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```

### 4. Run Development Servers

**Backend** (Terminal 1):
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend** (Terminal 2):
```bash
cd frontend
npm run dev
```

**Access the application:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## ⚙️ Configuration

### Required API Keys

Create a `.env` file in the `backend/` directory:

```env
# Required
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional (for enhanced features)
GROQ_API_KEY=your_groq_api_key_here
LOGIC_MILL_API_KEY=your_logic_mill_api_key_here
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | ✅ | Claude AI API key for analysis |
| `GROQ_API_KEY` | ⚪ | Alternative LLM provider |
| `LOGIC_MILL_API_KEY` | ⚪ | Patent search API access |
| `NODE_ENV` | ⚪ | Environment mode (development/production) |

## 📡 API Endpoints

### Core Analysis
- `POST /analyze` - Analyze research potential
- `GET /health` - Service health check

### Patent Intelligence
- `POST /patent-intelligence/semantic-alerts` - Patent monitoring
- `POST /patent-intelligence/competitor-discovery` - Competitor analysis
- `POST /patent-intelligence/licensing-opportunities` - Licensing analysis
- `POST /patent-intelligence/enhanced-novelty` - Deep novelty assessment

### Intelligence Analysis
- `POST /results/intelligence_analysis` - Comprehensive patent intelligence

## 🧪 Testing

### Frontend Tests
```bash
cd frontend

# Unit tests
npm test

# E2E tests
npm run test:e2e

# Test coverage
npm run test:coverage
```

### Backend Tests
```bash
cd backend

# Run tests
pytest

# With coverage
pytest --cov=src

# Quick health check
python quick_check.py
```

## 🚢 Deployment

### Production Build

```bash
# Build frontend
npm run build

# The application is configured for Vercel deployment
# Frontend builds to frontend/dist/
# Backend runs on FastAPI with uvicorn
```

### Deployment Platforms

**Vercel** (Recommended for frontend):
- Configured via `vercel.json`
- Automatic deployments from Git

**Railway** (Backend):
- Configured via `Procfile` and `railway.toml`
- Environment variables managed in Railway dashboard

**Docker**:
```bash
# Build and run backend
cd backend
docker build -t eureka-index-backend .
docker run -p 8000:8000 --env-file .env eureka-index-backend
```

## 🛠️ Development

### Tech Stack

**Frontend:**
- React 18 with Vite
- React Router for navigation
- Lucide React for icons
- Custom CSS (no frameworks)
- Jest + Playwright for testing

**Backend:**
- FastAPI with Pydantic
- Anthropic Claude AI
- OpenAlex API integration
- Logic Mill patent search
- Uvicorn ASGI server

**AI/ML:**
- Sentence Transformers
- Scikit-learn
- NetworkX for graph analysis
- Pandas for data processing

### Code Style

- **Frontend**: ESLint configuration
- **Backend**: PEP 8 Python style guide
- **Type Safety**: TypeScript-style JSDoc, Python type hints

## 📚 Documentation

- [`backend/README.md`](backend/README.md) - Backend API documentation
- [`frontend/README.md`](frontend/README.md) - Frontend development guide
- [`docs/`](docs/) - Additional project documentation
- API Docs: http://localhost:8000/docs (when running)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow existing code style and conventions
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting PR

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the `docs/` folder and component READMEs
- **API Reference**: Visit `/docs` endpoint when backend is running
- **Issues**: Open an issue on GitHub for bugs or feature requests

## 🙏 Acknowledgments

- OpenAlex for research publication data
- Anthropic for Claude AI capabilities
- Logic Mill for patent search services
- The open-source community for amazing tools and libraries

---

**Built with ❤️ by the EUREKA INDEX Team**

*Empowering technology transfer decisions through AI-powered analysis*