import { useState } from 'react'
import { 
  Play, 
  Pause, 
  Edit, 
  Trash2, 
  MoreVertical, 
  Calendar, 
  Target,
  TrendingUp,
  AlertCircle
} from 'lucide-react'
import './AlertsList.css'

function AlertsList({ alerts, onUpdateAlert, onDeleteAlert }) {
  const [expandedAlert, setExpandedAlert] = useState(null)
  const [actionMenuOpen, setActionMenuOpen] = useState(null)

  const handleToggleStatus = async (alertId, currentStatus) => {
    const newStatus = currentStatus === 'active' ? 'paused' : 'active'
    await onUpdateAlert(alertId, { status: newStatus })
  }

  const handleDelete = async (alertId) => {
    if (window.confirm('Are you sure you want to delete this alert? This action cannot be undone.')) {
      await onDeleteAlert(alertId)
    }
    setActionMenuOpen(null)
  }

  const formatDate = (date) => {
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    }).format(new Date(date))
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return '#10b981'
      case 'paused':
        return '#f59e0b'
      default:
        return '#64748b'
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active':
        return <Play size={16} />
      case 'paused':
        return <Pause size={16} />
      default:
        return <AlertCircle size={16} />
    }
  }

  if (alerts.length === 0) {
    return (
      <div className="alerts-empty">
        <div className="empty-icon">
          <AlertCircle size={48} />
        </div>
        <h3>No alerts found</h3>
        <p>Create your first patent alert to start monitoring new patents in your field.</p>
      </div>
    )
  }

  return (
    <div className="alerts-list">
      {alerts.map((alert) => (
        <div key={alert.id} className="alert-card">
          <div className="alert-header">
            <div className="alert-title-section">
              <div className="alert-status-indicator">
                <div 
                  className="status-dot"
                  style={{ backgroundColor: getStatusColor(alert.status) }}
                />
                <span className="status-text" style={{ color: getStatusColor(alert.status) }}>
                  {getStatusIcon(alert.status)}
                  {alert.status.charAt(0).toUpperCase() + alert.status.slice(1)}
                </span>
              </div>
              <h3 className="alert-name">{alert.name}</h3>
            </div>
            
            <div className="alert-actions">
              <button
                className={`toggle-btn ${alert.status === 'active' ? 'pause' : 'play'}`}
                onClick={() => handleToggleStatus(alert.id, alert.status)}
                title={alert.status === 'active' ? 'Pause Alert' : 'Activate Alert'}
              >
                {alert.status === 'active' ? <Pause size={18} /> : <Play size={18} />}
              </button>
              
              <div className="action-menu-container">
                <button
                  className="action-menu-btn"
                  onClick={() => setActionMenuOpen(actionMenuOpen === alert.id ? null : alert.id)}
                >
                  <MoreVertical size={18} />
                </button>
                
                {actionMenuOpen === alert.id && (
                  <div className="action-menu">
                    <button className="action-item">
                      <Edit size={16} />
                      Edit Alert
                    </button>
                    <button 
                      className="action-item danger"
                      onClick={() => handleDelete(alert.id)}
                    >
                      <Trash2 size={16} />
                      Delete Alert
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="alert-content">
            <div className="alert-keywords">
              <strong>Keywords:</strong>
              <div className="keywords-list">
                {alert.keywords.map((keyword, index) => (
                  <span key={index} className="keyword-tag">
                    {keyword}
                  </span>
                ))}
              </div>
            </div>

            <div className="alert-metrics">
              <div className="metric">
                <Target size={16} />
                <span>Threshold: {(alert.similarityThreshold * 100).toFixed(0)}%</span>
              </div>
              <div className="metric">
                <TrendingUp size={16} />
                <span>{alert.notificationCount} notifications</span>
              </div>
              <div className="metric">
                <Calendar size={16} />
                <span>Created: {formatDate(alert.createdAt)}</span>
              </div>
            </div>

            {alert.lastTriggered && (
              <div className="alert-last-triggered">
                <span className="last-triggered-label">Last triggered:</span>
                <span className="last-triggered-date">
                  {formatDate(alert.lastTriggered)}
                </span>
              </div>
            )}
          </div>

          <div className="alert-footer">
            <button
              className="expand-btn"
              onClick={() => setExpandedAlert(expandedAlert === alert.id ? null : alert.id)}
            >
              {expandedAlert === alert.id ? 'Show Less' : 'Show Details'}
            </button>
          </div>

          {expandedAlert === alert.id && (
            <div className="alert-expanded">
              <div className="expanded-section">
                <h4>Alert Configuration</h4>
                <div className="config-grid">
                  <div className="config-item">
                    <label>Similarity Threshold</label>
                    <div className="threshold-bar">
                      <div 
                        className="threshold-fill"
                        style={{ width: `${alert.similarityThreshold * 100}%` }}
                      />
                      <span className="threshold-value">
                        {(alert.similarityThreshold * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                  <div className="config-item">
                    <label>Notification Frequency</label>
                    <span>Real-time</span>
                  </div>
                  <div className="config-item">
                    <label>Patent Sources</label>
                    <span>USPTO, EPO, WIPO</span>
                  </div>
                </div>
              </div>

              <div className="expanded-section">
                <h4>Recent Activity</h4>
                <div className="activity-timeline">
                  <div className="activity-item">
                    <div className="activity-dot" />
                    <div className="activity-content">
                      <span className="activity-text">Alert created</span>
                      <span className="activity-date">{formatDate(alert.createdAt)}</span>
                    </div>
                  </div>
                  {alert.lastTriggered && (
                    <div className="activity-item">
                      <div className="activity-dot active" />
                      <div className="activity-content">
                        <span className="activity-text">Last notification sent</span>
                        <span className="activity-date">{formatDate(alert.lastTriggered)}</span>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  )
}

export default AlertsList