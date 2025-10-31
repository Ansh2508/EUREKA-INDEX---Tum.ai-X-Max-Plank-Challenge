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
  User,
  Search,
  Sparkles,
  Info
} from 'lucide-react'
import './Sidebar.css'

function Sidebar({ collapsed = false, mobileOpen = false, onCollapsedChange, onMobileToggle }) {
  const location = useLocation()

  const toggleSidebar = () => {
    if (onCollapsedChange) {
      onCollapsedChange(!collapsed)
    }
  }

  // Add subtle hover effect for better UX
  const handleNavItemHover = (e) => {
    if (!collapsed) return
    const tooltip = e.currentTarget.getAttribute('title')
    if (tooltip) {
      e.currentTarget.style.setProperty('--tooltip-content', `"${tooltip}"`)
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
      path: '/novelty',
      icon: Search,
      label: 'Novelty',
      description: 'Novelty Assessment'
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
    },
    {
      path: '/about',
      icon: Info,
      label: 'About',
      description: 'Project Information'
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
                  title={collapsed ? `${item.label} - ${item.description}` : ''}
                  onClick={handleLinkClick}
                  onMouseEnter={handleNavItemHover}
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
                <Sparkles size={20} />
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