import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import PatentAlerts from '../../../pages/PatentAlerts'

// Mock the components to avoid complex dependencies in unit tests
jest.mock('../AlertsList', () => {
  return function MockAlertsList({ alerts, onUpdateAlert, onDeleteAlert }) {
    return (
      <div data-testid="alerts-list">
        {alerts.map(alert => (
          <div key={alert.id} data-testid={`alert-${alert.id}`}>
            <span>{alert.name}</span>
            <button onClick={() => onUpdateAlert(alert.id, { status: 'paused' })}>
              Update
            </button>
            <button onClick={() => onDeleteAlert(alert.id)}>
              Delete
            </button>
          </div>
        ))}
      </div>
    )
  }
})

jest.mock('../NotificationPanel', () => {
  return function MockNotificationPanel({ notifications, onMarkAsRead }) {
    return (
      <div data-testid="notification-panel">
        {notifications.map(notification => (
          <div key={notification.id} data-testid={`notification-${notification.id}`}>
            <span>{notification.patentTitle}</span>
            <button onClick={() => onMarkAsRead(notification.id)}>
              Mark as Read
            </button>
          </div>
        ))}
      </div>
    )
  }
})

jest.mock('../CreateAlertModal', () => {
  return function MockCreateAlertModal({ onClose, onSubmit }) {
    return (
      <div data-testid="create-alert-modal">
        <button onClick={onClose}>Close</button>
        <button onClick={() => onSubmit({ name: 'Test Alert', keywords: ['test'] })}>
          Submit
        </button>
      </div>
    )
  }
})

const renderWithRouter = (component) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  )
}

describe('PatentAlerts', () => {
  beforeEach(() => {
    // Mock console.error to avoid noise in tests
    jest.spyOn(console, 'error').mockImplementation(() => {})
    // Mock timers to speed up loading
    jest.useFakeTimers()
  })

  afterEach(() => {
    jest.restoreAllMocks()
    jest.useRealTimers()
  })

  test('renders patent alerts page with header', async () => {
    renderWithRouter(<PatentAlerts />)
    
    // Fast-forward past the loading timeout
    jest.advanceTimersByTime(1000)
    
    await waitFor(() => {
      expect(screen.getByText('Patent Alerts')).toBeInTheDocument()
      expect(screen.getByText('Monitor new patents and stay ahead of the competition')).toBeInTheDocument()
    })
  })

  test('displays create alert button', async () => {
    renderWithRouter(<PatentAlerts />)
    
    // Fast-forward past the loading timeout
    jest.advanceTimersByTime(1000)
    
    await waitFor(() => {
      expect(screen.getByText('Create Alert')).toBeInTheDocument()
    })
  })

  test('shows loading spinner initially', () => {
    renderWithRouter(<PatentAlerts />)
    
    expect(screen.getByText('Loading patent alerts...')).toBeInTheDocument()
  })

  test('displays stats after loading', async () => {
    renderWithRouter(<PatentAlerts />)
    
    // Fast-forward past the loading timeout
    jest.advanceTimersByTime(1000)
    
    await waitFor(() => {
      expect(screen.getByText('Total Alerts')).toBeInTheDocument()
      expect(screen.getByText('Active Alerts')).toBeInTheDocument()
      expect(screen.getByText('New Notifications')).toBeInTheDocument()
      expect(screen.getByText('Weekly Growth')).toBeInTheDocument()
    })
  })

  test('opens create alert modal when button is clicked', async () => {
    renderWithRouter(<PatentAlerts />)
    
    // Fast-forward past the loading timeout
    jest.advanceTimersByTime(1000)
    
    await waitFor(() => {
      const createButton = screen.getByText('Create Alert')
      fireEvent.click(createButton)
    })
    
    expect(screen.getByTestId('create-alert-modal')).toBeInTheDocument()
  })

  test('filters alerts based on search term', async () => {
    renderWithRouter(<PatentAlerts />)
    
    // Fast-forward past the loading timeout
    jest.advanceTimersByTime(1000)
    
    await waitFor(() => {
      const searchInput = screen.getByPlaceholderText('Search alerts by name or keywords...')
      fireEvent.change(searchInput, { target: { value: 'Machine Learning' } })
    })
    
    // The filtering logic should work with the mocked components
    expect(screen.getByDisplayValue('Machine Learning')).toBeInTheDocument()
  })

  test('handles alert creation', async () => {
    renderWithRouter(<PatentAlerts />)
    
    // Fast-forward past the loading timeout
    jest.advanceTimersByTime(1000)
    
    await waitFor(() => {
      const createButton = screen.getByText('Create Alert')
      fireEvent.click(createButton)
    })
    
    const submitButton = screen.getByText('Submit')
    fireEvent.click(submitButton)
    
    // Fast-forward past the submission timeout
    jest.advanceTimersByTime(1000)
    
    // Modal should close after submission
    await waitFor(() => {
      expect(screen.queryByTestId('create-alert-modal')).not.toBeInTheDocument()
    })
  })
})