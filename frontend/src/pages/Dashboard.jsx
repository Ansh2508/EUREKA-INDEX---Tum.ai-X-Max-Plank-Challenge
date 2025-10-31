import {
  Microscope,
  TrendingUp,
  Bell,
  ClipboardList,
  FileText,
  BarChart3,
  Activity,
  ArrowUpRight,
  Calendar,
  Clock,
  ChevronRight,
  Brain,
  Zap
} from 'lucide-react'

import './Dashboard.css'

function Dashboard() {
  return (
    <div className="dashboard-page">
      <div className="dashboard-container">
        <div className="dashboard-header">
          <div className="header-content">
            <h1>Dashboard</h1>
            <p>Monitor your technology transfer analytics and insights</p>
          </div>
          <div className="header-actions">
            <button className="btn btn-secondary">
              <Calendar size={16} />
              Last 30 days
            </button>
            <button className="btn btn-primary">
              <Microscope size={16} />
              New Analysis
            </button>
          </div>
        </div>

        <div className="dashboard-content">
          <div className="metrics-grid">
            <div className="metric-card">
              <div className="metric-header">
                <div className="metric-icon microscope">
                  <Microscope size={20} />
                </div>
                <div className="metric-trend positive">
                  <ArrowUpRight size={16} />
                  12%
                </div>
              </div>
              <div className="metric-value">24</div>
              <div className="metric-label">Analyses Completed</div>
            </div>

            <div className="metric-card">
              <div className="metric-header">
                <div className="metric-icon chart">
                  <BarChart3 size={20} />
                </div>
                <div className="metric-trend positive">
                  <ArrowUpRight size={16} />
                  8%
                </div>
              </div>
              <div className="metric-value">8.5</div>
              <div className="metric-label">Average Market Score</div>
            </div>

            <div className="metric-card">
              <div className="metric-header">
                <div className="metric-icon alert">
                  <Bell size={20} />
                </div>
                <div className="metric-status">
                  <div className="status-dot active"></div>
                  Active
                </div>
              </div>
              <div className="metric-value">12</div>
              <div className="metric-label">Patent Alerts</div>
            </div>

            <div className="metric-card">
              <div className="metric-header">
                <div className="metric-icon report">
                  <ClipboardList size={20} />
                </div>
                <div className="metric-time">
                  <Clock size={14} />
                  Today
                </div>
              </div>
              <div className="metric-value">6</div>
              <div className="metric-label">Reports Generated</div>
            </div>
          </div>

          <div className="content-grid">


            <div className="content-card">
              <div className="card-header">
                <h3>Recent Analyses</h3>
                <button className="btn-link">
                  View All
                  <ChevronRight size={16} />
                </button>
              </div>
              <div className="card-body">
                <div className="list-item">
                  <div className="item-content">
                    <div className="item-title">Machine Learning Algorithm</div>
                    <div className="item-subtitle">2 hours ago • AI Enhanced</div>
                  </div>
                  <div className="score-badge high">8.5</div>
                </div>
                <div className="list-item">
                  <div className="item-content">
                    <div className="item-title">Quantum Computing Research</div>
                    <div className="item-subtitle">1 day ago • AI Enhanced</div>
                  </div>
                  <div className="score-badge excellent">9.2</div>
                </div>
                <div className="list-item">
                  <div className="item-content">
                    <div className="item-title">Biomedical Device Innovation</div>
                    <div className="item-subtitle">3 days ago • AI Enhanced</div>
                  </div>
                  <div className="score-badge good">7.8</div>
                </div>
              </div>
            </div>

            <div className="content-card">
              <div className="card-header">
                <h3>Market Trends</h3>
                <button className="btn-link">
                  Details
                  <ChevronRight size={16} />
                </button>
              </div>
              <div className="card-body">
                <div className="trend-item">
                  <div className="trend-content">
                    <div className="trend-title">AI & Machine Learning</div>
                    <div className="trend-growth positive">+15.3% CAGR</div>
                  </div>
                  <div className="trend-chart">
                    <TrendingUp size={18} />
                  </div>
                </div>
                <div className="trend-item">
                  <div className="trend-content">
                    <div className="trend-title">Quantum Technologies</div>
                    <div className="trend-growth positive">+22.1% CAGR</div>
                  </div>
                  <div className="trend-chart">
                    <TrendingUp size={18} />
                  </div>
                </div>
                <div className="trend-item">
                  <div className="trend-content">
                    <div className="trend-title">Biotechnology</div>
                    <div className="trend-growth positive">+12.8% CAGR</div>
                  </div>
                  <div className="trend-chart">
                    <TrendingUp size={18} />
                  </div>
                </div>
              </div>
            </div>

            <div className="content-card">
              <div className="card-header">
                <h3>Recent Alerts</h3>
                <button className="btn-link">
                  Manage
                  <ChevronRight size={16} />
                </button>
              </div>
              <div className="card-body">
                <div className="alert-item">
                  <div className="alert-indicator new">
                    <Bell size={16} />
                  </div>
                  <div className="alert-content">
                    <div className="alert-title">New patent in ML domain</div>
                    <div className="alert-time">Today</div>
                  </div>
                </div>
                <div className="alert-item">
                  <div className="alert-indicator activity">
                    <Activity size={16} />
                  </div>
                  <div className="alert-content">
                    <div className="alert-title">Similar research published</div>
                    <div className="alert-time">Yesterday</div>
                  </div>
                </div>
                <div className="alert-item">
                  <div className="alert-indicator document">
                    <FileText size={16} />
                  </div>
                  <div className="alert-content">
                    <div className="alert-title">Patent application filed</div>
                    <div className="alert-time">2 days ago</div>
                  </div>
                </div>
              </div>
            </div>

            <div className="content-card">
              <div className="card-header">
                <h3>Quick Actions</h3>
              </div>
              <div className="card-body">
                <div className="actions-grid">
                  <a href="/analysis" className="action-card">
                    <div className="action-icon microscope">
                      <Microscope size={20} />
                    </div>
                    <div className="action-text">
                      <div className="action-title">New Analysis</div>
                      <div className="action-description">Start technology assessment</div>
                    </div>
                  </a>
                  <a href="/reports" className="action-card">
                    <div className="action-icon report">
                      <ClipboardList size={20} />
                    </div>
                    <div className="action-text">
                      <div className="action-title">Generate Report</div>
                      <div className="action-description">Create detailed insights</div>
                    </div>
                  </a>
                  <a href="/alerts" className="action-card">
                    <div className="action-icon alert">
                      <Bell size={20} />
                    </div>
                    <div className="action-text">
                      <div className="action-title">Setup Alerts</div>
                      <div className="action-description">Monitor patent activity</div>
                    </div>
                  </a>
                  <a href="/patents" className="action-card">
                    <div className="action-icon document">
                      <FileText size={20} />
                    </div>
                    <div className="action-text">
                      <div className="action-title">Search Patents</div>
                      <div className="action-description">Explore patent database</div>
                    </div>
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard