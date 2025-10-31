/**
 * Research Analysis Service
 * Handles API communication for research analysis functionality
 * Integrates with LogicMill API and Google AI backend services
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

class ResearchAnalysisService {
    constructor() {
        this.baseURL = API_BASE_URL
    }

    /**
     * Submit research for comprehensive analysis
     * @param {Object} researchData - Research title and abstract
     * @returns {Promise<Object>} Analysis response with ID
     */
    async submitAnalysis(researchData) {
        try {
            const response = await fetch(`${this.baseURL}/research/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    title: researchData.title,
                    abstract: researchData.abstract
                }),
            })

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}))
                throw new Error(
                    errorData.detail?.errors?.join(', ') ||
                    errorData.detail ||
                    `Analysis submission failed (${response.status})`
                )
            }

            return await response.json()
        } catch (error) {
            console.error('Error submitting analysis:', error)
            throw error
        }
    }

    /**
     * Get analysis results by ID
     * @param {string} analysisId - Analysis ID
     * @returns {Promise<Object>} Analysis results
     */
    async getAnalysisResults(analysisId) {
        try {
            const response = await fetch(`${this.baseURL}/research/results/${analysisId}`)

            if (!response.ok) {
                throw new Error(`Failed to get results (${response.status})`)
            }

            return await response.json()
        } catch (error) {
            console.error('Error getting analysis results:', error)
            throw error
        }
    }

    /**
     * Search for similar patents and publications using LogicMill API
     * @param {Object} searchData - Research title and abstract
     * @param {number} amount - Number of results to return
     * @returns {Promise<Object>} Similarity search results
     */
    async searchSimilarDocuments(searchData, amount = 25) {
        try {
            const response = await fetch(`${this.baseURL}/research/similarity-search`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    title: searchData.title,
                    abstract: searchData.abstract,
                    amount: amount
                }),
            })

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}))
                throw new Error(
                    errorData.detail?.errors?.join(', ') ||
                    errorData.detail ||
                    `Similarity search failed (${response.status})`
                )
            }

            return await response.json()
        } catch (error) {
            console.error('Error in similarity search:', error)
            throw error
        }
    }

    /**
     * Get AI-powered research insights using Google AI
     * @param {Object} researchData - Research title and abstract
     * @param {string} analysisType - Type of analysis (novelty, claims, landscape, etc.)
     * @returns {Promise<Object>} AI analysis results
     */
    async getAIInsights(researchData, analysisType = 'novelty') {
        try {
            const response = await fetch(`${this.baseURL}/research/ai-insights`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    title: researchData.title,
                    abstract: researchData.abstract,
                    analysis_type: analysisType
                }),
            })

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}))
                throw new Error(
                    errorData.detail ||
                    `AI insights failed (${response.status})`
                )
            }

            return await response.json()
        } catch (error) {
            console.error('Error getting AI insights:', error)
            throw error
        }
    }

    /**
     * Get analysis history for the user
     * @returns {Promise<Object>} Analysis history
     */
    async getAnalysisHistory() {
        try {
            const response = await fetch(`${this.baseURL}/research/history`)

            if (!response.ok) {
                throw new Error(`Failed to get history (${response.status})`)
            }

            return await response.json()
        } catch (error) {
            console.error('Error getting analysis history:', error)
            throw error
        }
    }

    /**
     * Poll for analysis completion with exponential backoff
     * @param {string} analysisId - Analysis ID
     * @param {number} maxAttempts - Maximum polling attempts
     * @param {Function} onProgress - Progress callback
     * @returns {Promise<Object>} Final analysis results
     */
    async pollForResults(analysisId, maxAttempts = 30, onProgress = null) {
        let attempts = 0
        let delay = 1000 // Start with 1 second

        const poll = async () => {
            try {
                const result = await this.getAnalysisResults(analysisId)

                if (result.status === 'completed' && result.results) {
                    if (onProgress) onProgress(100)
                    return result.results
                } else if (result.status === 'failed') {
                    throw new Error(result.results?.error || 'Analysis failed')
                } else if (result.status === 'processing' || result.status === 'pending') {
                    attempts++

                    if (attempts >= maxAttempts) {
                        throw new Error('Analysis timeout - please try again')
                    }

                    // Update progress based on attempts
                    if (onProgress) {
                        const progress = Math.min(90, (attempts / maxAttempts) * 90)
                        onProgress(progress)
                    }

                    // Exponential backoff with jitter
                    const jitter = Math.random() * 0.1 * delay
                    await new Promise(resolve => setTimeout(resolve, delay + jitter))
                    delay = Math.min(delay * 1.2, 5000) // Max 5 seconds

                    return poll()
                }
            } catch (error) {
                console.error('Polling error:', error)
                throw error
            }
        }

        return poll()
    }

    /**
     * Validate research input
     * @param {Object} researchData - Research data to validate
     * @returns {Object} Validation result
     */
    validateResearchInput(researchData) {
        const errors = []

        if (!researchData.title || researchData.title.trim().length < 5) {
            errors.push('Title must be at least 5 characters long')
        }

        if (!researchData.abstract || researchData.abstract.trim().length < 20) {
            errors.push('Abstract must be at least 20 characters long')
        }

        if (researchData.title && researchData.title.length > 500) {
            errors.push('Title must be less than 500 characters')
        }

        if (researchData.abstract && researchData.abstract.length > 5000) {
            errors.push('Abstract must be less than 5000 characters')
        }

        return {
            valid: errors.length === 0,
            errors
        }
    }
}

// Export singleton instance
export default new ResearchAnalysisService()