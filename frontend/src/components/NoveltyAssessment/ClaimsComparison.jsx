import { useState, useMemo } from 'react'
import './ClaimsComparison.css'

function ClaimsComparison({ claimAnalysis = {}, priorArt = [] }) {
  const [selectedClaim, setSelectedClaim] = useState(0)
  const [comparisonMode, setComparisonMode] = useState('overview')
  const [selectedPriorArt, setSelectedPriorArt] = useState(null)

  // Extract claims from analysis or create default structure
  const claims = useMemo(() => {
    if (claimAnalysis.individual_claim_analysis) {
      return claimAnalysis.individual_claim_analysis.map((analysis, index) => ({
        index,
        text: analysis.claim_text || `Claim ${index + 1}`,
        noveltyScore: analysis.novelty_score || 0,
        conflicts: analysis.potential_conflicts || [],
        recommendations: analysis.recommendations || [],
        similarityBreakdown: analysis.similarity_breakdown || {}
      }))
    }
    
    // Fallback if no claim analysis available
    return []
  }, [claimAnalysis])

  // Process prior art for comparison
  const processedPriorArt = useMemo(() => {
    return priorArt.map(item => ({
      ...item,
      type: item.type || (item.patent_number ? 'patent' : 'publication'),
      title: item.title || item.patent_title || item.publication_title || 'Untitled',
      similarity: item.similarity_score || item.similarity || 0,
      claims: item.claims || [],
      abstract: item.abstract || item.patent_abstract || item.publication_abstract || ''
    }))
  }, [priorArt])

  const getNoveltyColor = (score) => {
    if (score >= 0.8) return '#10b981' // green - high novelty
    if (score >= 0.6) return '#f59e0b' // amber - medium novelty
    return '#ef4444' // red - low novelty
  }

  const getConflictRiskColor = (riskLevel) => {
    switch (riskLevel?.toLowerCase()) {
      case 'low': return '#10b981'
      case 'medium': return '#f59e0b'
      case 'high': return '#ef4444'
      default: return '#6b7280'
    }
  }

  const handleClaimComparison = async (claimIndex, priorArtItem) => {
    setSelectedClaim(claimIndex)
    setSelectedPriorArt(priorArtItem)
    setComparisonMode('detailed')
    
    // Here you could make an API call to get detailed claim comparison
    // For now, we'll use the existing data
  }

  if (!claims.length && !priorArt.length) {
    return (
      <div className="claims-comparison">
        <div className="no-data">
          <div className="no-data-icon">📝</div>
          <h4>No Claims Analysis Available</h4>
          <p>Claims analysis will be available once the novelty assessment is complete.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="claims-comparison">
      <div className="comparison-header">
        <h3>Claims Analysis & Comparison</h3>
        <div className="mode-selector">
          <button
            className={`mode-btn ${comparisonMode === 'overview' ? 'active' : ''}`}
            onClick={() => setComparisonMode('overview')}
          >
            📊 Overview
          </button>
          <button
            className={`mode-btn ${comparisonMode === 'detailed' ? 'active' : ''}`}
            onClick={() => setComparisonMode('detailed')}
          >
            🔍 Detailed Comparison
          </button>
        </div>
      </div>

      {comparisonMode === 'overview' ? (
        <div className="overview-mode">
          {/* Claims Summary */}
          {claims.length > 0 && (
            <div className="claims-summary">
              <h4>Research Claims Summary</h4>
              <div className="claims-grid">
                {claims.map((claim, index) => (
                  <div key={index} className="claim-card">
                    <div className="claim-header">
                      <div className="claim-number">Claim {index + 1}</div>
                      <div 
                        className="novelty-score"
                        style={{ color: getNoveltyColor(claim.noveltyScore) }}
                      >
                        {Math.round(claim.noveltyScore * 100)}% Novel
                      </div>
                    </div>
                    
                    <div className="claim-content">
                      <p className="claim-text">{claim.text}</p>
                      
                      {claim.conflicts.length > 0 && (
                        <div className="conflicts-summary">
                          <strong>Potential Conflicts:</strong>
                          <ul>
                            {claim.conflicts.slice(0, 2).map((conflict, idx) => (
                              <li key={idx}>
                                <span className="conflict-source">{conflict.source}</span>
                                <span 
                                  className="conflict-risk"
                                  style={{ color: getConflictRiskColor(conflict.risk_level) }}
                                >
                                  {conflict.risk_level} Risk
                                </span>
                              </li>
                            ))}
                            {claim.conflicts.length > 2 && (
                              <li className="more-conflicts">
                                +{claim.conflicts.length - 2} more conflicts
                              </li>
                            )}
                          </ul>
                        </div>
                      )}
                      
                      <div className="claim-actions">
                        <button
                          className="btn btn-small btn-secondary"
                          onClick={() => {
                            setSelectedClaim(index)
                            setComparisonMode('detailed')
                          }}
                        >
                          🔍 Analyze Claim
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Overall Analysis Summary */}
          {claimAnalysis.overall_claim_assessment && (
            <div className="overall-assessment">
              <h4>Overall Claims Assessment</h4>
              <div className="assessment-content">
                <div className="assessment-metrics">
                  <div className="metric">
                    <div className="metric-label">Average Novelty</div>
                    <div 
                      className="metric-value"
                      style={{ color: getNoveltyColor(claimAnalysis.overall_claim_assessment.average_novelty_score || 0) }}
                    >
                      {Math.round((claimAnalysis.overall_claim_assessment.average_novelty_score || 0) * 100)}%
                    </div>
                  </div>
                  <div className="metric">
                    <div className="metric-label">High Risk Claims</div>
                    <div className="metric-value">
                      {claimAnalysis.overall_claim_assessment.high_risk_claims || 0}
                    </div>
                  </div>
                  <div className="metric">
                    <div className="metric-label">Recommended Actions</div>
                    <div className="metric-value">
                      {claimAnalysis.overall_claim_assessment.recommended_actions?.length || 0}
                    </div>
                  </div>
                </div>
                
                {claimAnalysis.overall_claim_assessment.summary && (
                  <div className="assessment-summary-text">
                    <p>{claimAnalysis.overall_claim_assessment.summary}</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Top Conflicting Prior Art */}
          {processedPriorArt.length > 0 && (
            <div className="top-conflicts">
              <h4>Top Conflicting Prior Art</h4>
              <div className="conflicts-list">
                {processedPriorArt
                  .filter(item => item.similarity >= 0.6)
                  .sort((a, b) => b.similarity - a.similarity)
                  .slice(0, 5)
                  .map((item, index) => (
                    <div key={index} className="conflict-item">
                      <div className="conflict-header">
                        <div className="conflict-title">
                          <span className={`type-badge ${item.type}`}>
                            {item.type === 'patent' ? '📄' : '📚'}
                          </span>
                          {item.title}
                        </div>
                        <div 
                          className="similarity-score"
                          style={{ color: getConflictRiskColor(item.similarity >= 0.8 ? 'high' : 'medium') }}
                        >
                          {Math.round(item.similarity * 100)}% Similar
                        </div>
                      </div>
                      <div className="conflict-actions">
                        <button
                          className="btn btn-small btn-secondary"
                          onClick={() => handleClaimComparison(0, item)}
                        >
                          🔍 Compare Claims
                        </button>
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="detailed-mode">
          <div className="comparison-layout">
            {/* Claims Panel */}
            <div className="claims-panel">
              <h4>Research Claims</h4>
              <div className="claims-list">
                {claims.map((claim, index) => (
                  <div
                    key={index}
                    className={`claim-item ${selectedClaim === index ? 'selected' : ''}`}
                    onClick={() => setSelectedClaim(index)}
                  >
                    <div className="claim-header">
                      <span className="claim-number">Claim {index + 1}</span>
                      <span 
                        className="novelty-indicator"
                        style={{ backgroundColor: getNoveltyColor(claim.noveltyScore) }}
                      >
                        {Math.round(claim.noveltyScore * 100)}%
                      </span>
                    </div>
                    <p className="claim-preview">
                      {claim.text.length > 100 ? claim.text.substring(0, 100) + '...' : claim.text}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            {/* Comparison Panel */}
            <div className="comparison-panel">
              {selectedClaim !== null && claims[selectedClaim] && (
                <div className="selected-claim-analysis">
                  <h4>Claim {selectedClaim + 1} Analysis</h4>
                  
                  <div className="claim-full-text">
                    <h5>Full Claim Text</h5>
                    <p>{claims[selectedClaim].text}</p>
                  </div>

                  <div className="novelty-analysis">
                    <h5>Novelty Assessment</h5>
                    <div className="novelty-details">
                      <div className="novelty-score-display">
                        <div 
                          className="score-circle"
                          style={{ borderColor: getNoveltyColor(claims[selectedClaim].noveltyScore) }}
                        >
                          <span style={{ color: getNoveltyColor(claims[selectedClaim].noveltyScore) }}>
                            {Math.round(claims[selectedClaim].noveltyScore * 100)}%
                          </span>
                        </div>
                        <div className="score-label">Novelty Score</div>
                      </div>
                      
                      {claims[selectedClaim].similarityBreakdown && (
                        <div className="similarity-breakdown">
                          <h6>Similarity Breakdown</h6>
                          {Object.entries(claims[selectedClaim].similarityBreakdown).map(([aspect, score]) => (
                            <div key={aspect} className="breakdown-item">
                              <span className="aspect-name">{aspect}</span>
                              <div className="aspect-bar">
                                <div 
                                  className="aspect-fill"
                                  style={{ 
                                    width: `${score * 100}%`,
                                    backgroundColor: getNoveltyColor(1 - score) // Invert for similarity
                                  }}
                                ></div>
                              </div>
                              <span className="aspect-score">{Math.round(score * 100)}%</span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>

                  {claims[selectedClaim].conflicts.length > 0 && (
                    <div className="conflicts-analysis">
                      <h5>Potential Conflicts</h5>
                      <div className="conflicts-detailed">
                        {claims[selectedClaim].conflicts.map((conflict, idx) => (
                          <div key={idx} className="conflict-detail">
                            <div className="conflict-info">
                              <div className="conflict-source-title">{conflict.source}</div>
                              <div 
                                className="conflict-risk-badge"
                                style={{ backgroundColor: getConflictRiskColor(conflict.risk_level) }}
                              >
                                {conflict.risk_level} Risk
                              </div>
                            </div>
                            {conflict.conflicting_text && (
                              <div className="conflicting-text">
                                <strong>Conflicting Text:</strong>
                                <p>"{conflict.conflicting_text}"</p>
                              </div>
                            )}
                            {conflict.explanation && (
                              <div className="conflict-explanation">
                                <strong>Explanation:</strong>
                                <p>{conflict.explanation}</p>
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {claims[selectedClaim].recommendations.length > 0 && (
                    <div className="claim-recommendations">
                      <h5>Recommendations</h5>
                      <ul>
                        {claims[selectedClaim].recommendations.map((rec, idx) => (
                          <li key={idx}>{rec}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ClaimsComparison