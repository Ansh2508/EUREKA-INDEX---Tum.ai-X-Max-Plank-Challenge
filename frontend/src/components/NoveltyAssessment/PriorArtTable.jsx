import { useState, useMemo } from 'react'
import './PriorArtTable.css'

function PriorArtTable({ patents = [], publications = [] }) {
  const [activeFilter, setActiveFilter] = useState('all')
  const [sortBy, setSortBy] = useState('similarity')
  const [sortOrder, setSortOrder] = useState('desc')
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedItems, setSelectedItems] = useState(new Set())

  // Combine and normalize data
  const allPriorArt = useMemo(() => {
    const normalizedPatents = patents.map(patent => ({
      ...patent,
      type: 'patent',
      title: patent.title || patent.patent_title || 'Untitled Patent',
      abstract: patent.abstract || patent.patent_abstract || '',
      similarity: patent.similarity_score || patent.similarity || 0,
      date: patent.publication_date || patent.date || '',
      authors: patent.inventors || patent.authors || [],
      identifier: patent.patent_number || patent.id || '',
      source: patent.assignee || 'Unknown'
    }))

    const normalizedPublications = publications.map(pub => ({
      ...pub,
      type: 'publication',
      title: pub.title || pub.publication_title || 'Untitled Publication',
      abstract: pub.abstract || pub.publication_abstract || '',
      similarity: pub.similarity_score || pub.similarity || 0,
      date: pub.publication_date || pub.date || '',
      authors: pub.authors || [],
      identifier: pub.doi || pub.id || '',
      source: pub.journal || pub.venue || 'Unknown'
    }))

    return [...normalizedPatents, ...normalizedPublications]
  }, [patents, publications])

  // Filter and sort data
  const filteredAndSortedData = useMemo(() => {
    let filtered = allPriorArt

    // Apply type filter
    if (activeFilter !== 'all') {
      filtered = filtered.filter(item => item.type === activeFilter)
    }

    // Apply search filter
    if (searchTerm) {
      const term = searchTerm.toLowerCase()
      filtered = filtered.filter(item =>
        item.title.toLowerCase().includes(term) ||
        item.abstract.toLowerCase().includes(term) ||
        item.authors.some(author => author.toLowerCase().includes(term)) ||
        item.source.toLowerCase().includes(term)
      )
    }

    // Sort data
    filtered.sort((a, b) => {
      let aValue, bValue

      switch (sortBy) {
        case 'similarity':
          aValue = a.similarity
          bValue = b.similarity
          break
        case 'date':
          aValue = new Date(a.date || 0)
          bValue = new Date(b.date || 0)
          break
        case 'title':
          aValue = a.title.toLowerCase()
          bValue = b.title.toLowerCase()
          break
        default:
          return 0
      }

      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1
      } else {
        return aValue < bValue ? 1 : -1
      }
    })

    return filtered
  }, [allPriorArt, activeFilter, searchTerm, sortBy, sortOrder])

  const handleSort = (field) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      setSortBy(field)
      setSortOrder('desc')
    }
  }

  const handleSelectItem = (identifier) => {
    const newSelected = new Set(selectedItems)
    if (newSelected.has(identifier)) {
      newSelected.delete(identifier)
    } else {
      newSelected.add(identifier)
    }
    setSelectedItems(newSelected)
  }

  const handleSelectAll = () => {
    if (selectedItems.size === filteredAndSortedData.length) {
      setSelectedItems(new Set())
    } else {
      setSelectedItems(new Set(filteredAndSortedData.map(item => item.identifier)))
    }
  }

  const getSimilarityColor = (similarity) => {
    if (similarity >= 0.8) return '#ef4444' // red - high conflict risk
    if (similarity >= 0.6) return '#f59e0b' // amber - medium risk
    return '#10b981' // green - low risk
  }

  const getSimilarityLevel = (similarity) => {
    if (similarity >= 0.8) return 'High'
    if (similarity >= 0.6) return 'Medium'
    return 'Low'
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'Unknown'
    try {
      return new Date(dateString).toLocaleDateString()
    } catch {
      return dateString
    }
  }

  const truncateText = (text, maxLength = 150) => {
    if (!text) return ''
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
  }

  return (
    <div className="prior-art-table">
      <div className="table-header">
        <div className="header-content">
          <h3>Prior Art Analysis</h3>
          <div className="header-stats">
            <span className="stat-item">
              <strong>{patents.length}</strong> Patents
            </span>
            <span className="stat-item">
              <strong>{publications.length}</strong> Publications
            </span>
            <span className="stat-item">
              <strong>{filteredAndSortedData.length}</strong> Total Results
            </span>
          </div>
        </div>

        <div className="table-controls">
          <div className="search-box">
            <input
              type="text"
              placeholder="Search prior art..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
          </div>

          <div className="filter-tabs">
            <button
              className={`filter-tab ${activeFilter === 'all' ? 'active' : ''}`}
              onClick={() => setActiveFilter('all')}
            >
              All ({allPriorArt.length})
            </button>
            <button
              className={`filter-tab ${activeFilter === 'patent' ? 'active' : ''}`}
              onClick={() => setActiveFilter('patent')}
            >
              Patents ({patents.length})
            </button>
            <button
              className={`filter-tab ${activeFilter === 'publication' ? 'active' : ''}`}
              onClick={() => setActiveFilter('publication')}
            >
              Publications ({publications.length})
            </button>
          </div>
        </div>
      </div>

      {filteredAndSortedData.length === 0 ? (
        <div className="no-results">
          <div className="no-results-icon">🔍</div>
          <h4>No Prior Art Found</h4>
          <p>
            {searchTerm 
              ? `No results found for "${searchTerm}". Try adjusting your search terms.`
              : 'No prior art documents were identified for this research.'
            }
          </p>
        </div>
      ) : (
        <>
          <div className="table-actions">
            <div className="selection-controls">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={selectedItems.size === filteredAndSortedData.length && filteredAndSortedData.length > 0}
                  onChange={handleSelectAll}
                />
                Select All ({selectedItems.size} selected)
              </label>
            </div>

            <div className="action-buttons">
              <button 
                className="btn btn-secondary"
                disabled={selectedItems.size === 0}
              >
                📥 Export Selected
              </button>
              <button 
                className="btn btn-secondary"
                disabled={selectedItems.size === 0}
              >
                📊 Compare Selected
              </button>
            </div>
          </div>

          <div className="table-container">
            <table className="prior-art-data-table">
              <thead>
                <tr>
                  <th className="select-column">
                    <input
                      type="checkbox"
                      checked={selectedItems.size === filteredAndSortedData.length && filteredAndSortedData.length > 0}
                      onChange={handleSelectAll}
                    />
                  </th>
                  <th className="type-column">Type</th>
                  <th 
                    className={`sortable ${sortBy === 'title' ? 'sorted' : ''}`}
                    onClick={() => handleSort('title')}
                  >
                    Title {sortBy === 'title' && (sortOrder === 'asc' ? '↑' : '↓')}
                  </th>
                  <th 
                    className={`sortable similarity-column ${sortBy === 'similarity' ? 'sorted' : ''}`}
                    onClick={() => handleSort('similarity')}
                  >
                    Similarity {sortBy === 'similarity' && (sortOrder === 'asc' ? '↑' : '↓')}
                  </th>
                  <th 
                    className={`sortable date-column ${sortBy === 'date' ? 'sorted' : ''}`}
                    onClick={() => handleSort('date')}
                  >
                    Date {sortBy === 'date' && (sortOrder === 'asc' ? '↑' : '↓')}
                  </th>
                  <th className="authors-column">Authors/Inventors</th>
                  <th className="actions-column">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredAndSortedData.map((item, index) => (
                  <tr key={`${item.type}-${item.identifier}-${index}`} className="table-row">
                    <td className="select-cell">
                      <input
                        type="checkbox"
                        checked={selectedItems.has(item.identifier)}
                        onChange={() => handleSelectItem(item.identifier)}
                      />
                    </td>
                    <td className="type-cell">
                      <span className={`type-badge ${item.type}`}>
                        {item.type === 'patent' ? '📄' : '📚'} {item.type}
                      </span>
                    </td>
                    <td className="title-cell">
                      <div className="title-content">
                        <h4 className="item-title">{item.title}</h4>
                        <p className="item-abstract">{truncateText(item.abstract)}</p>
                        <div className="item-meta">
                          <span className="meta-item">
                            <strong>Source:</strong> {item.source}
                          </span>
                          {item.identifier && (
                            <span className="meta-item">
                              <strong>ID:</strong> {item.identifier}
                            </span>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="similarity-cell">
                      <div className="similarity-content">
                        <div 
                          className="similarity-score"
                          style={{ color: getSimilarityColor(item.similarity) }}
                        >
                          {Math.round(item.similarity * 100)}%
                        </div>
                        <div className="similarity-bar">
                          <div 
                            className="similarity-fill"
                            style={{ 
                              width: `${item.similarity * 100}%`,
                              backgroundColor: getSimilarityColor(item.similarity)
                            }}
                          ></div>
                        </div>
                        <div className="similarity-level">
                          {getSimilarityLevel(item.similarity)} Risk
                        </div>
                      </div>
                    </td>
                    <td className="date-cell">
                      {formatDate(item.date)}
                    </td>
                    <td className="authors-cell">
                      <div className="authors-list">
                        {item.authors.slice(0, 3).map((author, idx) => (
                          <span key={idx} className="author-name">{author}</span>
                        ))}
                        {item.authors.length > 3 && (
                          <span className="author-more">+{item.authors.length - 3} more</span>
                        )}
                      </div>
                    </td>
                    <td className="actions-cell">
                      <div className="action-buttons">
                        <button className="btn btn-small btn-secondary" title="View Details">
                          👁️
                        </button>
                        <button className="btn btn-small btn-secondary" title="Compare Claims">
                          ⚖️
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  )
}

export default PriorArtTable