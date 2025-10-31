import { useState, useEffect } from 'react'
import AssessmentForm from '../components/NoveltyAssessment/AssessmentForm'
import NoveltyReport from '../components/NoveltyAssessment/NoveltyReport'
import LoadingSpinner from '../components/UI/LoadingSpinner'
import './NoveltyAssessment.css'

function NoveltyAssessment() {
  const [loading, setLoading] = useState(false)
  const [assessment, setAssessment] = useState(null)
  const [error, setError] = useState(null)
  const [assessmentHistory, setAssessmentHistory] = useState([])
  const [showHistory, setShowHistory] = useState(false)
  const [assessmentProgress, setAssessmentProgress] = useState(0)
  const [currentAssessmentId, setCurrentAssessmentId] = useState(null)

  // Load assessment history from localStorage on component mount
  useEffect(() => {
    const savedHistory = localStorage.getItem('noveltyAssessmentHistory')
    if (savedHistory) {
      try {
        setAssessmentHistory(JSON.parse(savedHistory))
      } catch (err) {
        console.error('Failed to load assessment history:', err)
      }
    }
  }, [])

  // Save assessment to history
  const saveToHistory = (formData, assessment) => {
    const assessmentEntry = {
      id: Date.now(),
      timestamp: new Date().toISOString(),
      title: formData.research_title,
      abstract: formData.research_abstract.substring(0, 200) + '...',
      claims: formData.claims.length,
      assessment: assessment
    }
    
    const newHistory = [assessmentEntry, ...assessmentHistory.slice(0, 9)] // Keep last 10
    setAssessmentHistory(newHistory)
    localStorage.setItem('noveltyAssessmentHistory', JSON.stringify(newHistory))
  }

  const handleSubmit = async (formData) => {
    setLoading(true)
    setError(null)
    setAssessment(null)
    setAssessmentProgress(0)
    setCurrentAssessmentId(null)

    // Simulate progress updates for better UX
    const progressInterval = setInterval(() => {
      setAssessmentProgress(prev => {
        if (prev >= 90) return prev
        return prev + Math.random() * 10
      })
    }, 2000)

    try {
      // Save form data for retry functionality
      localStorage.setItem('lastNoveltyAssessmentRequest', JSON.stringify(formData))
      
      // Submit assessment request
      const response = await fetch('/api/novelty/assess', {
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
          : errorData.detail || `Assessment failed (${response.status})`
        throw new Error(errorMessage)
      }

      const assessmentResponse = await response.json()
      const assessmentId = assessmentResponse.assessment_id
      setCurrentAssessmentId(assessmentId)

      // Poll for results
      let attempts = 0
      const maxAttempts = 60 // 60 seconds max for novelty assessment
      
      const pollResults = async () => {
        try {
          const resultResponse = await fetch(`/api/novelty/results/${assessmentId}`)
          
          if (!resultResponse.ok) {
            throw new Error(`Failed to get results (${resultResponse.status})`)
          }
          
          const resultData = await resultResponse.json()
          
          if (resultData.status === 'completed' && resultData.assessment) {
            setAssessmentProgress(100)
            setTimeout(() => {
              setAssessment(resultData.assessment)
              saveToHistory(formData, resultData.assessment)
              clearInterval(progressInterval)
              setLoading(false)
            }, 500)
            return
          } else if (resultData.status === 'failed') {
            throw new Error(resultData.error || 'Assessment failed')
          } else if (resultData.status === 'processing') {
            // Continue polling
            attempts++
            if (attempts < maxAttempts) {
              // Update progress based on time elapsed
              const progressPercent = Math.min(85, (attempts / maxAttempts) * 85)
              setAssessmentProgress(progressPercent)
              setTimeout(pollResults, 1000)
            } else {
              throw new Error('Assessment timeout - please try again')
            }
          }
        } catch (pollError) {
          console.error('Polling error:', pollError)
          setError(pollError.message || 'Failed to get assessment results')
          clearInterval(progressInterval)
          setLoading(false)
        }
      }

      // Start polling after a short delay
      setTimeout(pollResults, 2000)
      
    } catch (err) {
      console.error('Assessment error:', err)
      setError(err.message || 'An unexpected error occurred during assessment')
      clearInterval(progressInterval)
      setLoading(false)
    }
  }

  const handleHistorySelect = (historyItem) => {
    setAssessment(historyItem.assessment)
    setShowHistory(false)
    setError(null)
  }

  const clearHistory = () => {
    setAssessmentHistory([])
    localStorage.removeItem('noveltyAssessmentHistory')
  }

  const handleRetry = () => {
    setError(null)
    // Retry with last form data if available
    const lastFormData = JSON.parse(localStorage.getItem('lastNoveltyAssessmentRequest') || '{}')
    if (lastFormData.research_title && lastFormData.research_abstract) {
      handleSubmit(lastFormData)
    }
  }

  return (
    <div className="novelty-assessment-page">
      <div className="assessment-container">
        <div className="page-header">
          <div className="header-content">
            <h1>Novelty Assessment</h1>
            <p className="subtitle">
              Evaluate the novelty and patentability of your research with comprehensive prior art analysis
            </p>
          </div>
          
          {assessmentHistory.length > 0 && (
            <div className="header-actions">
              <button 
                className="btn btn-secondary"
                onClick={() => setShowHistory(!showHistory)}
              >
                {showHistory ? 'Hide History' : `View History (${assessmentHistory.length})`}
              </button>
            </div>
          )}
        </div>

        {showHistory && (
          <div className="assessment-history">
            <div className="history-header">
              <h3>Recent Assessments</h3>
              <button className="btn btn-text" onClick={clearHistory}>
                Clear All
              </button>
            </div>
            <div className="history-list">
              {assessmentHistory.map((item) => (
                <div 
                  key={item.id} 
                  className="history-item"
                  onClick={() => handleHistorySelect(item)}
                >
                  <div className="history-title">{item.title}</div>
                  <div className="history-abstract">{item.abstract}</div>
                  <div className="history-meta">
                    <span className="history-claims">{item.claims} claims</span>
                    <span className="history-date">
                      {new Date(item.timestamp).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="assessment-content">
          <div className="form-section">
            <AssessmentForm onSubmit={handleSubmit} loading={loading} />
          </div>

          {error && (
            <div className="error-section">
              <div className="error-message">
                <div className="error-icon">⚠️</div>
                <div className="error-content">
                  <strong>Assessment Failed</strong>
                  <p>{error}</p>
                  <div className="error-actions">
                    <button 
                      className="btn btn-primary btn-small"
                      onClick={handleRetry}
                    >
                      Retry Assessment
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
                message="Conducting comprehensive novelty assessment..." 
                progress={assessmentProgress}
              />
              <div className="loading-steps">
                <div className={`step ${assessmentProgress > 0 ? 'active' : ''} ${assessmentProgress > 20 ? 'completed' : ''}`}>
                  Searching patent databases
                </div>
                <div className={`step ${assessmentProgress > 20 ? 'active' : ''} ${assessmentProgress > 40 ? 'completed' : ''}`}>
                  Analyzing scientific publications
                </div>
                <div className={`step ${assessmentProgress > 40 ? 'active' : ''} ${assessmentProgress > 60 ? 'completed' : ''}`}>
                  Evaluating claim novelty
                </div>
                <div className={`step ${assessmentProgress > 60 ? 'active' : ''} ${assessmentProgress > 80 ? 'completed' : ''}`}>
                  Assessing patentability
                </div>
                <div className={`step ${assessmentProgress > 80 ? 'active' : ''} ${assessmentProgress >= 100 ? 'completed' : ''}`}>
                  Generating comprehensive report
                </div>
              </div>
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ width: `${assessmentProgress}%` }}
                ></div>
              </div>
              <div className="progress-text">
                {Math.round(assessmentProgress)}% Complete
              </div>
              {currentAssessmentId && (
                <div className="assessment-id">
                  Assessment ID: {currentAssessmentId}
                </div>
              )}
            </div>
          )}

          {assessment && !loading && (
            <div className="results-section">
              <NoveltyReport assessment={assessment} />
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default NoveltyAssessment