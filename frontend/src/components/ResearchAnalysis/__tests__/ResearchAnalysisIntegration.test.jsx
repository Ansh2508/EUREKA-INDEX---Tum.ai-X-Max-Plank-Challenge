/**
 * Integration tests for Research Analysis feature
 * Tests the complete user workflow from form submission to results display
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi, beforeEach, afterEach, describe, it, expect } from 'vitest'
import Analysis from '../../pages/Analysis'

// Mock fetch globally
const mockFetch = vi.fn()
global.fetch = mockFetch

// Mock localStorage
const mockLocalStorage = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
global.localStorage = mockLocalStorage

describe('Research Analysis Integration', () => {
  beforeEach(() => {
    // Reset all mocks
    mockFetch.mockReset()
    mockLocalStorage.getItem.mockReset()
    mockLocalStorage.setItem.mockReset()
    mockLocalStorage.removeItem.mockReset()
    
    // Mock localStorage to return empty history initially
    mockLocalStorage.getItem.mockReturnValue(null)
  })

  afterEach(() => {
    vi.clearAllTimers()
  })

  const sampleFormData = {
    title: 'Advanced Machine Learning Algorithm',
    abstract: 'This research presents a novel machine learning algorithm for efficient data processing and pattern recognition in large datasets. The algorithm uses advanced neural network architectures to improve accuracy and reduce computational complexity.'
  }

  const mockAnalysisResponse = {
    id: 'test-analysis-123',
    title: sampleFormData.title,
    abstract: sampleFormData.abstract,
    status: 'pending',
    created_at: '2024-01-01T00:00:00Z'
  }

  const mockResultsResponse = {
    id: 'test-analysis-123',
    title: sampleFormData.title,
    abstract: sampleFormData.abstract,
    status: 'completed',
    results: {
      overall_assessment: {
        market_potential_score: 8.5
      },
      trl_assessment: {
        trl_score: 6,
        trl_category: 'Technology Demonstration',
        trl_description: 'Technology demonstrated in relevant environment'
      },
      market_analysis: {
        tam_billion_usd: 45.2,
        sam_billion_usd: 12.8,
        som_billion_usd: 2.1,
        domain: 'Machine Learning',
        cagr_percent: 15.3
      },
      ip_assessment: {
        ip_strength_score: 7.2,
        patent_count: 15,
        fto_risk: 'Medium',
        ip_quality: 'Good',
        recommendation: 'Consider filing patents'
      },
      competitive_landscape: {
        competitive_intensity: 'High',
        competitive_positioning: 'Strong',
        total_competing_documents: 127
      },
      recommendations: [
        'Consider strengthening IP portfolio',
        'Focus on market differentiation',
        'Explore partnership opportunities'
      ],
      similar_patents: [
        {
          id: 'US123456789',
          title: 'Machine Learning Data Processing System',
          score: 0.85,
          url: 'https://patents.uspto.gov/patent/US123456789',
          year: 2023,
          assignee: 'TechCorp Inc.',
          inventors: ['John Doe', 'Jane Smith'],
          abstract: 'A system for processing large datasets using machine learning algorithms...'
        }
      ],
      similar_publications: [
        {
          id: 'pub-456',
          title: 'Advanced Neural Networks for Pattern Recognition',
          score: 0.78,
          url: 'https://example.com/publication/456',
          year: 2023,
          authors: ['Dr. Alice Johnson', 'Prof. Bob Wilson'],
          journal: 'Journal of Machine Learning',
          abstract: 'This paper presents novel approaches to pattern recognition...'
        }
      ]
    }
  }

  it('should complete the full analysis workflow successfully', async () => {
    const user = userEvent.setup()

    // Mock successful API responses
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockAnalysisResponse
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockResultsResponse
      })

    render(<Analysis />)

    // Step 1: Fill out the form
    const titleInput = screen.getByLabelText(/research title/i)
    const abstractInput = screen.getByLabelText(/research abstract/i)
    const submitButton = screen.getByRole('button', { name: /analyze research/i })

    await user.type(titleInput, sampleFormData.title)
    await user.type(abstractInput, sampleFormData.abstract)

    // Verify form validation
    expect(submitButton).not.toHaveClass('disabled')

    // Step 2: Submit the form
    await user.click(submitButton)

    // Verify loading state
    expect(screen.getByText(/analyzing your research/i)).toBeInTheDocument()
    expect(screen.getByText(/searching patent databases/i)).toBeInTheDocument()

    // Verify API calls
    expect(mockFetch).toHaveBeenCalledWith('/api/research/analyze', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(sampleFormData),
    })

    // Wait for polling to complete
    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith('/api/research/results/test-analysis-123')
    }, { timeout: 3000 })

    // Step 3: Verify results are displayed
    await waitFor(() => {
      expect(screen.getByText(/analysis results/i)).toBeInTheDocument()
    })

    // Verify key metrics are displayed
    expect(screen.getByText('8.5')).toBeInTheDocument() // Market potential score
    expect(screen.getByText('6/9')).toBeInTheDocument() // TRL score
    expect(screen.getByText('$45.2B')).toBeInTheDocument() // TAM

    // Verify similar patents section
    expect(screen.getByText(/similar patents/i)).toBeInTheDocument()
    expect(screen.getByText('Machine Learning Data Processing System')).toBeInTheDocument()

    // Verify similar publications section
    expect(screen.getByText(/similar publications/i)).toBeInTheDocument()
    expect(screen.getByText('Advanced Neural Networks for Pattern Recognition')).toBeInTheDocument()

    // Step 4: Verify history is saved
    expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
      'lastAnalysisRequest',
      JSON.stringify(sampleFormData)
    )
    expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
      'analysisHistory',
      expect.stringContaining(sampleFormData.title)
    )
  })

  it('should handle API errors gracefully', async () => {
    const user = userEvent.setup()

    // Mock API error
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 400,
      json: async () => ({
        detail: {
          errors: ['Title must be at least 5 characters long']
        }
      })
    })

    render(<Analysis />)

    // Fill out form with invalid data
    const titleInput = screen.getByLabelText(/research title/i)
    const abstractInput = screen.getByLabelText(/research abstract/i)
    const submitButton = screen.getByRole('button', { name: /analyze research/i })

    await user.type(titleInput, 'AI') // Too short
    await user.type(abstractInput, sampleFormData.abstract)
    await user.click(submitButton)

    // Wait for error to appear
    await waitFor(() => {
      expect(screen.getByText(/analysis failed/i)).toBeInTheDocument()
    })

    // Verify error message
    expect(screen.getByText(/title must be at least 5 characters long/i)).toBeInTheDocument()

    // Verify retry button is present
    expect(screen.getByRole('button', { name: /retry analysis/i })).toBeInTheDocument()
  })

  it('should handle polling timeout gracefully', async () => {
    const user = userEvent.setup()

    // Mock analysis submission success but results never complete
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockAnalysisResponse
      })
      // Mock multiple polling responses that never complete
      .mockResolvedValue({
        ok: true,
        json: async () => ({
          ...mockAnalysisResponse,
          status: 'processing'
        })
      })

    render(<Analysis />)

    // Fill out and submit form
    const titleInput = screen.getByLabelText(/research title/i)
    const abstractInput = screen.getByLabelText(/research abstract/i)
    const submitButton = screen.getByRole('button', { name: /analyze research/i })

    await user.type(titleInput, sampleFormData.title)
    await user.type(abstractInput, sampleFormData.abstract)
    await user.click(submitButton)

    // Wait for timeout error
    await waitFor(() => {
      expect(screen.getByText(/analysis timeout/i)).toBeInTheDocument()
    }, { timeout: 35000 }) // Wait longer than the 30-second timeout
  })

  it('should load and display analysis history', async () => {
    const user = userEvent.setup()

    // Mock localStorage with existing history
    const mockHistory = [
      {
        id: 1,
        timestamp: '2024-01-01T00:00:00Z',
        title: 'Previous Analysis',
        abstract: 'Previous analysis abstract...',
        results: mockResultsResponse.results
      }
    ]
    mockLocalStorage.getItem.mockReturnValue(JSON.stringify(mockHistory))

    render(<Analysis />)

    // Verify history button is shown
    expect(screen.getByText(/view history \(1\)/i)).toBeInTheDocument()

    // Click to show history
    await user.click(screen.getByText(/view history \(1\)/i))

    // Verify history is displayed
    expect(screen.getByText('Previous Analysis')).toBeInTheDocument()
    expect(screen.getByText(/previous analysis abstract/i)).toBeInTheDocument()

    // Click on history item to load results
    await user.click(screen.getByText('Previous Analysis'))

    // Verify results are loaded
    expect(screen.getByText(/analysis results/i)).toBeInTheDocument()
  })

  it('should handle network errors', async () => {
    const user = userEvent.setup()

    // Mock network error
    mockFetch.mockRejectedValueOnce(new Error('Network error'))

    render(<Analysis />)

    // Fill out and submit form
    const titleInput = screen.getByLabelText(/research title/i)
    const abstractInput = screen.getByLabelText(/research abstract/i)
    const submitButton = screen.getByRole('button', { name: /analyze research/i })

    await user.type(titleInput, sampleFormData.title)
    await user.type(abstractInput, sampleFormData.abstract)
    await user.click(submitButton)

    // Wait for error
    await waitFor(() => {
      expect(screen.getByText(/analysis failed/i)).toBeInTheDocument()
    })

    expect(screen.getByText(/network error/i)).toBeInTheDocument()
  })

  it('should validate form inputs properly', async () => {
    const user = userEvent.setup()

    render(<Analysis />)

    const titleInput = screen.getByLabelText(/research title/i)
    const abstractInput = screen.getByLabelText(/research abstract/i)
    const submitButton = screen.getByRole('button', { name: /analyze research/i })

    // Initially button should be disabled
    expect(submitButton).toHaveClass('disabled')

    // Type short title
    await user.type(titleInput, 'AI')
    await user.tab() // Trigger blur event

    // Should show validation error
    expect(screen.getByText(/title must be at least 5 characters long/i)).toBeInTheDocument()

    // Type valid title
    await user.clear(titleInput)
    await user.type(titleInput, sampleFormData.title)

    // Type short abstract
    await user.type(abstractInput, 'Too short')
    await user.tab() // Trigger blur event

    // Should show validation error
    expect(screen.getByText(/abstract must be at least 20 characters long/i)).toBeInTheDocument()

    // Type valid abstract
    await user.clear(abstractInput)
    await user.type(abstractInput, sampleFormData.abstract)

    // Button should now be enabled
    await waitFor(() => {
      expect(submitButton).not.toHaveClass('disabled')
    })
  })
})