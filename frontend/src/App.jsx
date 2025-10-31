import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom'
import { useState, useEffect } from 'react'
import Sidebar from './components/Layout/Sidebar'
import Home from './pages/Home'
import Dashboard from './pages/Dashboard'
import Analysis from './pages/Analysis'
import PatentAlerts from './pages/PatentAlerts'
import NoveltyAssessment from './pages/NoveltyAssessment'
import About from './pages/About'
import './App.css'

function AppContent() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [isMobile, setIsMobile] = useState(false)
  const location = useLocation()

  // Don't show sidebar on home page
  const showSidebar = location.pathname !== '/'

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth <= 768)
      if (window.innerWidth <= 768) {
        setMobileMenuOpen(false)
      }
    }

    checkMobile()
    window.addEventListener('resize', checkMobile)
    return () => window.removeEventListener('resize', checkMobile)
  }, [])

  const toggleMobileMenu = () => {
    setMobileMenuOpen(!mobileMenuOpen)
  }

  return (
    <div className="app">
      {showSidebar && (
        <Sidebar
          collapsed={sidebarCollapsed}
          mobileOpen={mobileMenuOpen}
          onCollapsedChange={setSidebarCollapsed}
          onMobileToggle={setMobileMenuOpen}
        />
      )}

      {showSidebar && isMobile && (
        <button
          className="mobile-menu-toggle"
          onClick={toggleMobileMenu}
          aria-label="Toggle menu"
        >
          <span className="hamburger-icon">
            <span></span>
            <span></span>
            <span></span>
          </span>
        </button>
      )}

      {mobileMenuOpen && <div className="mobile-overlay" onClick={() => setMobileMenuOpen(false)} />}

      <div className={`app-content ${showSidebar && sidebarCollapsed ? 'sidebar-collapsed' : ''} ${!showSidebar ? 'no-sidebar' : ''}`}>
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/analysis" element={<Analysis />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/patents" element={<div className="page-placeholder">Patents page coming soon...</div>} />
            <Route path="/alerts" element={<PatentAlerts />} />
            <Route path="/novelty" element={<NoveltyAssessment />} />
            <Route path="/reports" element={<div className="page-placeholder">Reports page coming soon...</div>} />
            <Route path="/settings" element={<div className="page-placeholder">Settings page coming soon...</div>} />
            <Route path="/about" element={<About />} />
          </Routes>
        </main>

        <footer className="footer">
          <div className="footer-content">
            <p>&copy; 2025 EUREKA INDEX - Technology Transfer Analysis Platform</p>
            <p>AI-powered patent intelligence and research commercialization</p>
          </div>
        </footer>
      </div>
    </div>
  )
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  )
}

export default App
