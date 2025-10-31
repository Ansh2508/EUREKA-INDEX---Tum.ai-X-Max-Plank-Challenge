import './RecentAnalyses.css'

function RecentAnalyses({ analyses, onSelect }) {
    if (analyses.length === 0) {
        return (
            <div className="recent-analyses">
                <div className="empty-state">
                    <div className="empty-icon">📊</div>
                    <h3>No analyses yet</h3>
                    <p>Your analysis history will appear here once you start running analyses.</p>
                </div>
            </div>
        )
    }

    return (
        <div className="recent-analyses">
            <div className="analyses-grid">
                {analyses.map((analysis) => (
                    <div
                        key={analysis.id}
                        className="analysis-card"
                        onClick={() => onSelect(analysis)}
                    >
                        <div className="analysis-header">
                            <h4 className="analysis-title">{analysis.title}</h4>
                            <div className="analysis-date">
                                {new Date(analysis.timestamp).toLocaleDateString()}
                            </div>
                        </div>

                        <div className="analysis-preview">
                            <p className="analysis-abstract">{analysis.abstract}</p>
                        </div>

                        <div className="analysis-metrics">
                            {analysis.results?.overall_assessment?.market_potential_score && (
                                <div className="metric-chip">
                                    <span className="metric-icon">🎯</span>
                                    <span>Market: {analysis.results.overall_assessment.market_potential_score}</span>
                                </div>
                            )}

                            {analysis.results?.trl_assessment?.trl_score && (
                                <div className="metric-chip">
                                    <span className="metric-icon">🔬</span>
                                    <span>TRL: {analysis.results.trl_assessment.trl_score}/9</span>
                                </div>
                            )}

                            {analysis.results?.market_analysis?.tam_billion_usd && (
                                <div className="metric-chip">
                                    <span className="metric-icon">💰</span>
                                    <span>TAM: ${analysis.results.market_analysis.tam_billion_usd}B</span>
                                </div>
                            )}
                        </div>

                        <div className="analysis-footer">
                            <button className="view-btn">
                                <span>👁️</span>
                                View Results
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    )
}

export default RecentAnalyses