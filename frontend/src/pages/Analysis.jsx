import { useState } from 'react'
import './Analysis.css'

function Analysis() {
  const [title, setTitle] = useState('')
  const [abstract, setAbstract] = useState('')
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResults(null)

    try {
      const response = await fetch('http://localhost:8000/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ title, abstract }),
      })

      if (!response.ok) {
        throw new Error('Analysis failed')
      }

      const data = await response.json()
      setResults(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="analysis-page">
      <div className="analysis-container">
        <h1>Technology Transfer Analysis</h1>
        <p className="subtitle">
          Enter your research details to get comprehensive patent and market analysis
        </p>

        <form onSubmit={handleSubmit} className="analysis-form">
          <div className="form-group">
            <label htmlFor="title">Research Title *</label>
            <input
              type="text"
              id="title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Enter your research title"
              required
              minLength={5}
              maxLength={500}
            />
          </div>

          <div className="form-group">
            <label htmlFor="abstract">Research Abstract *</label>
            <textarea
              id="abstract"
              value={abstract}
              onChange={(e) => setAbstract(e.target.value)}
              placeholder="Enter your research abstract (minimum 20 characters)"
              required
              minLength={20}
              maxLength={5000}
              rows={8}
            />
          </div>

          <button 
            type="submit" 
            className="btn btn-primary btn-large"
            disabled={loading}
          >
            {loading ? 'Analyzing...' : 'Analyze Research'}
          </button>
        </form>

        {error && (
          <div className="error-message">
            <strong>Error:</strong> {error}
          </div>
        )}

        {results && (
          <div className="results">
            <h2>Analysis Results</h2>
            
            <div className="result-section">
              <h3>Technology Readiness Level (TRL)</h3>
              <div className="trl-score">
                <span className="score">{results.trl_score}</span>
                <span className="label">/ 9</span>
              </div>
              <p>{results.trl_description}</p>
            </div>

            <div className="result-section">
              <h3>Novelty Assessment</h3>
              <div className="novelty-score">
                Score: {results.novelty_score}/10
              </div>
              <p>{results.novelty_assessment}</p>
            </div>

            <div className="result-section">
              <h3>Market Potential</h3>
              <div className="market-metrics">
                <div className="metric">
                  <span className="metric-label">TAM</span>
                  <span className="metric-value">{results.market_size?.tam || 'N/A'}</span>
                </div>
                <div className="metric">
                  <span className="metric-label">SAM</span>
                  <span className="metric-value">{results.market_size?.sam || 'N/A'}</span>
                </div>
                <div className="metric">
                  <span className="metric-label">SOM</span>
                  <span className="metric-value">{results.market_size?.som || 'N/A'}</span>
                </div>
              </div>
            </div>

            <div className="result-section">
              <h3>IP Strength</h3>
              <p>Score: {results.ip_strength_score}/10</p>
              <p>{results.ip_strength_assessment}</p>
            </div>

            <div className="result-section">
              <h3>Recommendations</h3>
              <ul>
                {results.recommendations?.map((rec, index) => (
                  <li key={index}>{rec}</li>
                ))}
              </ul>
            </div>

            {results.similar_patents && results.similar_patents.length > 0 && (
              <div className="result-section">
                <h3>Similar Patents</h3>
                <div className="patents-list">
                  {results.similar_patents.slice(0, 5).map((patent, index) => (
                    <div key={index} className="patent-card">
                      <h4>{patent.title}</h4>
                      <p className="patent-meta">
                        {patent.assignee} | {patent.publication_date}
                      </p>
                      <p className="patent-abstract">{patent.abstract?.substring(0, 200)}...</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default Analysis

