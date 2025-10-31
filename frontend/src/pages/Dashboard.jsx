import { 
  Microscope, 
  TrendingUp, 
  Bell, 
  ClipboardList,
  FileText,
  Settings,
  BarChart3,
  Activity,
  Users,
  Target,
  ArrowUpRight,
  ArrowRight
} from 'lucide-react'
import './Dashboard.css'

function Dashboard() {
  return (
    <div className="dashboard-page">
      <div className="dashboard-container">
        <div className="dashboard-header">
          <h1>Analytics Dashboard</h1>
          <p>Comprehensive insights and analytics for technology transfer decisions</p>
        </div>

        <div className="dashboard-content">
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-icon">
                <Microscope size={28} />
              </div>
              <div className="stat-content">
                <div className="stat-value">24</div>
                <div className="stat-label">Analyses Completed</div>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">
                <BarChart3 size={28} />
              </div>
              <div className="stat-content">
                <div className="stat-value">8.5</div>
                <div className="stat-label">Avg Market Score</div>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">
                <Bell size={28} />
              </div>
              <div className="stat-content">
                <div className="stat-value">12</div>
                <div className="stat-label">Active Alerts</div>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">
                <ClipboardList size={28} />
              </div>
              <div className="stat-content">
                <div className="stat-value">6</div>
                <div className="stat-label">Reports Generated</div>
              </div>
            </div>
          </div>

          <div className="dashboard-grid">
            <div className="dashboard-card">
              <div className="card-header">
                <h3>Recent Analyses</h3>
                <button className="btn btn-text">View All</button>
              </div>
              <div className="card-content">
                <div className="analysis-item">
                  <div className="analysis-info">
                    <div className="analysis-title">Machine Learning Algorithm</div>
                    <div className="analysis-date">2 hours ago</div>
                  </div>
                  <div className="analysis-score">8.5</div>
                </div>
                <div className="analysis-item">
                  <div className="analysis-info">
                    <div className="analysis-title">Quantum Computing Research</div>
                    <div className="analysis-date">1 day ago</div>
                  </div>
                  <div className="analysis-score">9.2</div>
                </div>
                <div className="analysis-item">
                  <div className="analysis-info">
                    <div className="analysis-title">Biomedical Device Innovation</div>
                    <div className="analysis-date">3 days ago</div>
                  </div>
                  <div className="analysis-score">7.8</div>
                </div>
              </div>
            </div>

            <div className="dashboard-card">
              <div className="card-header">
                <h3>Market Trends</h3>
                <button className="btn btn-text">Details</button>
              </div>
              <div className="card-content">
                <div className="trend-item">
                  <div className="trend-info">
                    <div className="trend-title">AI & Machine Learning</div>
                    <div className="trend-growth">+15.3% CAGR</div>
                  </div>
                  <div className="trend-indicator up">
                    <TrendingUp size={20} />
                  </div>
                </div>
                <div className="trend-item">
                  <div className="trend-info">
                    <div className="trend-title">Quantum Technologies</div>
                    <div className="trend-growth">+22.1% CAGR</div>
                  </div>
                  <div className="trend-indicator up">
                    <TrendingUp size={20} />
                  </div>
                </div>
                <div className="trend-item">
                  <div className="trend-info">
                    <div className="trend-title">Biotechnology</div>
                    <div className="trend-growth">+12.8% CAGR</div>
                  </div>
                  <div className="trend-indicator up">
                    <TrendingUp size={20} />
                  </div>
                </div>
              </div>
            </div>

            <div className="dashboard-card">
              <div className="card-header">
                <h3>Patent Alerts</h3>
                <button className="btn btn-text">Manage</button>
              </div>
              <div className="card-content">
                <div className="alert-item">
                  <div className="alert-icon">
                    <Bell size={18} />
                  </div>
                  <div className="alert-info">
                    <div className="alert-title">New patent in ML domain</div>
                    <div className="alert-date">Today</div>
                  </div>
                </div>
                <div className="alert-item">
                  <div className="alert-icon">
                    <Activity size={18} />
                  </div>
                  <div className="alert-info">
                    <div className="alert-title">Similar research published</div>
                    <div className="alert-date">Yesterday</div>
                  </div>
                </div>
                <div className="alert-item">
                  <div className="alert-icon">
                    <FileText size={18} />
                  </div>
                  <div className="alert-info">
                    <div className="alert-title">Patent application filed</div>
                    <div className="alert-date">2 days ago</div>
                  </div>
                </div>
              </div>
            </div>

            <div className="dashboard-card">
              <div className="card-header">
                <h3>Quick Actions</h3>
              </div>
              <div className="card-content">
                <div className="actions-grid">
                  <a href="/analysis" className="action-item">
                    <div className="action-icon">
                      <Microscope size={24} />
                    </div>
                    <div className="action-label">New Analysis</div>
                  </a>
                  <a href="/reports" className="action-item">
                    <div className="action-icon">
                      <ClipboardList size={24} />
                    </div>
                    <div className="action-label">Generate Report</div>
                  </a>
                  <a href="/alerts" className="action-item">
                    <div className="action-icon">
                      <Bell size={24} />
                    </div>
                    <div className="action-label">Setup Alerts</div>
                  </a>
                  <a href="/patents" className="action-item">
                    <div className="action-icon">
                      <FileText size={24} />
                    </div>
                    <div className="action-label">Search Patents</div>
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