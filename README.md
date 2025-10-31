# EUREKA INDEX - Technology Transfer Analysis Platform

AI-powered technology transfer analysis platform for evaluating research innovations, patent potential, and commercialization opportunities.

## 🏗️ Project Structure

```
EUREKA-INDEX/
├── backend/              # FastAPI Python backend
│   ├── src/             # Source code
│   │   ├── agents/      # AI agents (semantic alerts, competitor discovery, etc.)
│   │   ├── routes/      # API route handlers
│   │   ├── services/    # External service integrations
│   │   ├── llms/        # LLM integrations
│   │   └── analysis.py  # Core analysis logic
│   ├── main.py          # Full-featured application
│   ├── main_simple.py   # Minimal deployment version
│   ├── requirements.txt # Python dependencies
│   └── Procfile         # Railway deployment config
│
├── frontend/            # React + Vite frontend
│   ├── src/
│   │   ├── pages/       # Page components (Home, Analysis, Dashboard)
│   │   ├── components/  # Reusable components
│   │   └── App.jsx      # Main app component
│   ├── public/          # Static assets
│   └── package.json     # Node dependencies
│
└── docs/                # Project documentation
    ├── CRITICAL_ANALYSIS_REPORT.md
    ├── FIX_IMPLEMENTATION_GUIDE.md
    ├── EXECUTIVE_SUMMARY.md
    └── ...
```

## 🚀 Quick Start

### Prerequisites

- **Backend**: Python 3.9+
- **Frontend**: Node.js 18+ and npm
- **API Keys**: Anthropic API key, Groq API key (optional)

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
# Create a .env file with:
# ANTHROPIC_API_KEY=your_key_here
# GROQ_API_KEY=your_key_here (optional)

# Run the backend
uvicorn main:app --reload
```

Backend will be available at: `http://localhost:8000`

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```

Frontend will be available at: `http://localhost:5173`

## 📋 Features

### Core Analysis Features
- **Patent Novelty Assessment**: AI-powered analysis of patent novelty and prior art
- **TRL Evaluation**: Technology Readiness Level assessment (1-9 scale)
- **Market Potential Analysis**: TAM/SAM/SOM calculations with CAGR projections
- **IP Strength Assessment**: Patent strength and competitive positioning
- **Competitive Landscape**: Key player identification and collaboration opportunities
- **AI-Generated Reports**: Comprehensive technology transfer reports

### Patent Intelligence Features
- **Semantic Patent Alerts**: Similarity-based patent monitoring
- **Competitor Discovery**: Network analysis of competitive landscape
- **Licensing Opportunities**: Identification of licensing potential
- **Enhanced Novelty Assessment**: Deep semantic similarity analysis

## 🔧 API Endpoints

### Analysis Endpoints
- `POST /analyze` - Analyze research title and abstract
- `POST /results/intelligence_analysis` - Patent intelligence analysis
- `GET /health` - Health check endpoint

### Patent Intelligence Endpoints
- `POST /patent-intelligence/semantic-alerts` - Semantic patent alerts
- `POST /patent-intelligence/competitor-discovery` - Competitor analysis
- `POST /patent-intelligence/licensing-opportunities` - Licensing analysis
- `POST /patent-intelligence/enhanced-novelty` - Enhanced novelty assessment

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI
- **AI/ML**: Anthropic Claude, Groq LLMs
- **Data Sources**: OpenAlex API, Logic Mill API
- **ML Libraries**: sentence-transformers, scikit-learn, networkx, pandas
- **Deployment**: Railway with Docker

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite (with Rolldown)
- **Routing**: React Router v6
- **Styling**: Custom CSS (no framework dependencies)

## 📦 Deployment

### Backend Deployment (Railway)

The backend is configured for Railway deployment:

```bash
# Railway will automatically detect and use:
# - Procfile for process configuration
# - railway.toml for build settings
# - requirements.txt for dependencies
```

### Frontend Deployment

Build the frontend for production:

```bash
cd frontend
npm run build
```

The `dist/` folder can be deployed to any static hosting service (Vercel, Netlify, etc.)

## 🔐 Environment Variables & API Keys

### Backend (.env)
```env
ANTHROPIC_API_KEY=your_anthropic_key
GROQ_API_KEY=your_groq_key (optional)
LOGIC_MILL_API_KEY=your_logic_mill_key (optional)
```

### Get API Keys:
- **Logic Mill**: https://logic-mill.net/identity/api-token
- **Groq**: https://console.groq.com/keys
- **Anthropic**: https://console.anthropic.com/settings/keys

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
```

## 📚 Documentation

Comprehensive documentation is available in the `docs/` folder:

- **EXECUTIVE_SUMMARY.md** - High-level overview for stakeholders
- **CRITICAL_ANALYSIS_REPORT.md** - Detailed code analysis and issues
- **FIX_IMPLEMENTATION_GUIDE.md** - Step-by-step fix instructions
- **QUICK_FIX_SUMMARY.md** - Emergency fixes and quick reference
- **ARCHITECTURE_AND_ISSUES.md** - Architecture diagrams and analysis

## 🐛 Known Issues

See `docs/CRITICAL_ANALYSIS_REPORT.md` for a comprehensive list of known issues and their fixes.

### Critical Issues to Address:
1. Missing ML dependencies in `requirements-minimal.txt`
2. Async/sync bug in `main.py:493`
3. Unregistered patent intelligence routes
4. Hardcoded admin password
5. 600+ lines of duplicate code in `enhanced_novelty.py`

## 🎯 Roadmap

- [ ] Add authentication and rate limiting
- [ ] Implement database/caching layer
- [ ] Complete all service integrations
- [ ] Add comprehensive test coverage
- [ ] Implement CI/CD pipeline
- [ ] Add monitoring and logging
- [ ] Create admin dashboard
- [ ] Add geographic visualization of research/companies
- [ ] Implement voice interface

## 📄 License

This project is licensed under the MIT License.

---

**Built with ❤️ for technology transfer professionals and researchers**
