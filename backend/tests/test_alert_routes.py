"""
Unit tests for Alert API routes
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from src.services.alert_service import AlertService, PatentAlert, AlertFrequency, AlertStatus
from src.agents.semantic_alerts import AlertResult

@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)

@pytest.fixture
def mock_alert_service():
    """Create mock AlertService"""
    return Mock(spec=AlertService)

@pytest.fixture
def sample_alert():
    """Create sample PatentAlert"""
    now = datetime.now()
    return PatentAlert(
        id="alert_123",
        user_id="user_123",
        research_title="Test Research",
        research_abstract="Test abstract for research",
        similarity_threshold=0.8,
        lookback_days=30,
        frequency=AlertFrequency.WEEKLY,
        status=AlertStatus.ACTIVE,
        created_at=now,
        updated_at=now,
        notification_count=0
    )

@pytest.fixture
def sample_alert_result():
    """Create sample AlertResult"""
    return AlertResult(
        id="US123456789",
        title="Test Patent",
        similarity_score=0.85,
        document_type="patent",
        publication_date="2024-01-15",
        authors=["John Doe"],
        institutions=["TechCorp Inc."],
        abstract="Test patent abstract",
        url="https://example.com/patent",
        alert_reason="High similarity"
    )

class TestAlertRoutes:
    """Test cases for Alert API routes"""
    
    @patch('src.routes.alerts.alert_service')
    def test_create_alert_success(self, mock_service, client, sample_alert):
        """Test successful alert creation"""
        mock_service.create_alert = AsyncMock(return_value=sample_alert)
        
        request_data = {
            "research_title": "Test Research",
            "research_abstract": "Test abstract for research",
            "similarity_threshold": 0.8,
            "lookback_days": 30,
            "frequency": "weekly"
        }
        
        response = client.post("/api/alerts/create", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "alert_123"
        assert data["research_title"] == "Test Research"
        assert data["frequency"] == "weekly"
        assert data["status"] == "active"
    
    @patch('src.routes.alerts.alert_service')
    def test_create_alert_invalid_frequency(self, mock_service, client):
        """Test alert creation with invalid frequency"""
        request_data = {
            "research_title": "Test Research",
            "research_abstract": "Test abstract for research",
            "frequency": "invalid_frequency"
        }
        
        response = client.post("/api/alerts/create", json=request_data)
        
        assert response.status_code == 422  # Validation error
    
    @patch('src.routes.alerts.alert_service')
    def test_create_alert_missing_fields(self, mock_service, client):
        """Test alert creation with missing required fields"""
        request_data = {
            "research_title": "Test Research"
            # Missing research_abstract
        }
        
        response = client.post("/api/alerts/create", json=request_data)
        
        assert response.status_code == 422  # Validation error
    
    @patch('src.routes.alerts.alert_service')
    def test_list_alerts_success(self, mock_service, client, sample_alert):
        """Test successful alert listing"""
        mock_service.get_alerts = AsyncMock(return_value=[sample_alert])
        
        response = client.get("/api/alerts/list")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == "alert_123"
        assert data[0]["research_title"] == "Test Research"
    
    @patch('src.routes.alerts.alert_service')
    def test_list_alerts_empty(self, mock_service, client):
        """Test alert listing with no alerts"""
        mock_service.get_alerts = AsyncMock(return_value=[])
        
        response = client.get("/api/alerts/list")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
    
    @patch('src.routes.alerts.alert_service')
    def test_get_alert_success(self, mock_service, client, sample_alert):
        """Test successful alert retrieval"""
        mock_service.get_alert = AsyncMock(return_value=sample_alert)
        
        response = client.get("/api/alerts/alert_123")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "alert_123"
        assert data["research_title"] == "Test Research"
    
    @patch('src.routes.alerts.alert_service')
    def test_get_alert_not_found(self, mock_service, client):
        """Test alert retrieval when alert doesn't exist"""
        mock_service.get_alert = AsyncMock(return_value=None)
        
        response = client.get("/api/alerts/nonexistent_id")
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    @patch('src.routes.alerts.alert_service')
    def test_update_alert_success(self, mock_service, client, sample_alert):
        """Test successful alert update"""
        updated_alert = sample_alert
        updated_alert.research_title = "Updated Research Title"
        mock_service.update_alert = AsyncMock(return_value=updated_alert)
        
        request_data = {
            "research_title": "Updated Research Title",
            "similarity_threshold": 0.9
        }
        
        response = client.put("/api/alerts/alert_123", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["research_title"] == "Updated Research Title"
    
    @patch('src.routes.alerts.alert_service')
    def test_update_alert_not_found(self, mock_service, client):
        """Test alert update when alert doesn't exist"""
        mock_service.update_alert = AsyncMock(return_value=None)
        
        request_data = {
            "research_title": "Updated Research Title"
        }
        
        response = client.put("/api/alerts/nonexistent_id", json=request_data)
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    @patch('src.routes.alerts.alert_service')
    def test_update_alert_invalid_enum(self, mock_service, client):
        """Test alert update with invalid enum value"""
        request_data = {
            "frequency": "invalid_frequency"
        }
        
        response = client.put("/api/alerts/alert_123", json=request_data)
        
        assert response.status_code == 422  # Validation error
    
    @patch('src.routes.alerts.alert_service')
    def test_delete_alert_success(self, mock_service, client):
        """Test successful alert deletion"""
        mock_service.delete_alert = AsyncMock(return_value=True)
        
        response = client.delete("/api/alerts/alert_123")
        
        assert response.status_code == 200
        data = response.json()
        assert "deleted successfully" in data["message"]
        assert data["alert_id"] == "alert_123"
    
    @patch('src.routes.alerts.alert_service')
    def test_delete_alert_not_found(self, mock_service, client):
        """Test alert deletion when alert doesn't exist"""
        mock_service.delete_alert = AsyncMock(return_value=False)
        
        response = client.delete("/api/alerts/nonexistent_id")
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    @patch('src.routes.alerts.alert_service')
    def test_get_notifications_success(self, mock_service, client, sample_alert_result):
        """Test successful notification retrieval"""
        from src.services.alert_service import AlertNotification
        
        notification = AlertNotification(
            id="notif_123",
            alert_id="alert_123",
            alert_results=[sample_alert_result],
            created_at=datetime.now()
        )
        
        mock_service.get_notifications = AsyncMock(return_value=[notification])
        
        response = client.get("/api/alerts/notifications/list")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == "notif_123"
        assert data[0]["alert_id"] == "alert_123"
        assert data[0]["result_count"] == 1
    
    @patch('src.routes.alerts.alert_service')
    def test_get_notifications_with_limit(self, mock_service, client):
        """Test notification retrieval with limit parameter"""
        mock_service.get_notifications = AsyncMock(return_value=[])
        
        response = client.get("/api/alerts/notifications/list?limit=10")
        
        assert response.status_code == 200
        mock_service.get_notifications.assert_called_once_with("demo_user_123", 10)
    
    @patch('src.routes.alerts.alert_service')
    def test_mark_notification_read_success(self, mock_service, client):
        """Test successful notification read marking"""
        mock_service.mark_notification_read = AsyncMock(return_value=True)
        
        response = client.post("/api/alerts/notifications/notif_123/read")
        
        assert response.status_code == 200
        data = response.json()
        assert "marked as read" in data["message"]
        assert data["notification_id"] == "notif_123"
    
    @patch('src.routes.alerts.alert_service')
    def test_mark_notification_read_not_found(self, mock_service, client):
        """Test notification read marking when notification doesn't exist"""
        mock_service.mark_notification_read = AsyncMock(return_value=False)
        
        response = client.post("/api/alerts/notifications/nonexistent_id/read")
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    @patch('src.routes.alerts.alert_service')
    def test_test_alert_success(self, mock_service, client, sample_alert):
        """Test successful alert testing"""
        mock_service.get_alert = AsyncMock(return_value=sample_alert)
        
        response = client.post("/api/alerts/alert_123/test")
        
        assert response.status_code == 200
        data = response.json()
        assert "test started" in data["message"]
        assert data["alert_id"] == "alert_123"
        assert data["status"] == "processing"
    
    @patch('src.routes.alerts.alert_service')
    def test_test_alert_not_found(self, mock_service, client):
        """Test alert testing when alert doesn't exist"""
        mock_service.get_alert = AsyncMock(return_value=None)
        
        response = client.post("/api/alerts/nonexistent_id/test")
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    @patch('src.routes.alerts.alert_service')
    def test_get_alert_stats_success(self, mock_service, client, sample_alert, sample_alert_result):
        """Test successful alert statistics retrieval"""
        from src.services.alert_service import AlertNotification
        
        # Create sample data
        active_alert = sample_alert
        paused_alert = sample_alert
        paused_alert.status = AlertStatus.PAUSED
        
        notification = AlertNotification(
            id="notif_123",
            alert_id="alert_123",
            alert_results=[sample_alert_result],
            created_at=datetime.now(),
            read=False
        )
        
        mock_service.get_alerts = AsyncMock(return_value=[active_alert, paused_alert])
        mock_service.get_notifications = AsyncMock(return_value=[notification])
        
        response = client.get("/api/alerts/stats/summary")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_alerts"] == 2
        assert data["active_alerts"] == 1
        assert data["paused_alerts"] == 1
        assert data["total_notifications"] == 1
        assert data["unread_notifications"] == 1
    
    @patch('src.routes.alerts.alert_service')
    def test_get_alert_stats_no_data(self, mock_service, client):
        """Test alert statistics with no data"""
        mock_service.get_alerts = AsyncMock(return_value=[])
        mock_service.get_notifications = AsyncMock(return_value=[])
        
        response = client.get("/api/alerts/stats/summary")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_alerts"] == 0
        assert data["active_alerts"] == 0
        assert data["paused_alerts"] == 0
        assert data["total_notifications"] == 0
        assert data["unread_notifications"] == 0
        assert data["last_notification"] is None
    
    @patch('src.routes.alerts.alert_service')
    def test_service_error_handling(self, mock_service, client):
        """Test error handling when service raises exception"""
        mock_service.get_alerts = AsyncMock(side_effect=Exception("Service error"))
        
        response = client.get("/api/alerts/list")
        
        assert response.status_code == 500
        data = response.json()
        assert "Failed to retrieve alerts" in data["detail"]
    
    def test_validation_errors(self, client):
        """Test various validation errors"""
        # Test empty research title
        response = client.post("/api/alerts/create", json={
            "research_title": "",
            "research_abstract": "Valid abstract"
        })
        assert response.status_code == 422
        
        # Test short research abstract
        response = client.post("/api/alerts/create", json={
            "research_title": "Valid title",
            "research_abstract": "Short"
        })
        assert response.status_code == 422
        
        # Test invalid similarity threshold
        response = client.post("/api/alerts/create", json={
            "research_title": "Valid title",
            "research_abstract": "Valid abstract with enough length",
            "similarity_threshold": 1.5  # > 1.0
        })
        assert response.status_code == 422
        
        # Test invalid lookback days
        response = client.post("/api/alerts/create", json={
            "research_title": "Valid title",
            "research_abstract": "Valid abstract with enough length",
            "lookback_days": 0  # < 1
        })
        assert response.status_code == 422