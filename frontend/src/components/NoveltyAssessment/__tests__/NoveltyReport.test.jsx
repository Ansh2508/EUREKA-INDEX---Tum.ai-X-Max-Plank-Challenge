import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import NoveltyReport from '../NoveltyReport'

const mockAssessment = {
  overall_novelty_score: 0.85,
  novelty_category: 'Highly Novel',
  patentability_indicators: {
    patentability_likelihood: 'High',
    prior_art_conflicts: 2,
    key_differentiators: [
      'Novel machine learning approach',
      'Unique data processing method'
    ]
  },
  prior_art_analysis: {
    analysis_summary: 'Limited prior art found with similar approach',
    key_findings: [
      'No direct conflicts identified',
      'Some related work in adjacent fields'
    ]
  },
  claim_analysis: {
    individual_claim_analysis: [
      {
        claim_text: 'A machine learning algorithm for medical image analysis',
        novelty_score: 0.8,
        potential_conflicts: [],
        recommendations: ['Consider narrowing the scope']
      }
    ],
    overall_claim_assessment: {
      average_novelty_score: 0.8,
      high_risk_claims: 0,
      recommended_actions: ['File patent application']
    }
  },
  recommendations: [
    'Proceed with patent filing',
    'Consider additional claims for broader protection'
  ],
  similar_patents: [
    {
      title: 'Medical Image Processing System',
      similarity_score: 0.65,
      patent_number: 'US1234567',
      publication_date: '2020-01-01'
    }
  ],
  similar_publications: [
    {
      title: 'Machine Learning in Medical Imaging',
      similarity_score: 0.55,
      doi: '10.1000/test',
      publication_date: '2021-06-15'
    }
  ]
}

describe('NoveltyReport', () => {
  test('renders loading state', () => {
    render(<NoveltyReport assessment={null} loading={true} />)
    
    expect(screen.getByText(/generating novelty assessment report/i)).toBeInTheDocument()
  })

  test('renders nothing when no assessment and not loading', () => {
    const { container } = render(<NoveltyReport assessment={null} loading={false} />)
    
    expect(container.firstChild).toBeNull()
  })

  test('renders assessment report with key metrics', () => {
    render(<NoveltyReport assessment={mockAssessment} loading={false} />)
    
    // Check header
    expect(screen.getByText(/novelty assessment report/i)).toBeInTheDocument()
    
    // Check key metrics
    expect(screen.getByText('85%')).toBeInTheDocument() // Novelty score
    expect(screen.getByText('High')).toBeInTheDocument() // Patentability
    expect(screen.getByText('2')).toBeInTheDocument() // Prior art found
    expect(screen.getByText('2')).toBeInTheDocument() // Conflicts
  })

  test('switches between tabs', async () => {
    const user = userEvent.setup()
    render(<NoveltyReport assessment={mockAssessment} loading={false} />)
    
    // Initially on overview tab
    expect(screen.getByText(/assessment summary/i)).toBeInTheDocument()
    
    // Switch to prior art tab
    const priorArtTab = screen.getByRole('button', { name: /prior art/i })
    await user.click(priorArtTab)
    
    expect(screen.getByText(/prior art analysis/i)).toBeInTheDocument()
    
    // Switch to claims tab
    const claimsTab = screen.getByRole('button', { name: /claims analysis/i })
    await user.click(claimsTab)
    
    expect(screen.getByText(/claims analysis & comparison/i)).toBeInTheDocument()
    
    // Switch to recommendations tab
    const recommendationsTab = screen.getByRole('button', { name: /recommendations/i })
    await user.click(recommendationsTab)
    
    expect(screen.getByText(/strategic recommendations/i)).toBeInTheDocument()
  })

  test('displays novelty score with appropriate color coding', () => {
    render(<NoveltyReport assessment={mockAssessment} loading={false} />)
    
    const noveltyScore = screen.getByText('85%')
    const computedStyle = window.getComputedStyle(noveltyScore)
    
    // High novelty should be green
    expect(computedStyle.color).toBe('rgb(16, 185, 129)') // #10b981
  })

  test('shows patentability assessment', () => {
    render(<NoveltyReport assessment={mockAssessment} loading={false} />)
    
    expect(screen.getByText('High')).toBeInTheDocument()
    expect(screen.getByText('Likelihood')).toBeInTheDocument()
  })

  test('displays key differentiators', () => {
    render(<NoveltyReport assessment={mockAssessment} loading={false} />)
    
    expect(screen.getByText('Novel machine learning approach')).toBeInTheDocument()
    expect(screen.getByText('Unique data processing method')).toBeInTheDocument()
  })

  test('shows prior art analysis summary', () => {
    render(<NoveltyReport assessment={mockAssessment} loading={false} />)
    
    expect(screen.getByText('Limited prior art found with similar approach')).toBeInTheDocument()
    expect(screen.getByText('No direct conflicts identified')).toBeInTheDocument()
  })

  test('displays recommendations', async () => {
    const user = userEvent.setup()
    render(<NoveltyReport assessment={mockAssessment} loading={false} />)
    
    // Switch to recommendations tab
    const recommendationsTab = screen.getByRole('button', { name: /recommendations/i })
    await user.click(recommendationsTab)
    
    expect(screen.getByText('Proceed with patent filing')).toBeInTheDocument()
    expect(screen.getByText('Consider additional claims for broader protection')).toBeInTheDocument()
  })

  test('toggles detailed report view', async () => {
    const user = userEvent.setup()
    render(<NoveltyReport assessment={mockAssessment} loading={false} />)
    
    const detailedButton = screen.getByRole('button', { name: /detailed report/i })
    await user.click(detailedButton)
    
    expect(screen.getByRole('button', { name: /summary view/i })).toBeInTheDocument()
  })

  test('handles missing optional data gracefully', () => {
    const minimalAssessment = {
      overall_novelty_score: 0.7,
      novelty_category: 'Moderately Novel'
    }
    
    render(<NoveltyReport assessment={minimalAssessment} loading={false} />)
    
    // Should still render basic metrics
    expect(screen.getByText('70%')).toBeInTheDocument()
    expect(screen.getByText('Moderately Novel')).toBeInTheDocument()
    
    // Should handle missing data gracefully
    expect(screen.getByText('Unknown')).toBeInTheDocument() // For missing patentability
  })
})