/**
 * Alert Service - API client for patent alerts
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

class AlertService {
    constructor() {
        this.baseURL = `${API_BASE_URL}/api/alerts`
    }

    async createAlert(alertData) {
        const response = await fetch(`${this.baseURL}/create`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                research_title: alertData.name,
                research_abstract: alertData.description || alertData.name,
                similarity_threshold: alertData.similarityThreshold,
                lookback_days: alertData.lookbackDays || 30,
                frequency: alertData.frequency || 'weekly'
            })
        })

        if (!response.ok) {
            const error = await response.json()
            throw new Error(error.detail || 'Failed to create alert')
        }

        return response.json()
    }

    async getAlerts() {
        const response = await fetch(`${this.baseURL}/list`)

        if (!response.ok) {
            const error = await response.json()
            throw new Error(error.detail || 'Failed to fetch alerts')
        }

        return response.json()
    }

    async getAlert(alertId) {
        const response = await fetch(`${this.baseURL}/${alertId}`)

        if (!response.ok) {
            const error = await response.json()
            throw new Error(error.detail || 'Failed to fetch alert')
        }

        return response.json()
    }

    async updateAlert(alertId, updates) {
        const response = await fetch(`${this.baseURL}/${alertId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                research_title: updates.name,
                research_abstract: updates.description,
                similarity_threshold: updates.similarityThreshold,
                lookback_days: updates.lookbackDays,
                frequency: updates.frequency,
                status: updates.status
            })
        })

        if (!response.ok) {
            const error = await response.json()
            throw new Error(error.detail || 'Failed to update alert')
        }

        return response.json()
    }

    async deleteAlert(alertId) {
        const response = await fetch(`${this.baseURL}/${alertId}`, {
            method: 'DELETE'
        })

        if (!response.ok) {
            const error = await response.json()
            throw new Error(error.detail || 'Failed to delete alert')
        }

        return response.json()
    }

    async getNotifications(limit = 50) {
        const response = await fetch(`${this.baseURL}/notifications/list?limit=${limit}`)

        if (!response.ok) {
            const error = await response.json()
            throw new Error(error.detail || 'Failed to fetch notifications')
        }

        return response.json()
    }

    async markNotificationRead(notificationId) {
        const response = await fetch(`${this.baseURL}/notifications/${notificationId}/read`, {
            method: 'POST'
        })

        if (!response.ok) {
            const error = await response.json()
            throw new Error(error.detail || 'Failed to mark notification as read')
        }

        return response.json()
    }

    async testAlert(alertId) {
        const response = await fetch(`${this.baseURL}/${alertId}/test`, {
            method: 'POST'
        })

        if (!response.ok) {
            const error = await response.json()
            throw new Error(error.detail || 'Failed to test alert')
        }

        return response.json()
    }

    async getAlertStats() {
        const response = await fetch(`${this.baseURL}/stats/summary`)

        if (!response.ok) {
            const error = await response.json()
            throw new Error(error.detail || 'Failed to fetch alert stats')
        }

        return response.json()
    }

    // Transform backend alert format to frontend format
    transformAlert(backendAlert) {
        return {
            id: backendAlert.id,
            name: backendAlert.research_title,
            keywords: backendAlert.research_abstract.split(' ').slice(0, 5), // Extract keywords from abstract
            description: backendAlert.research_abstract,
            similarityThreshold: backendAlert.similarity_threshold,
            lookbackDays: backendAlert.lookback_days,
            frequency: backendAlert.frequency,
            status: backendAlert.status,
            createdAt: new Date(backendAlert.created_at),
            updatedAt: new Date(backendAlert.updated_at),
            lastTriggered: backendAlert.last_run ? new Date(backendAlert.last_run) : null,
            nextRun: backendAlert.next_run ? new Date(backendAlert.next_run) : null,
            notificationCount: backendAlert.notification_count
        }
    }

    // Transform backend notification format to frontend format
    transformNotification(backendNotification) {
        return {
            id: backendNotification.id,
            alertId: backendNotification.alert_id,
            alertName: `Alert ${backendNotification.alert_id}`, // Will be populated from alert data
            patentTitle: backendNotification.alert_results[0]?.patent_title || 'Patent Found',
            patentId: backendNotification.alert_results[0]?.patent_id || 'Unknown',
            similarityScore: backendNotification.alert_results[0]?.similarity_score || 0,
            timestamp: new Date(backendNotification.created_at),
            read: backendNotification.read,
            resultCount: backendNotification.result_count
        }
    }
}

export default new AlertService()