import { useState } from 'react'
import PriorArtTable from './PriorArtTable'
import ClaimsComparison from './ClaimsComparison'
import './NoveltyReport.css'

function NoveltyReport({ assessment, loading }) {
  const [activeTab, setActiveTab] = useState('overview')
  const [showFullReport, setShowFullReport] = useState(false)

  if (loading) {
    return (
      <div className="report-loading">
        <div className="loading-spinner"></div>
        <p>Generating novelty assessment report...</p>
      </div>
    )
  }

  if (!assessment) {
    return null
  }

  const {
    overall_novelty_score,
    novelty_category,
    patentability_indicators,
    prior_art_analysis,
    claim_analysis,
    recommendations,
    detailed_analysis,
    similar_patents = [],
    similar_publications = []
  } = assessment

  const getScoreColor = (score) => {
    if (score >= 0.8) return '#10b981' // green
    if (score >= 0.6) return '#f59e0b' // amber
    return '#ef4444' // red
  }

  const getNoveltyLevel = (score) => {
    if (score >= 0.8) return 'High'
    if (score >= 0.6) return 'Medium'
    return 'Low'
  }

  const getPatentabilityColor = (likelihood) => {
    if (likelihood === 'High') return '#10b981'
    if (likelihood === 'Medium') return '#f59e0b'
    return '#ef4444'
  }

  return (
    <div className="novelty-report">
      <div className="report-header">
        <div className="header-content">
          <h2 className="report-title">🔍 Novelty Assessment Report</h2>
          <div className="report-actions">
            <button className="btn btn-secondary">
              <span>📥</span> Export PDF
            </button>
            <button className="btn btn-secondary">
              <span>📤</span> Share Report
            </button>
            <button 
              className="btn btn-primary"
              onClick={() => setShowFullReport(!showFullReport)}
            >
              <span>📊</span> {showFullReport ? 'Summary View' : 'Detailed Report'}
            </button>
          </div>
        </div>
      </div>

      {/* Key Metrics Overview */}
      <div className="metrics-overview">
        <div className="metric-card novelty-score">
          <div className="metric-icon">🎯</div>
          <div className="metric-content">
            <div 
              className="metric-value"
              style={{ color: getScoreColor(overall_novelty_score) }}
            >
              {Math.round(overall_novelty_score * 100)}%
            </div>
            <div className="metric-label">Novelty Score</div>
            <div className="metric-sublabel">{novelty_category}</div>
          </div>
        </div>
        
        <div className="metric-card patentability">
          <div className="metric-icon">⚖️</div>
          <div className="metric-content">
            <div 
              className="metric-value"
              style={{ color: getPatentabilityColor(patentability_indicators?.patentability_likelihood) }}
            >
              {patentability_indicators?.patentability_likelihood || 'Unknown'}
            </div>
            <div className="metric-label">Patentability</div>
            <div className="metric-sublabel">Likelihood</div>
          </div>
        </div>
        
        <div className="metric-card prior-art">
          <div className="metric-icon">📚</div>
          <div className="metric-content">
            <div className="metric-value">
              {(similar_patents.length + similar_publications.length)}
            </div>
            <div className="metric-label">Prior Art Found</div>
            <div className="metric-sublabel">
              {similar_patents.length} patents, {similar_publications.length} publications
            </div>
          </div>
        </div>
        
        <div className="metric-card conflicts">
          <div className="metric-icon">⚠️</div>
          <div className="metric-content">
            <div className="metric-value">
              {patentability_indicators?.prior_art_conflicts || 0}
            </div>
            <div className="metric-label">Conflicts</div>
            <div className="metric-sublabel">High similarity items</div>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="report-tabs">
        <button 
          className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          📊 Overview
        </button>
        <button 
          className={`tab-button ${activeTab === 'prior-art' ? 'active' : ''}`}
          onClick={() => setActiveTab('prior-art')}
        >
          📚 Prior Art
        </button>
        <button 
          className={`tab-button ${activeTab === 'claims' ? 'active' : ''}`}
          onClick={() => setActiveTab('claims')}
        >
          📝 Claims Analysis
        </button>
        <button 
          className={`tab-button ${activeTab === 'recommendations' ? 'active' : ''}`}
          onClick={() => setActiveTab('recommendations')}
        >
          💡 Recommendations
        </button>
      </div>

      {/* Tab Content */}
      <div className="tab-content">
        {activeTab === 'overview' && (
          <div className="overview-tab">
            <div className="assessment-summary">
              <h3>Assessment Summary</h3>
              <div className="summary-grid">
                <div className="summary-item">
                  <div className="summary-label">Overall Novelty</div>
                  <div className="summary-value">
                    <div className="novelty-bar">
                      <div 
                        className="novelty-fill"
                        style={{ 
                          width: `${overall_novelty_score * 100}%`,
                          backgroundColor: getScoreColor(overall_novelty_score)
                        }}
                      ></div>
                    </div>
                    <span className="novelty-text">
                      {getNoveltyLevel(overall_novelty_score)} Novelty ({Math.round(overall_novelty_score * 100)}%)
                    </span>
                  </div>
                </div>

                {patentability_indicators && (
                  <>
                    <div className="summary-item">
                      <div className="summary-label">Patentability Assessment</div>
                      <div className="summary-value">
                        <span 
                          className="patentability-badge"
                          style={{ backgroundColor: getPatentabilityColor(patentability_indicators.patentability_likelihood) }}
                        >
                          {patentability_indicators.patentability_likelihood} Likelihood
                        </span>
                      </div>
                    </div>

                    {patentability_indicators.key_differentiators && (
                      <div className="summary-item full-width">
                        <div className="summary-label">Key Differentiators</div>
                        <div className="summary-value">
                          <ul className="differentiators-list">
                            {patentability_indicators.key_differentiators.map((diff, index) => (
                              <li key={index}>{diff}</li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    )}
                  </>
                )}
              </div>
            </div>

            {prior_art_analysis && (
              <div className="prior-art-summary">
                <h3>Prior Art Analysis</h3>
                <div className="analysis-content">
                  <p><strong>Analysis Summary:</strong> {prior_art_analysis.analysis_summary}</p>
                  {prior_art_analysis.key_findings && (
                    <div className="key-findings">
                      <strong>Key Findings:</strong>
                      <ul>
                        {prior_art_analysis.key_findings.map((finding, index) => (
                          <li key={index}>{finding}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            )}

            {showFullReport && detailed_analysis && (
              <div className="detailed-analysis">
                <h3>Detailed AI Analysis</h3>
                <div className="analysis-content">
                  <div dangerouslySetInnerHTML={{ __html: detailed_analysis }} />
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'prior-art' && (
          <div className="prior-art-tab">
            <PriorArtTable 
              patents={similar_patents}
              publications={similar_publications}
            />
          </div>
        )}

        {activeTab === 'claims' && (
          <div className="claims-tab">
            <ClaimsComparison 
              claimAnalysis={claim_analysis}
              priorArt={[...similar_patents, ...similar_publications]}
            />
          </div>
        )}

        {activeTab === 'recommendations' && (
          <div className="recommendations-tab">
            <div className="recommendations-section">
              <h3>Strategic Recommendations</h3>
              {recommendations && recommendations.length > 0 ? (
                <div className="recommendations-list">
                  {recommendations.map((rec, index) => (
                    <div key={index} className="recommendation-item">
                      <div className="recommendation-icon">💡</div>
                      <div className="recommendation-content">
                        <p>{rec}</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="no-recommendations">
                  <p>No specific recommendations available for this assessment.</p>
                </div>
              )}
            </div>

            <div className="next-steps-section">
              <h3>Suggested Next Steps</h3>
              <div className="next-steps-list">
                <div className="step-item">
                  <div className="step-number">1</div>
                  <div className="step-content">
                    <h4>Review Prior Art</h4>
                    <p>Carefully examine the identified prior art to understand potential conflicts and opportunities for differentiation.</p>
                  </div>
                </div>
                <div className="step-item">
                  <div className="step-number">2</div>
                  <div className="step-content">
                    <h4>Refine Claims</h4>
                    <p>Based on the analysis, consider refining your claims to emphasize novel aspects and avoid conflicts.</p>
                  </div>
                </div>
                <div className="step-item">
                  <div className="step-number">3</div>
                  <div className="step-content">
                    <h4>Consult Patent Attorney</h4>
                    <p>Discuss the assessment results with a qualified patent attorney for professional guidance on filing strategy.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default NoveltyReport