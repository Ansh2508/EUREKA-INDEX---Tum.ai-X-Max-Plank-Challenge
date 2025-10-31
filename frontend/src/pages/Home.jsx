import { 
  Microscope, 
  BarChart3, 
  Bot, 
  Bell, 
  ClipboardList, 
  ArrowRight,
  Zap,
  Target,
  TrendingUp
} from 'lucide-react'
import './Home.css'

function Home() {
  return (
    <div className="home-page">
      <div className="home-container">
        <div className="hero-section">
          <div className="hero-content">
            <h1 className="hero-title">
              Welcome to <span className="brand-highlight">EUREKA INDEX</span>
            </h1>
            <p className="hero-subtitle">
              AI-powered patent intelligence and research commercialization platform
            </p>
            <div className="hero-features">
              <div className="feature-item">
                <span className="feature-icon">
                  <Microscope size={20} />
                </span>
                <span>Research Analysis</span>
              </div>
              <div className="feature-item">
                <span className="feature-icon">
                  <BarChart3 size={20} />
                </span>
                <span>Market Intelligence</span>
              </div>
              <div className="feature-item">
                <span className="feature-icon">
                  <Bot size={20} />
                </span>
                <span>AI-Powered Insights</span>
              </div>
            </div>
            <div className="hero-actions">
              <a href="/dashboard" className="btn btn-primary btn-large">
                Go to Dashboard
              </a>
              <a href="/analysis" className="btn btn-secondary btn-large">
                Start Analysis
              </a>
            </div>
          </div>
        </div>

        <div className="features-section">
          <h2 className="section-title">Platform Features</h2>
          <div className="features-grid">
            <div className="feature-card">
              <div className="card-icon">
                <Microscope size={32} />
              </div>
              <h3>Research Analysis</h3>
              <p>Analyze your research against patent databases to assess market potential and identify similar technologies.</p>
              <a href="/analysis" className="card-link">
                Get Started <ArrowRight size={16} />
              </a>
            </div>
            <div className="feature-card">
              <div className="card-icon">
                <BarChart3 size={32} />
              </div>
              <h3>Analytics Dashboard</h3>
              <p>Comprehensive dashboard with insights, trends, and analytics for technology transfer decisions.</p>
              <a href="/dashboard" className="card-link">
                View Dashboard <ArrowRight size={16} />
              </a>
            </div>
            <div className="feature-card">
              <div className="card-icon">
                <Bell size={32} />
              </div>
              <h3>Patent Alerts</h3>
              <p>Stay informed with automated alerts about new patents and publications in your research area.</p>
              <a href="/alerts" className="card-link">
                Setup Alerts <ArrowRight size={16} />
              </a>
            </div>
            <div className="feature-card">
              <div className="card-icon">
                <ClipboardList size={32} />
              </div>
              <h3>Detailed Reports</h3>
              <p>Generate comprehensive reports with market analysis, IP assessment, and commercialization recommendations.</p>
              <a href="/reports" className="card-link">
                View Reports <ArrowRight size={16} />
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Home