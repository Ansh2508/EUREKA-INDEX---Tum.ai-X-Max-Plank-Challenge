import { useState, useEffect } from 'react'
import AnalysisForm from '../components/ResearchAnalysis/AnalysisForm'
import ResultsDisplay from '../components/ResearchAnalysis/ResultsDisplay'
import LoadingSpinner from '../components/UI/LoadingSpinner'
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
      const response = await fetch('/api/research/analyze', {
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

      const analysisResponse = await response.json()
      const analysisId = analysisResponse.id

      // Poll for results
      let attempts = 0
      const maxAttempts = 30 // 30 seconds max
      
      const pollResults = async () => {
        try {
          const resultResponse = await fetch(`/api/research/results/${analysisId}`)
          
          if (!resultResponse.ok) {
            throw new Error(`Failed to get results (${resultResponse.status})`)
          }
          
          const resultData = await resultResponse.json()
          
          if (resultData.status === 'completed' && resultData.results) {
            setAnalysisProgress(100)
            setTimeout(() => {
              setResults(resultData.results)
              saveToHistory(formData, resultData.results)
              clearInterval(progressInterval)
              setLoading(false)
            }, 500)
            return
          } else if (resultData.status === 'failed') {
            throw new Error(resultData.results?.error || 'Analysis failed')
          } else if (resultData.status === 'processing' || resultData.status === 'pending') {
            // Continue polling
            attempts++
            if (attempts < maxAttempts) {
              setTimeout(pollResults, 1000)
            } else {
              throw new Error('Analysis timeout - please try again')
            }
          }
        } catch (pollError) {
          console.error('Polling error:', pollError)
          setError(pollError.message || 'Failed to get analysis results')
          clearInterval(progressInterval)
          setLoading(false)
        }
      }

      // Start polling after a short delay
      setTimeout(pollResults, 1000)
      
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
        <div className="page-header">
          <div className="header-content">
            <h1>Research Analysis</h1>
            <p className="subtitle">
              Submit your research details to discover similar patents and assess market potential
            </p>
          </div>
          
          {analysisHistory.length > 0 && (
            <div className="header-actions">
              <button 
                className="btn btn-secondary"
                onClick={() => setShowHistory(!showHistory)}
              >
                {showHistory ? 'Hide History' : `View History (${analysisHistory.length})`}
              </button>
            </div>
          )}
        </div>

        {showHistory && (
          <div className="analysis-history">
            <div className="history-header">
              <h3>Recent Analyses</h3>
              <button className="btn btn-text" onClick={clearHistory}>
                Clear All
              </button>
            </div>
            <div className="history-list">
              {analysisHistory.map((item) => (
                <div 
                  key={item.id} 
                  className="history-item"
                  onClick={() => handleHistorySelect(item)}
                >
                  <div className="history-title">{item.title}</div>
                  <div className="history-abstract">{item.abstract}</div>
                  <div className="history-date">
                    {new Date(item.timestamp).toLocaleDateString()}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="analysis-content">
          <div className="form-section">
            <AnalysisForm onSubmit={handleSubmit} loading={loading} />
          </div>

          {error && (
            <div className="error-section">
              <div className="error-message">
                <div className="error-icon">!</div>
                <div className="error-content">
                  <strong>Analysis Failed</strong>
                  <p>{error}</p>
                  <div className="error-actions">
                    <button 
                      className="btn btn-primary btn-small"
                      onClick={() => {
                        setError(null)
                        // Retry with last form data if available
                        const lastFormData = JSON.parse(localStorage.getItem('lastAnalysisRequest') || '{}')
                        if (lastFormData.title && lastFormData.abstract) {
                          handleSubmit(lastFormData)
                        }
                      }}
                    >
                      Retry Analysis
                    </button>
                    <button 
                      className="btn btn-text"
                      onClick={() => setError(null)}
                    >
                      Dismiss
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {loading && (
            <div className="loading-section">
              <LoadingSpinner 
                size="large" 
                message="Analyzing your research against patent databases..." 
                progress={analysisProgress}
              />
              <div className="loading-steps">
                <div className={`step ${analysisProgress > 0 ? 'active' : ''} ${analysisProgress > 25 ? 'completed' : ''}`}>
                  Searching patent databases
                </div>
                <div className={`step ${analysisProgress > 25 ? 'active' : ''} ${analysisProgress > 50 ? 'completed' : ''}`}>
                  Calculating similarity scores
                </div>
                <div className={`step ${analysisProgress > 50 ? 'active' : ''} ${analysisProgress > 75 ? 'completed' : ''}`}>
                  Analyzing market potential
                </div>
                <div className={`step ${analysisProgress > 75 ? 'active' : ''} ${analysisProgress >= 100 ? 'completed' : ''}`}>
                  Generating report
                </div>
              </div>
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ width: `${analysisProgress}%` }}
                ></div>
              </div>
              <div className="progress-text">
                {Math.round(analysisProgress)}% Complete
              </div>
            </div>
          )}

          {results && !loading && (
            <div className="results-section">
              <ResultsDisplay results={results} />
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Analysis

