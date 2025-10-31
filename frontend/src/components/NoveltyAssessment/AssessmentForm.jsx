import { useState, useEffect } from 'react'
import './AssessmentForm.css'

function AssessmentForm({ onSubmit, loading }) {
  const [title, setTitle] = useState('')
  const [abstract, setAbstract] = useState('')
  const [claims, setClaims] = useState([''])
  const [errors, setErrors] = useState({})
  const [touched, setTouched] = useState({})
  const [isFormValid, setIsFormValid] = useState(false)

  // Real-time validation
  useEffect(() => {
    const newErrors = {}
    
    if (touched.title) {
      if (!title.trim()) {
        newErrors.title = 'Title is required'
      } else if (title.length < 5) {
        newErrors.title = 'Title must be at least 5 characters long'
      } else if (title.length > 500) {
        newErrors.title = 'Title must be less than 500 characters'
      }
    }
    
    if (touched.abstract) {
      if (!abstract.trim()) {
        newErrors.abstract = 'Abstract is required'
      } else if (abstract.length < 50) {
        newErrors.abstract = 'Abstract must be at least 50 characters long'
      } else if (abstract.length > 5000) {
        newErrors.abstract = 'Abstract must be less than 5000 characters'
      }
    }

    if (touched.claims) {
      const validClaims = claims.filter(claim => claim.trim())
      if (validClaims.length === 0) {
        newErrors.claims = 'At least one claim is required'
      } else if (validClaims.some(claim => claim.length < 10)) {
        newErrors.claims = 'Each claim must be at least 10 characters long'
      }
    }
    
    setErrors(newErrors)
    
    // Check if form is valid for submission
    const hasRequiredFields = title.trim() && abstract.trim() && claims.some(claim => claim.trim())
    const hasNoErrors = Object.keys(newErrors).length === 0
    const meetsMinimumLength = title.length >= 5 && abstract.length >= 50
    setIsFormValid(hasRequiredFields && hasNoErrors && meetsMinimumLength)
  }, [title, abstract, claims, touched])

  const handleBlur = (field) => {
    setTouched(prev => ({ ...prev, [field]: true }))
  }

  const handleClaimChange = (index, value) => {
    const newClaims = [...claims]
    newClaims[index] = value
    setClaims(newClaims)
  }

  const addClaim = () => {
    setClaims([...claims, ''])
  }

  const removeClaim = (index) => {
    if (claims.length > 1) {
      const newClaims = claims.filter((_, i) => i !== index)
      setClaims(newClaims)
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    
    // Mark all fields as touched for validation display
    setTouched({ title: true, abstract: true, claims: true })
    
    if (isFormValid) {
      const validClaims = claims.filter(claim => claim.trim())
      onSubmit({ 
        research_title: title.trim(), 
        research_abstract: abstract.trim(),
        claims: validClaims
      })
    }
  }

  const handleClear = () => {
    setTitle('')
    setAbstract('')
    setClaims([''])
    setErrors({})
    setTouched({})
  }

  const getCharCountColor = (current, max) => {
    const percentage = (current / max) * 100
    if (percentage > 90) return '#ef4444' // red
    if (percentage > 75) return '#f59e0b' // amber
    return '#6b7280' // gray
  }

  return (
    <div className="assessment-form-container">
      <div className="form-header">
        <div className="header-icon">🔍</div>
        <h2>Submit Research for Novelty Assessment</h2>
        <p>Evaluate the novelty and patentability of your research with comprehensive prior art analysis</p>
      </div>

      <form onSubmit={handleSubmit} className="assessment-form">
        <div className="form-group">
          <label htmlFor="title" className="form-label">
            Research Title *
            <span className="label-hint">A clear, descriptive title of your research</span>
          </label>
          <input
            type="text"
            id="title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            onBlur={() => handleBlur('title')}
            placeholder="e.g., Novel Machine Learning Algorithm for Medical Image Analysis"
            className={`form-input ${errors.title ? 'error' : ''} ${title && !errors.title ? 'valid' : ''}`}
            disabled={loading}
          />
          {errors.title && <span className="error-text">⚠️ {errors.title}</span>}
          <div 
            className="char-count"
            style={{ color: getCharCountColor(title.length, 500) }}
          >
            {title.length}/500 characters
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="abstract" className="form-label">
            Research Abstract *
            <span className="label-hint">Detailed description of your research, methodology, and findings</span>
          </label>
          <textarea
            id="abstract"
            value={abstract}
            onChange={(e) => setAbstract(e.target.value)}
            onBlur={() => handleBlur('abstract')}
            placeholder="Describe your research in detail including the problem you're solving, your approach, key findings, and potential applications. Be specific about the technical aspects and innovations."
            rows={8}
            className={`form-textarea ${errors.abstract ? 'error' : ''} ${abstract && !errors.abstract ? 'valid' : ''}`}
            disabled={loading}
          />
          {errors.abstract && <span className="error-text">⚠️ {errors.abstract}</span>}
          <div 
            className="char-count"
            style={{ color: getCharCountColor(abstract.length, 5000) }}
          >
            {abstract.length}/5000 characters
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">
            Research Claims *
            <span className="label-hint">Specific claims about your invention or discovery</span>
          </label>
          {claims.map((claim, index) => (
            <div key={index} className="claim-input-group">
              <div className="claim-number">{index + 1}.</div>
              <textarea
                value={claim}
                onChange={(e) => handleClaimChange(index, e.target.value)}
                onBlur={() => handleBlur('claims')}
                placeholder={`Claim ${index + 1}: Describe a specific aspect of your invention...`}
                rows={3}
                className={`form-textarea claim-textarea ${errors.claims ? 'error' : ''}`}
                disabled={loading}
              />
              {claims.length > 1 && (
                <button
                  type="button"
                  className="remove-claim-btn"
                  onClick={() => removeClaim(index)}
                  disabled={loading}
                  title="Remove this claim"
                >
                  ✕
                </button>
              )}
            </div>
          ))}
          
          <button
            type="button"
            className="btn btn-secondary add-claim-btn"
            onClick={addClaim}
            disabled={loading || claims.length >= 10}
          >
            <span className="btn-icon">➕</span>
            Add Another Claim
          </button>
          
          {errors.claims && <span className="error-text">⚠️ {errors.claims}</span>}
          <div className="claims-count">
            {claims.filter(claim => claim.trim()).length} of {claims.length} claims completed
          </div>
        </div>

        <div className="form-actions">
          <button 
            type="button"
            className="btn btn-secondary"
            onClick={handleClear}
            disabled={loading || (!title && !abstract && claims.every(c => !c))}
          >
            <span className="btn-icon">🗑️</span>
            Clear Form
          </button>
          
          <button 
            type="submit" 
            className={`btn btn-primary btn-large ${!isFormValid ? 'disabled' : ''}`}
            disabled={loading || !isFormValid}
          >
            {loading ? (
              <>
                <span className="btn-spinner"></span>
                Assessing Novelty...
              </>
            ) : (
              <>
                <span className="btn-icon">🔍</span>
                Assess Novelty
              </>
            )}
          </button>
        </div>

        {isFormValid && !loading && (
          <div className="form-preview">
            <h4>📋 Assessment Preview</h4>
            <div className="preview-content">
              <div className="preview-item">
                <strong>Title:</strong> {title}
              </div>
              <div className="preview-item">
                <strong>Abstract:</strong> {abstract.substring(0, 150)}...
              </div>
              <div className="preview-item">
                <strong>Claims:</strong> {claims.filter(c => c.trim()).length} claims defined
              </div>
            </div>
          </div>
        )}

        {!loading && (title || abstract || claims.some(c => c)) && (
          <div className="form-tips">
            <h4>💡 Tips for better novelty assessment:</h4>
            <ul>
              <li>Be specific about technical innovations and unique aspects</li>
              <li>Include detailed methodology and implementation details</li>
              <li>Clearly define what makes your approach different from existing solutions</li>
              <li>Provide measurable results or performance improvements</li>
              <li>Write claims that are specific and technically precise</li>
            </ul>
          </div>
        )}
      </form>
    </div>
  )
}

export default AssessmentForm