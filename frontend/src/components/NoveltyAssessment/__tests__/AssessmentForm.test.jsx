import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import AssessmentForm from '../AssessmentForm'

describe('AssessmentForm', () => {
  const mockOnSubmit = jest.fn()

  beforeEach(() => {
    mockOnSubmit.mockClear()
  })

  test('renders form with all required fields', () => {
    render(<AssessmentForm onSubmit={mockOnSubmit} loading={false} />)
    
    expect(screen.getByLabelText(/research title/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/research abstract/i)).toBeInTheDocument()
    expect(screen.getByText(/research claims/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /assess novelty/i })).toBeInTheDocument()
  })

  test('validates required fields', async () => {
    const user = userEvent.setup()
    render(<AssessmentForm onSubmit={mockOnSubmit} loading={false} />)
    
    const submitButton = screen.getByRole('button', { name: /assess novelty/i })
    
    // Try to submit empty form
    await user.click(submitButton)
    
    expect(mockOnSubmit).not.toHaveBeenCalled()
    expect(screen.getByText(/title is required/i)).toBeInTheDocument()
    expect(screen.getByText(/abstract is required/i)).toBeInTheDocument()
  })

  test('validates minimum field lengths', async () => {
    const user = userEvent.setup()
    render(<AssessmentForm onSubmit={mockOnSubmit} loading={false} />)
    
    const titleInput = screen.getByLabelText(/research title/i)
    const abstractInput = screen.getByLabelText(/research abstract/i)
    
    // Enter text that's too short
    await user.type(titleInput, 'Hi')
    await user.type(abstractInput, 'Short abstract')
    await user.tab() // Trigger blur events
    
    await waitFor(() => {
      expect(screen.getByText(/title must be at least 5 characters/i)).toBeInTheDocument()
      expect(screen.getByText(/abstract must be at least 50 characters/i)).toBeInTheDocument()
    })
  })

  test('allows adding and removing claims', async () => {
    const user = userEvent.setup()
    render(<AssessmentForm onSubmit={mockOnSubmit} loading={false} />)
    
    // Initially should have one claim input
    expect(screen.getAllByText(/claim \d+:/)).toHaveLength(1)
    
    // Add another claim
    const addButton = screen.getByRole('button', { name: /add another claim/i })
    await user.click(addButton)
    
    expect(screen.getAllByText(/claim \d+:/)).toHaveLength(2)
    
    // Remove a claim (should have remove button now)
    const removeButtons = screen.getAllByTitle(/remove this claim/i)
    expect(removeButtons).toHaveLength(1) // Only second claim should have remove button
    
    await user.click(removeButtons[0])
    expect(screen.getAllByText(/claim \d+:/)).toHaveLength(1)
  })

  test('submits form with valid data', async () => {
    const user = userEvent.setup()
    render(<AssessmentForm onSubmit={mockOnSubmit} loading={false} />)
    
    const titleInput = screen.getByLabelText(/research title/i)
    const abstractInput = screen.getByLabelText(/research abstract/i)
    const claimInput = screen.getByPlaceholderText(/claim 1:/i)
    
    // Fill in valid data
    await user.type(titleInput, 'Novel Machine Learning Algorithm')
    await user.type(abstractInput, 'This is a detailed abstract describing a novel machine learning algorithm for medical image analysis. It includes comprehensive methodology and results.')
    await user.type(claimInput, 'A machine learning algorithm that processes medical images with high accuracy')
    
    const submitButton = screen.getByRole('button', { name: /assess novelty/i })
    await user.click(submitButton)
    
    expect(mockOnSubmit).toHaveBeenCalledWith({
      research_title: 'Novel Machine Learning Algorithm',
      research_abstract: 'This is a detailed abstract describing a novel machine learning algorithm for medical image analysis. It includes comprehensive methodology and results.',
      claims: ['A machine learning algorithm that processes medical images with high accuracy']
    })
  })

  test('disables form when loading', () => {
    render(<AssessmentForm onSubmit={mockOnSubmit} loading={true} />)
    
    const titleInput = screen.getByLabelText(/research title/i)
    const abstractInput = screen.getByLabelText(/research abstract/i)
    const submitButton = screen.getByRole('button', { name: /assessing novelty/i })
    
    expect(titleInput).toBeDisabled()
    expect(abstractInput).toBeDisabled()
    expect(submitButton).toBeDisabled()
  })

  test('shows character count for inputs', async () => {
    const user = userEvent.setup()
    render(<AssessmentForm onSubmit={mockOnSubmit} loading={false} />)
    
    const titleInput = screen.getByLabelText(/research title/i)
    
    await user.type(titleInput, 'Test title')
    
    expect(screen.getByText('10/500 characters')).toBeInTheDocument()
  })

  test('clears form when clear button is clicked', async () => {
    const user = userEvent.setup()
    render(<AssessmentForm onSubmit={mockOnSubmit} loading={false} />)
    
    const titleInput = screen.getByLabelText(/research title/i)
    const abstractInput = screen.getByLabelText(/research abstract/i)
    
    // Fill in some data
    await user.type(titleInput, 'Test title')
    await user.type(abstractInput, 'Test abstract')
    
    // Clear the form
    const clearButton = screen.getByRole('button', { name: /clear form/i })
    await user.click(clearButton)
    
    expect(titleInput.value).toBe('')
    expect(abstractInput.value).toBe('')
  })
})