# EUREKA INDEX - Technology Transfer Analysis Platform

AI-Powered Technology Transfer Analysis Platform that helps researchers, universities, and organizations evaluate the commercial potential of their innovations.

## 🚀 Features

- **AI-Powered Analysis**: Advanced machine learning algorithms for patent and research analysis
- **Patent Intelligence**: Real-time patent search and monitoring with similarity detection
- **Market Analytics**: Data-driven insights into technology trends and commercialization potential
- **Smart Alerts**: Automated monitoring of new patents and research publications
- **Comprehensive Reports**: Detailed technology transfer reports with actionable recommendations
- **Novelty Assessment**: Compare innovations against existing patents and research

## 🛠 Tech Stack

### Frontend
- **React 18** - Modern UI library with hooks and concurrent features
- **Vite** - Lightning-fast build tool and dev server
- **React Router** - Client-side routing for single-page application
- **Lucide React** - Beautiful, customizable SVG icons
- **CSS3** - Modern styling with grid, flexbox, and animations

### Backend
- **FastAPI** - High-performance Python web framework
- **Uvicorn** - ASGI server for production deployment
- **Pydantic** - Data validation and serialization
- **Python 3.9+** - Modern Python with type hints

### AI & ML
- **Anthropic Claude** - Advanced AI for patent analysis and insights
- **Groq** - High-speed inference for real-time processing
- **Custom NLP** - Specialized models for patent text analysis

## 📊 Scoring Methodology

EUREKA INDEX uses sophisticated multi-dimensional scoring algorithms:

- **Market Potential Score (0-10)**: TAM analysis, commercial activity, innovation momentum
- **Technology Readiness Level (TRL 1-9)**: Keyword-based classification with patent volume adjustment
- **Competitive Landscape Analysis**: Intensity scoring and positioning assessment
- **IP Strength Assessment**: Multi-factor scoring with citation analysis
- **Regulatory Risk Assessment**: Domain-based risk scoring with compliance requirements

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- Python 3.9+
- npm or yarn

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Backend Development
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

## 🌐 Deployment

### Deploy to Vercel (Frontend)

1. **Push to GitHub**: Make sure your code is in a GitHub repository
2. **Connect to Vercel**: Go to [vercel.com](https://vercel.com) and sign in with GitHub
3. **Import Project**: Click "New Project" and select your repository
4. **Configure Settings**: Vercel will auto-detect the configuration from `vercel.json`
5. **Deploy**: Click "Deploy" and your app will be live!

The `vercel.json` configuration handles:
- Building the frontend from the `frontend/` directory
- Setting the correct output directory (`frontend/dist`)
- Configuring SPA routing for React Router

### Environment Variables
Set these in your Vercel dashboard:
- `VITE_API_URL` - Your backend API URL
- `VITE_APP_ENV` - Environment (production/development)

## 📁 Project Structure

```
EUREKA-INDEX/
├── frontend/                 # React frontend application
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   └── utils/          # Utility functions
│   ├── public/             # Static assets
│   └── package.json
├── backend/                 # FastAPI backend application
│   ├── src/
│   │   ├── routes/         # API routes
│   │   ├── services/       # Business logic
│   │   └── utils/          # Utility functions
│   ├── tests/              # Test files
│   └── requirements.txt
├── vercel.json             # Vercel deployment configuration
└── README.md
```

## 🧪 Testing

### Frontend Tests
```bash
cd frontend
npm run test              # Unit tests
npm run test:e2e         # End-to-end tests
npm run test:coverage    # Coverage report
```

### Backend Tests
```bash
cd backend
pytest                   # Run all tests
pytest --cov            # Coverage report
```

## 📈 Market Coverage

EUREKA INDEX analyzes 25+ industry domains including:
- Healthcare ($580B TAM, 8.9% CAGR)
- Space Technology ($485B TAM, 15% CAGR)
- AI/ML ($380B TAM, 25% CAGR)
- Defense Technology ($520B TAM, 8.5% CAGR)
- Quantum Computing ($65B TAM, 28% CAGR)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Max Planck Institute for research collaboration
- TUM.ai for technical partnership
- Open source community for amazing tools and libraries

---

**EUREKA INDEX** - Accelerating innovation through intelligent technology transfer analysis.