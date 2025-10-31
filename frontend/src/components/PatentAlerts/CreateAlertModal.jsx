import { useState, useEffect } from 'react'
import { X, Plus, Trash2, Target, Bell, Search } from 'lucide-react'
import LoadingSpinner from '../UI/LoadingSpinner'
import './CreateAlertModal.css'

function CreateAlertModal({ onClose, onSubmit }) {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    keywords: [''],
    similarityThreshold: 0.8,
    lookbackDays: 30,
    frequency: 'weekly',
    sources: ['uspto', 'epo', 'wipo']
  })
  const [errors, setErrors] = useState({})
  const [touched, setTouched] = useState({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isFormValid, setIsFormValid] = useState(false)

  // Validation
  useEffect(() => {
    const newErrors = {}
    
    if (touched.name) {
      if (!formData.name.trim()) {
        newErrors.name = 'Alert name is required'
      } else if (formData.name.length < 3) {
        newErrors.name = 'Alert name must be at least 3 characters'
      } else if (formData.name.length > 100) {
        newErrors.name = 'Alert name must be less than 100 characters'
      }
    }

    if (touched.description) {
      if (!formData.description.trim()) {
        newErrors.description = 'Research description is required'
      } else if (formData.description.length < 10) {
        newErrors.description = 'Description must be at least 10 characters'
      } else if (formData.description.length > 5000) {
        newErrors.description = 'Description must be less than 5000 characters'
      }
    }
    
    if (touched.keywords) {
      const validKeywords = formData.keywords.filter(k => k.trim())
      if (validKeywords.length === 0) {
        newErrors.keywords = 'At least one keyword is required'
      } else if (validKeywords.some(k => k.length < 2)) {
        newErrors.keywords = 'Keywords must be at least 2 characters long'
      }
    }
    
    setErrors(newErrors)
    
    // Check form validity
    const hasRequiredFields = formData.name.trim() && 
                             formData.description.trim() &&
                             formData.keywords.some(k => k.trim().length >= 2)
    const hasNoErrors = Object.keys(newErrors).length === 0
    setIsFormValid(hasRequiredFields && hasNoErrors)
  }, [formData, touched])

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const handleBlur = (field) => {
    setTouched(prev => ({ ...prev, [field]: true }))
  }

  const handleKeywordChange = (index, value) => {
    const newKeywords = [...formData.keywords]
    newKeywords[index] = value
    setFormData(prev => ({ ...prev, keywords: newKeywords }))
  }

  const addKeyword = () => {
    setFormData(prev => ({
      ...prev,
      keywords: [...prev.keywords, '']
    }))
  }

  const removeKeyword = (index) => {
    if (formData.keywords.length > 1) {
      const newKeywords = formData.keywords.filter((_, i) => i !== index)
      setFormData(prev => ({ ...prev, keywords: newKeywords }))
    }
  }

  const handleSourceToggle = (source) => {
    const newSources = formData.sources.includes(source)
      ? formData.sources.filter(s => s !== source)
      : [...formData.sources, source]
    
    setFormData(prev => ({ ...prev, sources: newSources }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    // Mark all fields as touched for validation
    setTouched({ name: true, description: true, keywords: true })
    
    if (!isFormValid) return
    
    setIsSubmitting(true)
    
    try {
      const cleanedData = {
        ...formData,
        keywords: formData.keywords.filter(k => k.trim()).map(k => k.trim()),
        name: formData.name.trim()
      }
      
      await onSubmit(cleanedData)
    } catch (error) {
      console.error('Error creating alert:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose()
    }
  }

  const getThresholdLabel = (threshold) => {
    if (threshold >= 0.9) return 'Very High'
    if (threshold >= 0.8) return 'High'
    if (threshold >= 0.7) return 'Medium'
    if (threshold >= 0.6) return 'Low'
    return 'Very Low'
  }

  const sourceOptions = [
    { id: 'uspto', name: 'USPTO', description: 'United States Patent and Trademark Office' },
    { id: 'epo', name: 'EPO', description: 'European Patent Office' },
    { id: 'wipo', name: 'WIPO', description: 'World Intellectual Property Organization' }
  ]

  return (
    <div className="modal-overlay" onClick={handleOverlayClick}>
      <div className="create-alert-modal">
        <div className="modal-header">
          <div className="header-content">
            <div className="header-icon">
              <Bell size={24} />
            </div>
            <div>
              <h2>Create Patent Alert</h2>
              <p>Set up automated monitoring for new patents in your field</p>
            </div>
          </div>
          <button className="close-btn" onClick={onClose}>
            <X size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="modal-form">
          <div className="form-section">
            <h3>Basic Information</h3>
            
            <div className="form-group">
              <label htmlFor="alertName" className="form-label">
                Alert Name *
                <span className="label-hint">A descriptive name for your alert</span>
              </label>
              <input
                type="text"
                id="alertName"
                value={formData.name}
                onChange={(e) => handleInputChange('name', e.target.value)}
                onBlur={() => handleBlur('name')}
                placeholder="e.g., Machine Learning Patents"
                className={`form-input ${errors.name ? 'error' : ''}`}
                disabled={isSubmitting}
              />
              {errors.name && <span className="error-text">⚠️ {errors.name}</span>}
              <div className="char-count">
                {formData.name.length}/100 characters
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="alertDescription" className="form-label">
                Research Description *
                <span className="label-hint">Describe your research area or technology focus</span>
              </label>
              <textarea
                id="alertDescription"
                value={formData.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
                onBlur={() => handleBlur('description')}
                placeholder="e.g., Our research focuses on deep learning algorithms for computer vision applications, particularly in medical image analysis and autonomous vehicle perception systems..."
                className={`form-textarea ${errors.description ? 'error' : ''}`}
                rows={4}
                disabled={isSubmitting}
              />
              {errors.description && <span className="error-text">⚠️ {errors.description}</span>}
              <div className="char-count">
                {formData.description.length}/5000 characters
              </div>
            </div>
          </div>

          <div className="form-section">
            <h3>Keywords & Search Terms</h3>
            <p className="section-description">
              Add keywords that describe the technology or patents you want to monitor
            </p>
            
            <div className="keywords-container">
              {formData.keywords.map((keyword, index) => (
                <div key={index} className="keyword-input-group">
                  <div className="keyword-input-wrapper">
                    <Search size={18} />
                    <input
                      type="text"
                      value={keyword}
                      onChange={(e) => handleKeywordChange(index, e.target.value)}
                      onBlur={() => handleBlur('keywords')}
                      placeholder={`Keyword ${index + 1}`}
                      className="keyword-input"
                      disabled={isSubmitting}
                    />
                  </div>
                  {formData.keywords.length > 1 && (
                    <button
                      type="button"
                      className="remove-keyword-btn"
                      onClick={() => removeKeyword(index)}
                      disabled={isSubmitting}
                    >
                      <Trash2 size={16} />
                    </button>
                  )}
                </div>
              ))}
              
              <button
                type="button"
                className="add-keyword-btn"
                onClick={addKeyword}
                disabled={isSubmitting || formData.keywords.length >= 10}
              >
                <Plus size={16} />
                Add Keyword
              </button>
              
              {errors.keywords && <span className="error-text">⚠️ {errors.keywords}</span>}
            </div>
          </div>

          <div className="form-section">
            <h3>Alert Configuration</h3>
            
            <div className="form-group">
              <label className="form-label">
                <Target size={18} />
                Similarity Threshold: {getThresholdLabel(formData.similarityThreshold)}
                <span className="label-hint">
                  How similar patents must be to trigger an alert ({(formData.similarityThreshold * 100).toFixed(0)}%)
                </span>
              </label>
              <div className="threshold-slider-container">
                <input
                  type="range"
                  min="0.5"
                  max="0.95"
                  step="0.05"
                  value={formData.similarityThreshold}
                  onChange={(e) => handleInputChange('similarityThreshold', parseFloat(e.target.value))}
                  className="threshold-slider"
                  disabled={isSubmitting}
                />
                <div className="threshold-labels">
                  <span>50%</span>
                  <span>95%</span>
                </div>
              </div>
              <div className="threshold-explanation">
                <div className="threshold-guide">
                  <div className="guide-item">
                    <span className="guide-dot high"></span>
                    <span>High (80-95%): Very similar patents only</span>
                  </div>
                  <div className="guide-item">
                    <span className="guide-dot medium"></span>
                    <span>Medium (70-80%): Moderately similar patents</span>
                  </div>
                  <div className="guide-item">
                    <span className="guide-dot low"></span>
                    <span>Low (50-70%): Broadly related patents</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">
                Check Frequency
                <span className="label-hint">How often to check for new patents</span>
              </label>
              <select
                value={formData.frequency}
                onChange={(e) => handleInputChange('frequency', e.target.value)}
                className="form-select"
                disabled={isSubmitting}
              >
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">
                Lookback Period
                <span className="label-hint">How many days back to search for patents</span>
              </label>
              <select
                value={formData.lookbackDays}
                onChange={(e) => handleInputChange('lookbackDays', parseInt(e.target.value))}
                className="form-select"
                disabled={isSubmitting}
              >
                <option value={7}>Last 7 days</option>
                <option value={14}>Last 2 weeks</option>
                <option value={30}>Last 30 days</option>
                <option value={60}>Last 2 months</option>
                <option value={90}>Last 3 months</option>
              </select>
            </div>
          </div>

          <div className="form-section">
            <h3>Patent Sources</h3>
            <p className="section-description">
              Select which patent databases to monitor
            </p>
            
            <div className="sources-grid">
              {sourceOptions.map((source) => (
                <label key={source.id} className="source-checkbox">
                  <input
                    type="checkbox"
                    checked={formData.sources.includes(source.id)}
                    onChange={() => handleSourceToggle(source.id)}
                    disabled={isSubmitting}
                  />
                  <div className="checkbox-content">
                    <div className="source-name">{source.name}</div>
                    <div className="source-description">{source.description}</div>
                  </div>
                </label>
              ))}
            </div>
          </div>

          <div className="modal-footer">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={onClose}
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className={`btn btn-primary ${!isFormValid ? 'disabled' : ''}`}
              disabled={!isFormValid || isSubmitting}
            >
              {isSubmitting ? (
                <>
                  <LoadingSpinner size="small" />
                  Creating Alert...
                </>
              ) : (
                <>
                  <Bell size={18} />
                  Create Alert
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default CreateAlertModal