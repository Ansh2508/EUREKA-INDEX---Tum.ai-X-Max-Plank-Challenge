import { useState, useEffect } from 'react'
import './AnalysisForm.css'

function AnalysisForm({ onSubmit, loading }) {
  const [title, setTitle] = useState('')
  const [abstract, setAbstract] = useState('')
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
      } else if (abstract.length < 20) {
        newErrors.abstract = 'Abstract must be at least 20 characters long'
      } else if (abstract.length > 5000) {
        newErrors.abstract = 'Abstract must be less than 5000 characters'
      }
    }
    
    setErrors(newErrors)
    
    // Check if form is valid for submission
    const hasRequiredFields = title.trim() && abstract.trim()
    const hasNoErrors = Object.keys(newErrors).length === 0
    const meetsMinimumLength = title.length >= 5 && abstract.length >= 20
    setIsFormValid(hasRequiredFields && hasNoErrors && meetsMinimumLength)
  }, [title, abstract, touched])

  const handleBlur = (field) => {
    setTouched(prev => ({ ...prev, [field]: true }))
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    
    // Mark all fields as touched for validation display
    setTouched({ title: true, abstract: true })
    
    if (isFormValid) {
      onSubmit({ title: title.trim(), abstract: abstract.trim() })
    }
  }

  const handleClear = () => {
    setTitle('')
    setAbstract('')
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
    <div className="analysis-form-container">
      <div className="form-header">
        <div className="header-icon">🔬</div>
        <h2>Submit Research for Analysis</h2>
        <p>Provide your research details to discover similar patents and assess commercialization potential</p>
      </div>

      <form onSubmit={handleSubmit} className="analysis-form">
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
            rows={10}
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

        <div className="form-actions">
          <button 
            type="button"
            className="btn btn-secondary"
            onClick={handleClear}
            disabled={loading || (!title && !abstract)}
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
                Analyzing...
              </>
            ) : (
              <>
                <span className="btn-icon">🔍</span>
                Analyze Research
              </>
            )}
          </button>
        </div>

        {isFormValid && !loading && (
          <div className="form-preview">
            <h4>📋 Analysis Preview</h4>
            <div className="preview-content">
              <div className="preview-item">
                <strong>Title:</strong> {title}
              </div>
              <div className="preview-item">
                <strong>Abstract:</strong> {abstract.substring(0, 150)}...
              </div>
              <div className="preview-stats">
                <span>📊 {title.split(' ').length} words in title</span>
                <span>📝 {abstract.split(' ').length} words in abstract</span>
              </div>
            </div>
          </div>
        )}

        {!loading && (title || abstract) && (
          <div className="form-tips">
            <h4>💡 Tips for better results:</h4>
            <ul>
              <li>Include specific technical terms and methodologies</li>
              <li>Mention the problem domain and potential applications</li>
              <li>Describe what makes your approach novel or innovative</li>
              <li>Include any preliminary results or validation data</li>
            </ul>
          </div>
        )}
      </form>
    </div>
  )
}

export default AnalysisForm