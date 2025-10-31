import { useState, useEffect } from 'react'
import { Microscope, History, ChevronRight, RotateCcw, X, Clock, CheckCircle, AlertCircle } from 'lucide-react'
import AnalysisForm from '../components/ResearchAnalysis/AnalysisForm'
import ResultsDisplay from '../components/ResearchAnalysis/ResultsDisplay'
import './Analysis.css'

function Analysis() {
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)
  const [analysisHistory, setAnalysisHistory] = useState([])
  const [showHistory, setShowHistory] = useState(false)
  const [analysisProgress, setAnalysisProgress] = useState(0)

  // Load analysis history from localStorage on component mount
  useEffect(() => {
    const savedHistory = localStorage.getItem('analysisHistory')
    if (savedHistory) {
      try {
        setAnalysisHistory(JSON.parse(savedHistory))
      } catch (err) {
        console.error('Failed to load analysis history:', err)
      }
    }
  }, [])

  // Save analysis to history
  const saveToHistory = (formData, results) => {
    const analysisEntry = {
      id: Date.now(),
      timestamp: new Date().toISOString(),
      title: formData.title,
      abstract: formData.abstract.substring(0, 200) + '...',
      results: results
    }

    const newHistory = [analysisEntry, ...analysisHistory.slice(0, 9)] // Keep last 10
    setAnalysisHistory(newHistory)
    localStorage.setItem('analysisHistory', JSON.stringify(newHistory))
  }

  const handleSubmit = async (formData) => {
    setLoading(true)
    setError(null)
    setResults(null)
    setAnalysisProgress(0)

    // Simulate progress updates for better UX
    const progressInterval = setInterval(() => {
      setAnalysisProgress(prev => {
        if (prev >= 90) return prev
        return prev + Math.random() * 15
      })
    }, 1000)

    try {
      // Save form data for retry functionality
      localStorage.setItem('lastAnalysisRequest', JSON.stringify(formData))

      // Submit analysis request
      const response = await fetch('/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        const errorMessage = errorData.detail?.errors
          ? errorData.detail.errors.join(', ')
          : errorData.detail || `Analysis failed (${response.status})`
        throw new Error(errorMessage)
      }

      // Get results directly (no polling needed for /analyze endpoint)
      const analysisResults = await response.json()

      // Simulate progress completion
      setAnalysisProgress(100)

      setTimeout(() => {
        setResults(analysisResults)
        saveToHistory(formData, analysisResults)
        clearInterval(progressInterval)
        setLoading(false)
      }, 500)

    } catch (err) {
      console.error('Analysis error:', err)
      setError(err.message || 'An unexpected error occurred during analysis')
      clearInterval(progressInterval)
      setLoading(false)
    }
  }

  const handleHistorySelect = (historyItem) => {
    setResults(historyItem.results)
    setShowHistory(false)
    setError(null)
  }

  const clearHistory = () => {
    setAnalysisHistory([])
    localStorage.removeItem('analysisHistory')
  }

  return (
    <div className="analysis-page">
      <div className="analysis-container">
        <div className="analysis-header">
          <div className="header-content">
            <h1>Research Analysis</h1>
          </div>
          <div className="header-actions">
            {analysisHistory.length > 0 && (
              <button
                className="modern-btn history-btn"
                onClick={() => setShowHistory(!showHistory)}
              >
                <History size={16} />
                {showHistory ? 'Hide' : `History (${analysisHistory.length})`}
              </button>
            )}
          </div>
        </div>

        {showHistory && (
          <div className="history-panel">
            <div className="history-header">
              <h3>Recent Analyses</h3>
              <button className="clear-btn" onClick={clearHistory}>
                Clear All
              </button>
            </div>
            <div className="history-grid">
              {analysisHistory.map((item) => (
                <div
                  key={item.id}
                  className="history-card"
                  onClick={() => handleHistorySelect(item)}
                >
                  <div className="history-content">
                    <div className="history-title">{item.title}</div>
                    <div className="history-abstract">{item.abstract}</div>
                  </div>
                  <div className="history-meta">
                    <div className="history-date">
                      <Clock size={14} />
                      {new Date(item.timestamp).toLocaleDateString()}
                    </div>
                    <ChevronRight size={16} className="history-arrow" />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="analysis-main">
          {!results && !loading && (
            <div className="form-card">
              <AnalysisForm onSubmit={handleSubmit} loading={loading} />
            </div>
          )}

          {error && (
            <div className="error-card">
              <div className="error-header">
                <AlertCircle size={24} className="error-icon" />
                <div className="error-title">
                  <h3>Analysis Failed</h3>
                  <p>{error}</p>
                </div>
                <button className="close-btn" onClick={() => setError(null)}>
                  <X size={20} />
                </button>
              </div>
              <div className="error-actions">
                <button
                  className="modern-btn primary-btn"
                  onClick={() => {
                    setError(null)
                    const lastFormData = JSON.parse(localStorage.getItem('lastAnalysisRequest') || '{}')
                    if (lastFormData.title && lastFormData.abstract) {
                      handleSubmit(lastFormData)
                    }
                  }}
                >
                  <RotateCcw size={18} />
                  Retry Analysis
                </button>
              </div>
            </div>
          )}

          {loading && (
            <div className="loading-card">
              <div className="loading-header">
                <div className="loading-icon">
                  <Microscope size={32} />
                </div>
                <div className="loading-title">
                  <h2>Analyzing Research</h2>
                  <p>Processing your research against patent databases...</p>
                </div>
              </div>

              <div className="progress-section">
                <div className="progress-bar">
                  <div
                    className="progress-fill"
                    style={{ width: `${analysisProgress}%` }}
                  />
                </div>
                <div className="progress-text">
                  {Math.round(analysisProgress)}% Complete
                </div>
              </div>

              <div className="analysis-steps">
                <div className={`analysis-step ${analysisProgress > 0 ? 'active' : ''} ${analysisProgress > 25 ? 'completed' : ''}`}>
                  <div className="step-indicator">
                    {analysisProgress > 25 ? <CheckCircle size={16} /> : <div className="step-dot" />}
                  </div>
                  <div className="step-content">
                    <div className="step-title">Searching Patent Databases</div>
                    <div className="step-description">Scanning millions of patents and publications</div>
                  </div>
                </div>

                <div className={`analysis-step ${analysisProgress > 25 ? 'active' : ''} ${analysisProgress > 50 ? 'completed' : ''}`}>
                  <div className="step-indicator">
                    {analysisProgress > 50 ? <CheckCircle size={16} /> : <div className="step-dot" />}
                  </div>
                  <div className="step-content">
                    <div className="step-title">Calculating Similarity Scores</div>
                    <div className="step-description">AI-powered semantic analysis and matching</div>
                  </div>
                </div>

                <div className={`analysis-step ${analysisProgress > 50 ? 'active' : ''} ${analysisProgress > 75 ? 'completed' : ''}`}>
                  <div className="step-indicator">
                    {analysisProgress > 75 ? <CheckCircle size={16} /> : <div className="step-dot" />}
                  </div>
                  <div className="step-content">
                    <div className="step-title">Market Potential Analysis</div>
                    <div className="step-description">Evaluating commercial viability and opportunities</div>
                  </div>
                </div>

                <div className={`analysis-step ${analysisProgress > 75 ? 'active' : ''} ${analysisProgress >= 100 ? 'completed' : ''}`}>
                  <div className="step-indicator">
                    {analysisProgress >= 100 ? <CheckCircle size={16} /> : <div className="step-dot" />}
                  </div>
                  <div className="step-content">
                    <div className="step-title">Generating Report</div>
                    <div className="step-description">Compiling insights and recommendations</div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {results && !loading && (
            <div className="results-card">
              <ResultsDisplay results={results} />
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Analysis

