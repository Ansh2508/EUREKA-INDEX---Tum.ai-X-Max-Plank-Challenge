import { render, screen } from '@testing-library/react'
import SimilarityCard from '../SimilarityCard'

describe('SimilarityCard', () => {
  const mockPatent = {
    title: 'Test Patent Title',
    score: 0.85,
    url: 'https://example.com/patent',
    year: 2023,
    citations: 15,
    assignee: 'Test Company',
    inventors: ['John Doe', 'Jane Smith'],
    abstract: 'This is a test patent abstract with sufficient length for testing purposes.'
  }

  const mockPublication = {
    title: 'Test Publication Title',
    score: 0.75,
    url: 'https://example.com/publication',
    year: 2022,
    citations: 25,
    authors: ['Dr. Alice Johnson', 'Prof. Bob Wilson'],
    journal: 'Test Journal',
    abstract: 'This is a test publication abstract with sufficient length for testing purposes.'
  }

  test('renders patent card correctly', () => {
    render(<SimilarityCard document={mockPatent} type="patent" />)
    
    expect(screen.getByText('📄 Patent')).toBeInTheDocument()
    expect(screen.getByText('85.0%')).toBeInTheDocument()
    expect(screen.getByText('Test Patent Title')).toBeInTheDocument()
    expect(screen.getByText(/Test Company/)).toBeInTheDocument()
    expect(screen.getByText(/John Doe, Jane Smith/)).toBeInTheDocument()
    expect(screen.getByText(/2023/)).toBeInTheDocument()
    expect(screen.getByText(/15 citations/)).toBeInTheDocument()
  })

  test('renders publication card correctly', () => {
    render(<SimilarityCard document={mockPublication} type="publication" />)
    
    expect(screen.getByText('📚 Publication')).toBeInTheDocument()
    expect(screen.getByText('75.0%')).toBeInTheDocument()
    expect(screen.getByText('Test Publication Title')).toBeInTheDocument()
    expect(screen.getByText(/Dr. Alice Johnson, Prof. Bob Wilson/)).toBeInTheDocument()
    expect(screen.getByText(/Test Journal/)).toBeInTheDocument()
    expect(screen.getByText(/2022/)).toBeInTheDocument()
    expect(screen.getByText(/25 citations/)).toBeInTheDocument()
  })

  test('truncates long abstracts', () => {
    const longAbstract = 'A'.repeat(300)
    const documentWithLongAbstract = {
      ...mockPatent,
      abstract: longAbstract
    }
    
    render(<SimilarityCard document={documentWithLongAbstract} type="patent" />)
    
    const abstractElement = screen.getByText(/A{200}\.\.\./)
    expect(abstractElement).toBeInTheDocument()
  })

  test('handles missing data gracefully', () => {
    const incompleteDocument = {
      title: 'Test Title',
      score: null
    }
    
    render(<SimilarityCard document={incompleteDocument} type="patent" />)
    
    expect(screen.getByText('Test Title')).toBeInTheDocument()
    expect(screen.getByText('N/A')).toBeInTheDocument()
    expect(screen.getByText('No abstract available')).toBeInTheDocument()
  })

  test('renders clickable title when URL is provided', () => {
    render(<SimilarityCard document={mockPatent} type="patent" />)
    
    const titleLink = screen.getByRole('link', { name: 'Test Patent Title' })
    expect(titleLink).toHaveAttribute('href', 'https://example.com/patent')
    expect(titleLink).toHaveAttribute('target', '_blank')
  })

  test('renders view link when URL is provided', () => {
    render(<SimilarityCard document={mockPatent} type="patent" />)
    
    const viewLink = screen.getByRole('link', { name: /view full document/i })
    expect(viewLink).toHaveAttribute('href', 'https://example.com/patent')
    expect(viewLink).toHaveAttribute('target', '_blank')
  })

  test('handles multiple inventors/authors correctly', () => {
    const documentWithManyAuthors = {
      ...mockPatent,
      inventors: ['Author 1', 'Author 2', 'Author 3', 'Author 4']
    }
    
    render(<SimilarityCard document={documentWithManyAuthors} type="patent" />)
    
    expect(screen.getByText(/Author 1, Author 2 \+2 more/)).toBeInTheDocument()
  })
})