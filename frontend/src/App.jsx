import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import Home from './pages/Home'
import Dashboard from './pages/Dashboard'
import Analysis from './pages/Analysis'
import './App.css'

function App() {
  return (
    <Router>
      <div className="app">
        <nav className="navbar">
          <div className="nav-container">
            <Link to="/" className="nav-logo">
              <img src="/favicon.svg" alt="EUREKA INDEX" className="logo-icon" />
              <span>EUREKA INDEX</span>
            </Link>
            <div className="nav-links">
              <Link to="/" className="nav-link">Home</Link>
              <Link to="/analysis" className="nav-link">Analysis</Link>
              <Link to="/dashboard" className="nav-link">Dashboard</Link>
            </div>
          </div>
        </nav>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/analysis" element={<Analysis />} />
            <Route path="/dashboard" element={<Dashboard />} />
          </Routes>
        </main>

        <footer className="footer">
          <div className="footer-content">
            <p>&copy; 2024 EUREKA INDEX - Technology Transfer Analysis Platform</p>
            <p>AI-powered patent intelligence and research commercialization</p>
          </div>
        </footer>
      </div>
    </Router>
  )
}

export default App
