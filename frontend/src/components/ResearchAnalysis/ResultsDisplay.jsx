import { BarChart3, Target, Shield, DollarSign, Download, Share2, TrendingUp, FileText, Lightbulb } from 'lucide-react'
import SimilarityCard from './SimilarityCard'
import './ResultsDisplay.css'

function ResultsDisplay({ results, loading }) {
  if (loading) {
    return (
      <div className="results-loading">
        <div className="loading-spinner"></div>
        <p>Analyzing your research...</p>
      </div>
    )
  }

  if (!results) {
    return null
  }

  const {
    overall_assessment,
    trl_assessment,
    market_analysis,
    ip_assessment,
    competitive_landscape,
    regulatory_assessment,
    recommendations,
    similar_patents = [],
    similar_publications = []
  } = results

  return (
    <div className="modern-results-display">
      <div className="results-header">
        <div className="header-content">
          <h2>Analysis Complete</h2>
          <p>Comprehensive patent intelligence and market assessment for your research</p>
        </div>
        <div className="header-actions">
          <button className="modern-btn secondary-btn">
            <Download size={16} />
            Export
          </button>
          <button className="modern-btn secondary-btn">
            <Share2 size={16} />
            Share
          </button>
        </div>
      </div>

      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-icon-section">
            <div className="metric-icon target">
              <Target size={20} />
            </div>
            <div className="metric-trend positive">High</div>
          </div>
          <div className="metric-content">
            <div className="metric-value">
              {overall_assessment?.market_potential_score || 'N/A'}
            </div>
            <div className="metric-label">Market Potential</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon-section">
            <div className="metric-icon chart">
              <BarChart3 size={20} />
            </div>
            <div className="metric-status">Ready</div>
          </div>
          <div className="metric-content">
            <div className="metric-value">
              {trl_assessment?.trl_score || 'N/A'}/9
            </div>
            <div className="metric-label">TRL Score</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon-section">
            <div className="metric-icon shield">
              <Shield size={20} />
            </div>
            <div className="metric-trend positive">Strong</div>
          </div>
          <div className="metric-content">
            <div className="metric-value">
              {ip_assessment?.ip_strength_score || 'N/A'}/10
            </div>
            <div className="metric-label">IP Strength</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon-section">
            <div className="metric-icon dollar">
              <DollarSign size={20} />
            </div>
            <div className="metric-time">Billion USD</div>
          </div>
          <div className="metric-content">
            <div className="metric-value">
              ${market_analysis?.tam_billion_usd || 'N/A'}B
            </div>
            <div className="metric-label">Total Addressable Market</div>
          </div>
        </div>
      </div>

      <div className="content-grid">
        {/* TRL Assessment */}
        {trl_assessment && (
          <div className="content-card">
            <div className="card-header">
              <h3>
                <BarChart3 size={20} />
                Technology Readiness Level
              </h3>
            </div>
            <div className="card-body">
              <div className="trl-display">
                <div className="trl-score-badge">
                  <span className="score">{trl_assessment.trl_score}</span>
                  <span className="max-score">/9</span>
                </div>
                <div className="trl-details">
                  <div className="detail-item">
                    <span className="detail-label">Category</span>
                    <span className="detail-value">{trl_assessment.trl_category}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Description</span>
                    <span className="detail-value">{trl_assessment.trl_description}</span>
                  </div>
                  {trl_assessment.next_steps && (
                    <div className="detail-item">
                      <span className="detail-label">Next Steps</span>
                      <span className="detail-value">{trl_assessment.next_steps}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Market Analysis */}
        {market_analysis && (
          <div className="content-card">
            <div className="card-header">
              <h3>
                <TrendingUp size={20} />
                Market Analysis
              </h3>
            </div>
            <div className="card-body">
              <div className="market-size-grid">
                <div className="size-card">
                  <div className="size-label">TAM</div>
                  <div className="size-value">${market_analysis.tam_billion_usd}B</div>
                </div>
                <div className="size-card">
                  <div className="size-label">SAM</div>
                  <div className="size-value">${market_analysis.sam_billion_usd}B</div>
                </div>
                <div className="size-card">
                  <div className="size-label">SOM</div>
                  <div className="size-value">${market_analysis.som_billion_usd}B</div>
                </div>
              </div>
              <div className="market-details">
                {market_analysis.domain && (
                  <div className="detail-item">
                    <span className="detail-label">Domain</span>
                    <span className="detail-value">{market_analysis.domain}</span>
                  </div>
                )}
                {market_analysis.cagr_percent && (
                  <div className="detail-item">
                    <span className="detail-label">CAGR</span>
                    <span className="detail-value">{market_analysis.cagr_percent}%</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Competitive Landscape */}
        {competitive_landscape && (
          <div className="content-card">
            <div className="card-header">
              <h3>
                <Target size={20} />
                Competitive Landscape
              </h3>
            </div>
            <div className="card-body">
              <div className="competitive-details">
                <div className="detail-item">
                  <span className="detail-label">Intensity</span>
                  <span className="detail-value">{competitive_landscape.competitive_intensity}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Position</span>
                  <span className="detail-value">{competitive_landscape.competitive_positioning}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Competing Documents</span>
                  <span className="detail-value">{competitive_landscape.total_competing_documents}</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* IP Assessment */}
        {ip_assessment && (
          <div className="content-card">
            <div className="card-header">
              <h3>
                <Shield size={20} />
                IP Strength Assessment
              </h3>
            </div>
            <div className="card-body">
              <div className="ip-details">
                <div className="detail-item">
                  <span className="detail-label">Score</span>
                  <span className="detail-value">{ip_assessment.ip_strength_score}/10</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Patent Count</span>
                  <span className="detail-value">{ip_assessment.patent_count}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">FTO Risk</span>
                  <span className="detail-value">{ip_assessment.fto_risk}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Quality</span>
                  <span className="detail-value">{ip_assessment.ip_quality}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Recommendation</span>
                  <span className="detail-value">{ip_assessment.recommendation}</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Recommendations */}
        {recommendations && recommendations.length > 0 && (
          <div className="content-card">
            <div className="card-header">
              <h3>
                <Lightbulb size={20} />
                Recommendations
              </h3>
            </div>
            <div className="card-body">
              <div className="recommendations-list">
                {recommendations.map((rec, index) => (
                  <div key={index} className="recommendation-item">
                    <div className="recommendation-bullet" />
                    <span className="recommendation-text">{rec}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Similar Patents */}
        {similar_patents.length > 0 && (
          <div className="content-card full-width">
            <div className="card-header">
              <h3>
                <FileText size={20} />
                Similar Patents ({similar_patents.length})
              </h3>
            </div>
            <div className="card-body">
              <div className="similarity-grid">
                {similar_patents.slice(0, 10).map((patent, index) => (
                  <SimilarityCard
                    key={index}
                    document={patent}
                    type="patent"
                  />
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Similar Publications */}
        {similar_publications.length > 0 && (
          <div className="content-card full-width">
            <div className="card-header">
              <h3>
                <FileText size={20} />
                Similar Publications ({similar_publications.length})
              </h3>
            </div>
            <div className="card-body">
              <div className="similarity-grid">
                {similar_publications.slice(0, 10).map((publication, index) => (
                  <SimilarityCard
                    key={index}
                    document={publication}
                    type="publication"
                  />
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default ResultsDisplay