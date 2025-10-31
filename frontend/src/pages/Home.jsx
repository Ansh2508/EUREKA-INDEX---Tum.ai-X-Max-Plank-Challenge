import { Link } from 'react-router-dom'
import './Home.css'

function Home() {
  return (
    <div className="home">
      <section className="hero">
        <div className="hero-content">
          <h1 className="hero-title">
            EUREKA INDEX
          </h1>
          <p className="hero-subtitle">
            AI-Powered Technology Transfer Analysis Platform
          </p>
          <p className="hero-description">
            Evaluate patent potential, novelty assessment, and commercialization 
            opportunities for research innovations. Get comprehensive IP intelligence in minutes.
          </p>
          <div className="hero-buttons">
            <Link to="/analysis" className="btn btn-primary">
              Start Analysis
            </Link>
            <Link to="/dashboard" className="btn btn-secondary">
              View Dashboard
            </Link>
          </div>
        </div>
      </section>

      <section className="features">
        <div className="features-container">
          <h2 className="section-title">Key Features</h2>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">🔍</div>
              <h3>Patent Novelty Assessment</h3>
              <p>AI-powered analysis of patent novelty and prior art landscape</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">📊</div>
              <h3>TRL Evaluation</h3>
              <p>Technology Readiness Level assessment for commercialization planning</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">💡</div>
              <h3>Market Potential Analysis</h3>
              <p>Comprehensive market size and opportunity evaluation</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🎯</div>
              <h3>IP Strength Assessment</h3>
              <p>Evaluate patent strength and competitive positioning</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🌐</div>
              <h3>Competitive Landscape</h3>
              <p>Identify key players and collaboration opportunities</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">📝</div>
              <h3>AI-Generated Reports</h3>
              <p>Comprehensive technology transfer reports powered by Claude AI</p>
            </div>
          </div>
        </div>
      </section>

      <section className="how-it-works">
        <div className="how-it-works-container">
          <h2 className="section-title">How It Works</h2>
          <div className="steps">
            <div className="step">
              <div className="step-number">1</div>
              <h3>Submit Research</h3>
              <p>Enter your research title and abstract</p>
            </div>
            <div className="step">
              <div className="step-number">2</div>
              <h3>AI Analysis</h3>
              <p>Our AI analyzes patents, publications, and market data</p>
            </div>
            <div className="step">
              <div className="step-number">3</div>
              <h3>Get Insights</h3>
              <p>Receive comprehensive analysis and recommendations</p>
            </div>
          </div>
        </div>
      </section>

      <section className="cta">
        <div className="cta-content">
          <h2>Ready to Analyze Your Research?</h2>
          <p>Get started with EUREKA INDEX today</p>
          <Link to="/analysis" className="btn btn-primary btn-large">
            Start Free Analysis
          </Link>
        </div>
      </section>
    </div>
  )
}

export default Home

