import { useState, useEffect } from 'react'
import { Bell, Plus, Settings, Filter, Search, TrendingUp } from 'lucide-react'
import AlertsList from '../components/PatentAlerts/AlertsList'
import CreateAlertModal from '../components/PatentAlerts/CreateAlertModal'
import NotificationPanel from '../components/PatentAlerts/NotificationPanel'
import LoadingSpinner from '../components/UI/LoadingSpinner'
import alertService from '../services/alertService'
import './PatentAlerts.css'

function PatentAlerts() {
  const [alerts, setAlerts] = useState([])
  const [notifications, setNotifications] = useState([])
  const [loading, setLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterStatus, setFilterStatus] = useState('all')
  const [stats, setStats] = useState({
    totalAlerts: 0,
    activeAlerts: 0,
    recentNotifications: 0,
    weeklyTrend: 0
  })

  // Real API calls using alertService
  useEffect(() => {
    fetchAlerts()
    fetchNotifications()
    fetchStats()

    // Set up polling for real-time updates
    const interval = setInterval(() => {
      fetchNotifications()
      fetchStats()
    }, 30000) // Poll every 30 seconds

    return () => clearInterval(interval)
  }, [])

  const fetchAlerts = async () => {
    try {
      setLoading(true)
      const backendAlerts = await alertService.getAlerts()
      const transformedAlerts = backendAlerts.map(alert => alertService.transformAlert(alert))
      setAlerts(transformedAlerts)
    } catch (error) {
      console.error('Error fetching alerts:', error)
      // Fallback to empty array on error
      setAlerts([])
    } finally {
      setLoading(false)
    }
  }

  const fetchNotifications = async () => {
    try {
      const backendNotifications = await alertService.getNotifications()
      const transformedNotifications = backendNotifications.map(notification =>
        alertService.transformNotification(notification)
      )

      // Enrich notifications with alert names
      const enrichedNotifications = transformedNotifications.map(notification => {
        const alert = alerts.find(a => a.id === notification.alertId)
        return {
          ...notification,
          alertName: alert ? alert.name : `Alert ${notification.alertId}`
        }
      })

      setNotifications(enrichedNotifications)
    } catch (error) {
      console.error('Error fetching notifications:', error)
      // Fallback to empty array on error
      setNotifications([])
    }
  }

  const fetchStats = async () => {
    try {
      const backendStats = await alertService.getAlertStats()
      setStats({
        totalAlerts: backendStats.total_alerts,
        activeAlerts: backendStats.active_alerts,
        recentNotifications: backendStats.unread_notifications,
        weeklyTrend: 15.3 // This would need to be calculated on backend
      })
    } catch (error) {
      console.error('Error fetching stats:', error)
      // Fallback to default stats on error
      setStats({
        totalAlerts: 0,
        activeAlerts: 0,
        recentNotifications: 0,
        weeklyTrend: 0
      })
    }
  }

  const handleCreateAlert = async (alertData) => {
    try {
      const backendAlert = await alertService.createAlert(alertData)
      const transformedAlert = alertService.transformAlert(backendAlert)

      setAlerts(prev => [transformedAlert, ...prev])
      setShowCreateModal(false)

      // Refresh stats
      await fetchStats()
    } catch (error) {
      console.error('Error creating alert:', error)
      // You might want to show a user-friendly error message here
      alert('Failed to create alert: ' + error.message)
    }
  }

  const handleUpdateAlert = async (alertId, updates) => {
    try {
      const backendAlert = await alertService.updateAlert(alertId, updates)
      const transformedAlert = alertService.transformAlert(backendAlert)

      setAlerts(prev => prev.map(alert =>
        alert.id === alertId ? transformedAlert : alert
      ))

      // Update stats if status changed
      if (updates.status) {
        await fetchStats()
      }
    } catch (error) {
      console.error('Error updating alert:', error)
      alert('Failed to update alert: ' + error.message)
    }
  }

  const handleDeleteAlert = async (alertId) => {
    try {
      await alertService.deleteAlert(alertId)

      setAlerts(prev => prev.filter(alert => alert.id !== alertId))

      // Refresh stats
      await fetchStats()
    } catch (error) {
      console.error('Error deleting alert:', error)
      alert('Failed to delete alert: ' + error.message)
    }
  }

  const handleMarkNotificationRead = async (notificationId) => {
    try {
      await alertService.markNotificationRead(notificationId)

      setNotifications(prev => prev.map(notification =>
        notification.id === notificationId
          ? { ...notification, read: true }
          : notification
      ))

      // Refresh stats to update unread count
      await fetchStats()
    } catch (error) {
      console.error('Error marking notification as read:', error)
      alert('Failed to mark notification as read: ' + error.message)
    }
  }

  const filteredAlerts = alerts.filter(alert => {
    const matchesSearch = alert.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      alert.keywords.some(keyword =>
        keyword.toLowerCase().includes(searchTerm.toLowerCase())
      )
    const matchesFilter = filterStatus === 'all' || alert.status === filterStatus
    return matchesSearch && matchesFilter
  })

  if (loading) {
    return (
      <div className="patent-alerts-page">
        <LoadingSpinner size="large" message="Loading patent alerts..." />
      </div>
    )
  }

  return (
    <div className="patent-alerts-page">
      <div className="alerts-container">
        {/* Header */}
        <div className="alerts-header">
          <div className="header-content">
            <div className="header-title">
              <div className="header-badge">
                <Bell size={16} />
                <span>Patent Intelligence System</span>
              </div>
              <h1>Patent Alerts Dashboard</h1>
              <p>Monitor new patents and stay ahead of the competition with intelligent alerts</p>
            </div>
            <div className="header-actions">
              <button
                className="btn btn-primary"
                onClick={() => setShowCreateModal(true)}
              >
                <Plus size={20} />
                Create Alert
              </button>
              <button className="btn btn-secondary">
                <Settings size={20} />
                Settings
              </button>
            </div>
          </div>
        </div>

        {/* Stats Dashboard */}
        <div className="stats-section">
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-icon">
                <Bell size={24} />
              </div>
              <div className="stat-content">
                <div className="stat-value">{stats.totalAlerts}</div>
                <div className="stat-label">Total Alerts</div>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon active">
                <TrendingUp size={24} />
              </div>
              <div className="stat-content">
                <div className="stat-value">{stats.activeAlerts}</div>
                <div className="stat-label">Active Alerts</div>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon notification">
                <Bell size={24} />
              </div>
              <div className="stat-content">
                <div className="stat-value">{stats.recentNotifications}</div>
                <div className="stat-label">New Notifications</div>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon trend">
                <TrendingUp size={24} />
              </div>
              <div className="stat-content">
                <div className="stat-value">+{stats.weeklyTrend}%</div>
                <div className="stat-label">Weekly Growth</div>
              </div>
            </div>
          </div>

        </div>

        {/* Main Content */}
        <div className="main-content-section">
          <div className="alerts-content">
            <div className="alerts-main">
              {/* Search and Filter Controls */}
              <div className="alerts-controls">
                <div className="search-box">
                  <Search size={20} />
                  <input
                    type="text"
                    placeholder="Search alerts by name or keywords..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </div>
                <div className="filter-controls">
                  <select
                    value={filterStatus}
                    onChange={(e) => setFilterStatus(e.target.value)}
                    className="filter-select"
                  >
                    <option value="all">All Alerts</option>
                    <option value="active">Active</option>
                    <option value="paused">Paused</option>
                  </select>
                  <button className="btn btn-secondary">
                    <Filter size={18} />
                    More Filters
                  </button>
                </div>
              </div>

              {/* Alerts List */}
              <AlertsList
                alerts={filteredAlerts}
                onUpdateAlert={handleUpdateAlert}
                onDeleteAlert={handleDeleteAlert}
              />
            </div>

            {/* Notifications Panel */}
            <div className="alerts-sidebar">
              <NotificationPanel
                notifications={notifications}
                onMarkAsRead={handleMarkNotificationRead}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Create Alert Modal */}
      {showCreateModal && (
        <CreateAlertModal
          onClose={() => setShowCreateModal(false)}
          onSubmit={handleCreateAlert}
        />
      )}
    </div>
  )
}

export default PatentAlerts