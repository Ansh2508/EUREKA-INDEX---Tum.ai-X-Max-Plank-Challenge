import './SimilarityCard.css'

function SimilarityCard({ document, type }) {
  const {
    title,
    score,
    url,
    year,
    citations,
    assignee,
    inventors,
    authors,
    journal,
    abstract
  } = document

  const formatScore = (score) => {
    if (typeof score === 'number') {
      return (score * 100).toFixed(1) + '%'
    }
    return 'N/A'
  }

  const truncateText = (text, maxLength = 200) => {
    if (!text) return 'No abstract available'
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
  }

  const getScoreColor = (score) => {
    if (typeof score !== 'number') return '#6b7280'
    const percentage = score * 100
    if (percentage >= 80) return '#ef4444' // High similarity - red
    if (percentage >= 60) return '#f59e0b' // Medium-high - amber
    if (percentage >= 40) return '#3b82f6' // Medium - blue
    return '#22c55e' // Low similarity - green
  }

  return (
    <div className={`similarity-card ${type}`}>
      <div className="card-header">
        <div className="card-type">
          {type === 'patent' ? '📄 Patent' : '📚 Publication'}
        </div>
        <div 
          className="similarity-score"
          style={{ 
            backgroundColor: `${getScoreColor(score)}20`,
            color: getScoreColor(score),
            border: `1px solid ${getScoreColor(score)}40`
          }}
        >
          {formatScore(score)}
        </div>
      </div>
      
      <div className="card-content">
        <h4 className="card-title">
          {url ? (
            <a href={url} target="_blank" rel="noopener noreferrer">
              {title || 'Untitled'}
            </a>
          ) : (
            title || 'Untitled'
          )}
        </h4>
        
        <div className="card-meta">
          {type === 'patent' ? (
            <>
              {assignee && <span className="meta-item">👤 {assignee}</span>}
              {inventors && inventors.length > 0 && (
                <span className="meta-item">
                  🔬 {inventors.slice(0, 2).join(', ')}
                  {inventors.length > 2 && ` +${inventors.length - 2} more`}
                </span>
              )}
            </>
          ) : (
            <>
              {authors && authors.length > 0 && (
                <span className="meta-item">
                  ✍️ {authors.slice(0, 2).join(', ')}
                  {authors.length > 2 && ` +${authors.length - 2} more`}
                </span>
              )}
              {journal && <span className="meta-item">📖 {journal}</span>}
            </>
          )}
          
          {year && <span className="meta-item">📅 {year}</span>}
          {citations !== undefined && (
            <span className="meta-item">📊 {citations} citations</span>
          )}
        </div>
        
        <p className="card-abstract">
          {truncateText(abstract)}
        </p>
        
        {score && typeof score === 'number' && (
          <div className="similarity-indicator">
            <div className="indicator-label">Similarity</div>
            <div className="indicator-bar">
              <div 
                className="indicator-fill"
                style={{ 
                  width: `${score * 100}%`,
                  backgroundColor: getScoreColor(score)
                }}
              ></div>
            </div>
          </div>
        )}
      </div>
      
      <div className="card-footer">
        <div className="footer-actions">
          {url && (
            <a 
              href={url} 
              target="_blank" 
              rel="noopener noreferrer"
              className="view-link"
            >
              <span className="link-icon">🔗</span>
              View Full Document
            </a>
          )}
          <button className="action-btn" title="Save for later">
            <span>⭐</span>
          </button>
          <button className="action-btn" title="Share">
            <span>📤</span>
          </button>
        </div>
      </div>
    </div>
  )
}

export default SimilarityCard