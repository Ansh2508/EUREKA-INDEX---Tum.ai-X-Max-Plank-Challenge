import { useState } from 'react'
import { 
  Bell, 
  BellOff, 
  ExternalLink, 
  Clock, 
  TrendingUp,
  Filter,
  MoreVertical,
  Check,
  Eye
} from 'lucide-react'
import './NotificationPanel.css'

function NotificationPanel({ notifications, onMarkAsRead }) {
  const [filter, setFilter] = useState('all') // all, unread, read
  const [sortBy, setSortBy] = useState('newest') // newest, oldest, similarity

  const formatTimeAgo = (date) => {
    const now = new Date()
    const diffInMinutes = Math.floor((now - new Date(date)) / (1000 * 60))
    
    if (diffInMinutes < 1) return 'Just now'
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`
    
    const diffInHours = Math.floor(diffInMinutes / 60)
    if (diffInHours < 24) return `${diffInHours}h ago`
    
    const diffInDays = Math.floor(diffInHours / 24)
    if (diffInDays < 7) return `${diffInDays}d ago`
    
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric'
    }).format(new Date(date))
  }

  const getSimilarityColor = (score) => {
    if (score >= 0.9) return '#10b981' // green
    if (score >= 0.8) return '#f59e0b' // amber
    if (score >= 0.7) return '#ef4444' // red
    return '#64748b' // gray
  }

  const getSimilarityLabel = (score) => {
    if (score >= 0.9) return 'Very High'
    if (score >= 0.8) return 'High'
    if (score >= 0.7) return 'Medium'
    return 'Low'
  }

  const filteredNotifications = notifications
    .filter(notification => {
      if (filter === 'unread') return !notification.read
      if (filter === 'read') return notification.read
      return true
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'oldest':
          return new Date(a.timestamp) - new Date(b.timestamp)
        case 'similarity':
          return b.similarityScore - a.similarityScore
        case 'newest':
        default:
          return new Date(b.timestamp) - new Date(a.timestamp)
      }
    })

  const unreadCount = notifications.filter(n => !n.read).length

  const handleMarkAsRead = (notificationId, event) => {
    event.stopPropagation()
    onMarkAsRead(notificationId)
  }

  const handleMarkAllAsRead = () => {
    const unreadNotifications = notifications.filter(n => !n.read)
    unreadNotifications.forEach(notification => {
      onMarkAsRead(notification.id)
    })
  }

  return (
    <div className="notification-panel">
      <div className="panel-header">
        <div className="header-title">
          <Bell size={20} />
          <h3>Recent Alerts</h3>
          {unreadCount > 0 && (
            <span className="unread-badge">{unreadCount}</span>
          )}
        </div>
        
        <div className="header-actions">
          {unreadCount > 0 && (
            <button 
              className="mark-all-read-btn"
              onClick={handleMarkAllAsRead}
              title="Mark all as read"
            >
              <Check size={16} />
            </button>
          )}
        </div>
      </div>

      <div className="panel-controls">
        <div className="filter-tabs">
          <button
            className={`filter-tab ${filter === 'all' ? 'active' : ''}`}
            onClick={() => setFilter('all')}
          >
            All ({notifications.length})
          </button>
          <button
            className={`filter-tab ${filter === 'unread' ? 'active' : ''}`}
            onClick={() => setFilter('unread')}
          >
            Unread ({unreadCount})
          </button>
        </div>

        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          className="sort-select"
        >
          <option value="newest">Newest First</option>
          <option value="oldest">Oldest First</option>
          <option value="similarity">By Similarity</option>
        </select>
      </div>

      <div className="notifications-list">
        {filteredNotifications.length === 0 ? (
          <div className="empty-notifications">
            <BellOff size={32} />
            <p>
              {filter === 'unread' 
                ? 'No unread notifications' 
                : 'No notifications yet'
              }
            </p>
          </div>
        ) : (
          filteredNotifications.map((notification) => (
            <div 
              key={notification.id} 
              className={`notification-item ${!notification.read ? 'unread' : ''}`}
            >
              <div className="notification-header">
                <div className="alert-info">
                  <span className="alert-name">{notification.alertName}</span>
                  <span className="notification-time">
                    <Clock size={12} />
                    {formatTimeAgo(notification.timestamp)}
                  </span>
                </div>
                
                {!notification.read && (
                  <button
                    className="mark-read-btn"
                    onClick={(e) => handleMarkAsRead(notification.id, e)}
                    title="Mark as read"
                  >
                    <Eye size={14} />
                  </button>
                )}
              </div>

              <div className="notification-content">
                <h4 className="patent-title">{notification.patentTitle}</h4>
                <div className="patent-info">
                  <span className="patent-id">{notification.patentId}</span>
                  <div 
                    className="similarity-score"
                    style={{ color: getSimilarityColor(notification.similarityScore) }}
                  >
                    <TrendingUp size={14} />
                    {(notification.similarityScore * 100).toFixed(0)}% similarity
                    <span className="similarity-label">
                      ({getSimilarityLabel(notification.similarityScore)})
                    </span>
                  </div>
                </div>
              </div>

              <div className="notification-actions">
                <button className="action-btn primary">
                  <ExternalLink size={14} />
                  View Patent
                </button>
                <button className="action-btn secondary">
                  <MoreVertical size={14} />
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {filteredNotifications.length > 0 && (
        <div className="panel-footer">
          <button className="view-all-btn">
            View All Notifications
            <ExternalLink size={14} />
          </button>
        </div>
      )}
    </div>
  )
}

export default NotificationPanel