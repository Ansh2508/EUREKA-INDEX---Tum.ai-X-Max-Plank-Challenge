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
    <div className="results-display">
      <div className="results-header">
        <h2 className="results-title">📊 Analysis Results</h2>
        <div className="results-actions">
          <button className="btn btn-secondary">
            <span>📥</span> Export Report
          </button>
          <button className="btn btn-secondary">
            <span>📤</span> Share Results
          </button>
        </div>
      </div>
      
      {/* Key Metrics Overview */}
      <div className="metrics-overview">
        <div className="metric-card market-potential">
          <div className="metric-icon">🎯</div>
          <div className="metric-value">
            {overall_assessment?.market_potential_score || 'N/A'}
          </div>
          <div className="metric-label">Market Potential</div>
        </div>
        
        <div className="metric-card trl-score">
          <div className="metric-icon">🔬</div>
          <div className="metric-value">
            {trl_assessment?.trl_score || 'N/A'}/9
          </div>
          <div className="metric-label">TRL Score</div>
        </div>
        
        <div className="metric-card ip-strength">
          <div className="metric-icon">🛡️</div>
          <div className="metric-value">
            {ip_assessment?.ip_strength_score || 'N/A'}/10
          </div>
          <div className="metric-label">IP Strength</div>
        </div>
        
        <div className="metric-card market-size">
          <div className="metric-icon">💰</div>
          <div className="metric-value">
            ${market_analysis?.tam_billion_usd || 'N/A'}B
          </div>
          <div className="metric-label">TAM</div>
        </div>
      </div>

      {/* Detailed Sections */}
      <div className="results-sections">
        
        {/* TRL Assessment */}
        {trl_assessment && (
          <div className="result-section">
            <h3>Technology Readiness Level</h3>
            <div className="trl-display">
              <div className="trl-score">
                <span className="score">{trl_assessment.trl_score}</span>
                <span className="max-score">/9</span>
              </div>
              <div className="trl-details">
                <p><strong>Category:</strong> {trl_assessment.trl_category}</p>
                <p><strong>Description:</strong> {trl_assessment.trl_description}</p>
                {trl_assessment.next_steps && (
                  <p><strong>Next Steps:</strong> {trl_assessment.next_steps}</p>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Market Analysis */}
        {market_analysis && (
          <div className="result-section">
            <h3>Market Analysis</h3>
            <div className="market-metrics">
              <div className="market-size">
                <div className="size-item">
                  <span className="size-label">TAM</span>
                  <span className="size-value">${market_analysis.tam_billion_usd}B</span>
                </div>
                <div className="size-item">
                  <span className="size-label">SAM</span>
                  <span className="size-value">${market_analysis.sam_billion_usd}B</span>
                </div>
                <div className="size-item">
                  <span className="size-label">SOM</span>
                  <span className="size-value">${market_analysis.som_billion_usd}B</span>
                </div>
              </div>
              {market_analysis.domain && (
                <p><strong>Domain:</strong> {market_analysis.domain}</p>
              )}
              {market_analysis.cagr_percent && (
                <p><strong>CAGR:</strong> {market_analysis.cagr_percent}%</p>
              )}
            </div>
          </div>
        )}

        {/* Competitive Landscape */}
        {competitive_landscape && (
          <div className="result-section">
            <h3>Competitive Landscape</h3>
            <div className="competitive-info">
              <p><strong>Intensity:</strong> {competitive_landscape.competitive_intensity}</p>
              <p><strong>Position:</strong> {competitive_landscape.competitive_positioning}</p>
              <p><strong>Total Competing Documents:</strong> {competitive_landscape.total_competing_documents}</p>
            </div>
          </div>
        )}

        {/* IP Assessment */}
        {ip_assessment && (
          <div className="result-section">
            <h3>IP Strength Assessment</h3>
            <div className="ip-info">
              <p><strong>Score:</strong> {ip_assessment.ip_strength_score}/10</p>
              <p><strong>Patent Count:</strong> {ip_assessment.patent_count}</p>
              <p><strong>FTO Risk:</strong> {ip_assessment.fto_risk}</p>
              <p><strong>Quality:</strong> {ip_assessment.ip_quality}</p>
              <p><strong>Recommendation:</strong> {ip_assessment.recommendation}</p>
            </div>
          </div>
        )}

        {/* Recommendations */}
        {recommendations && recommendations.length > 0 && (
          <div className="result-section">
            <h3>Recommendations</h3>
            <ul className="recommendations-list">
              {recommendations.map((rec, index) => (
                <li key={index}>{rec}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Similar Patents */}
        {similar_patents.length > 0 && (
          <div className="result-section">
            <h3>Similar Patents ({similar_patents.length})</h3>
            <div className="similarity-cards">
              {similar_patents.slice(0, 10).map((patent, index) => (
                <SimilarityCard 
                  key={index} 
                  document={patent} 
                  type="patent"
                />
              ))}
            </div>
          </div>
        )}

        {/* Similar Publications */}
        {similar_publications.length > 0 && (
          <div className="result-section">
            <h3>Similar Publications ({similar_publications.length})</h3>
            <div className="similarity-cards">
              {similar_publications.slice(0, 10).map((publication, index) => (
                <SimilarityCard 
                  key={index} 
                  document={publication} 
                  type="publication"
                />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default ResultsDisplay