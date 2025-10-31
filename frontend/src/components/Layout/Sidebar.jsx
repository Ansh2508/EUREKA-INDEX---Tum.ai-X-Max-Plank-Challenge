import { Link, useLocation } from 'react-router-dom'
import { 
  LayoutDashboard, 
  Microscope, 
  FileText, 
  Bell, 
  ClipboardList, 
  Settings,
  ChevronLeft,
  ChevronRight,
  Bot,
  User
} from 'lucide-react'
import './Sidebar.css'

function Sidebar({ collapsed = false, mobileOpen = false, onCollapsedChange, onMobileToggle }) {
  const location = useLocation()

  const toggleSidebar = () => {
    if (onCollapsedChange) {
      onCollapsedChange(!collapsed)
    }
  }

  const menuItems = [
    {
      path: '/dashboard',
      icon: LayoutDashboard,
      label: 'Dashboard',
      description: 'Analytics Dashboard'
    },
    {
      path: '/analysis',
      icon: Microscope,
      label: 'Analysis',
      description: 'Research Analysis'
    },
    {
      path: '/patents',
      icon: FileText,
      label: 'Patents',
      description: 'Patent Search'
    },
    {
      path: '/alerts',
      icon: Bell,
      label: 'Alerts',
      description: 'Patent Alerts'
    },
    {
      path: '/reports',
      icon: ClipboardList,
      label: 'Reports',
      description: 'Analysis Reports'
    },
    {
      path: '/settings',
      icon: Settings,
      label: 'Settings',
      description: 'App Settings'
    }
  ]

  const handleLinkClick = () => {
    if (onMobileToggle) {
      onMobileToggle(false)
    }
  }

  return (
    <aside className={`sidebar ${collapsed ? 'collapsed' : ''} ${mobileOpen ? 'mobile-open' : ''}`}>
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <img src="/favicon.svg" alt="EUREKA INDEX" className="logo-icon" />
          {!collapsed && <span className="logo-text">EUREKA INDEX</span>}
        </div>
        <button 
          className="sidebar-toggle"
          onClick={toggleSidebar}
          aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
        </button>
      </div>

      <nav className="sidebar-nav">
        <ul className="nav-menu">
          {menuItems.map((item) => {
            const IconComponent = item.icon
            return (
              <li key={item.path} className="nav-item">
                <Link 
                  to={item.path}
                  className={`nav-link ${location.pathname === item.path ? 'active' : ''}`}
                  title={collapsed ? item.label : ''}
                  onClick={handleLinkClick}
                >
                  <span className="nav-icon">
                    <IconComponent size={20} />
                  </span>
                  {!collapsed && (
                    <div className="nav-content">
                      <span className="nav-label">{item.label}</span>
                      <span className="nav-description">{item.description}</span>
                    </div>
                  )}
                </Link>
              </li>
            )
          })}
        </ul>
      </nav>

      <div className="sidebar-footer">
        {!collapsed && (
          <div className="sidebar-info">
            <div className="info-item">
              <span className="info-icon">
                <Bot size={20} />
              </span>
              <div className="info-content">
                <span className="info-label">AI-Powered</span>
                <span className="info-description">Patent Intelligence</span>
              </div>
            </div>
          </div>
        )}
        
        <div className="sidebar-user">
          <div className="user-avatar">
            <span className="avatar-icon">
              <User size={18} />
            </span>
          </div>
          {!collapsed && (
            <div className="user-info">
              <span className="user-name">Research User</span>
              <span className="user-role">Analyst</span>
            </div>
          )}
        </div>
      </div>
    </aside>
  )
}

export default Sidebar