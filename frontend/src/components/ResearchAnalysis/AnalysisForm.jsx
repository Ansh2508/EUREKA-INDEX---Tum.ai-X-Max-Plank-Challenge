import { useState, useEffect } from 'react'
import { FileText, Sparkles, RotateCcw } from 'lucide-react'
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
    <form onSubmit={handleSubmit} className="modern-analysis-form">
      <div className="form-fields">
        <div className="field-group">
          <label htmlFor="title" className="field-label">
            <FileText size={16} />
            Research Title
            <span className="required">*</span>
          </label>
          <input
            type="text"
            id="title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            onBlur={() => handleBlur('title')}
            placeholder="Enter a clear, descriptive title of your research"
            className={`field-input ${errors.title ? 'error' : ''} ${title && !errors.title ? 'valid' : ''}`}
            disabled={loading}
          />
          {errors.title && (
            <div className="field-error">
              {errors.title}
            </div>
          )}
          <div className="field-meta">
            <span className={`char-count ${title.length > 450 ? 'warning' : ''} ${title.length > 500 ? 'error' : ''}`}>
              {title.length}/500
            </span>
          </div>
        </div>

        <div className="field-group">
          <label htmlFor="abstract" className="field-label">
            <Sparkles size={16} />
            Research Abstract
            <span className="required">*</span>
          </label>
          <textarea
            id="abstract"
            value={abstract}
            onChange={(e) => setAbstract(e.target.value)}
            onBlur={() => handleBlur('abstract')}
            placeholder="Provide a detailed description of your research including methodology, key findings, and potential applications. Be specific about technical innovations and the problems you're solving."
            rows={8}
            className={`field-textarea ${errors.abstract ? 'error' : ''} ${abstract && !errors.abstract ? 'valid' : ''}`}
            disabled={loading}
          />
          {errors.abstract && (
            <div className="field-error">
              {errors.abstract}
            </div>
          )}
          <div className="field-meta">
            <span className={`char-count ${abstract.length > 4500 ? 'warning' : ''} ${abstract.length > 5000 ? 'error' : ''}`}>
              {abstract.length}/5000
            </span>
            <span className="word-count">
              {abstract.trim() ? abstract.trim().split(/\s+/).length : 0} words
            </span>
          </div>
        </div>
      </div>

      <div className="form-actions">
        <button
          type="button"
          className="modern-btn secondary-btn"
          onClick={handleClear}
          disabled={loading || (!title && !abstract)}
        >
          <RotateCcw size={16} />
          Clear
        </button>

        <button
          type="submit"
          className="modern-btn primary-btn"
          disabled={loading || !isFormValid}
        >
          {loading ? (
            <>
              <div className="spinner" />
              Analyzing...
            </>
          ) : (
            <>
              <Sparkles size={16} />
              Start Analysis
            </>
          )}
        </button>
      </div>

      {isFormValid && !loading && (
        <div className="form-summary">
          <div className="summary-header">
            <h4>Ready to Analyze</h4>
            <div className="summary-stats">
              <span className="stat">
                {title.split(' ').length} title words
              </span>
              <span className="stat">
                {abstract.split(' ').length} abstract words
              </span>
            </div>
          </div>
        </div>
      )}
    </form>
  )
}

export default AnalysisForm