import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import AnalysisForm from '../AnalysisForm'

describe('AnalysisForm', () => {
  const mockOnSubmit = jest.fn()

  beforeEach(() => {
    mockOnSubmit.mockClear()
  })

  test('renders form fields correctly', () => {
    render(<AnalysisForm onSubmit={mockOnSubmit} loading={false} />)
    
    expect(screen.getByLabelText(/research title/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/research abstract/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /analyze research/i })).toBeInTheDocument()
  })

  test('shows character counts', () => {
    render(<AnalysisForm onSubmit={mockOnSubmit} loading={false} />)
    
    expect(screen.getByText('0/500 characters')).toBeInTheDocument()
    expect(screen.getByText('0/5000 characters')).toBeInTheDocument()
  })

  test('updates character counts when typing', async () => {
    const user = userEvent.setup()
    render(<AnalysisForm onSubmit={mockOnSubmit} loading={false} />)
    
    const titleInput = screen.getByLabelText(/research title/i)
    await user.type(titleInput, 'Test Title')
    
    expect(screen.getByText('10/500 characters')).toBeInTheDocument()
  })

  test('validates required fields', async () => {
    const user = userEvent.setup()
    render(<AnalysisForm onSubmit={mockOnSubmit} loading={false} />)
    
    const submitButton = screen.getByRole('button', { name: /analyze research/i })
    await user.click(submitButton)
    
    // After clicking submit, the form should mark fields as touched and show errors
    await waitFor(() => {
      expect(screen.getByText('⚠️ Title is required')).toBeInTheDocument()
      expect(screen.getByText('⚠️ Abstract is required')).toBeInTheDocument()
    })
    expect(mockOnSubmit).not.toHaveBeenCalled()
  })

  test('validates minimum length', async () => {
    const user = userEvent.setup()
    render(<AnalysisForm onSubmit={mockOnSubmit} loading={false} />)
    
    const titleInput = screen.getByLabelText(/research title/i)
    const abstractInput = screen.getByLabelText(/research abstract/i)
    
    await user.type(titleInput, 'AI')
    await user.type(abstractInput, 'Short abstract')
    
    const submitButton = screen.getByRole('button', { name: /analyze research/i })
    await user.click(submitButton)
    
    expect(screen.getByText('⚠️ Title must be at least 5 characters long')).toBeInTheDocument()
    expect(screen.getByText('⚠️ Abstract must be at least 20 characters long')).toBeInTheDocument()
    expect(mockOnSubmit).not.toHaveBeenCalled()
  })

  test('submits valid form data', async () => {
    const user = userEvent.setup()
    render(<AnalysisForm onSubmit={mockOnSubmit} loading={false} />)
    
    const titleInput = screen.getByLabelText(/research title/i)
    const abstractInput = screen.getByLabelText(/research abstract/i)
    
    const validTitle = 'Machine Learning Algorithm'
    const validAbstract = 'This is a valid abstract with sufficient length for testing purposes.'
    
    await user.type(titleInput, validTitle)
    await user.type(abstractInput, validAbstract)
    
    const submitButton = screen.getByRole('button', { name: /analyze research/i })
    await user.click(submitButton)
    
    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith({
        title: validTitle,
        abstract: validAbstract
      })
    })
  })

  test('disables form when loading', () => {
    render(<AnalysisForm onSubmit={mockOnSubmit} loading={true} />)
    
    const titleInput = screen.getByLabelText(/research title/i)
    const abstractInput = screen.getByLabelText(/research abstract/i)
    const submitButton = screen.getByRole('button', { name: /analyzing.../i })
    
    expect(titleInput).toBeDisabled()
    expect(abstractInput).toBeDisabled()
    expect(submitButton).toBeDisabled()
  })
})