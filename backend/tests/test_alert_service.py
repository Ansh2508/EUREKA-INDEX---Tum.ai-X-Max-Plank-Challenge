"""
Unit tests for AlertService
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock

from src.services.alert_service import (
    AlertService, 
    PatentAlert, 
    AlertNotification,
    AlertFrequency, 
    AlertStatus
)
from src.agents.semantic_alerts import AlertResult

@pytest.fixture
def alert_service():
    """Create AlertService instance for testing"""
    return AlertService()

@pytest.fixture
def sample_alert_result():
    """Create sample AlertResult for testing"""
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

class TestAlertService:
    """Test cases for AlertService"""
    
    @pytest.mark.asyncio
    async def test_create_alert(self, alert_service):
        """Test creating a new alert"""
        alert = await alert_service.create_alert(
            user_id="user123",
            research_title="Test Research",
            research_abstract="This is a test research abstract",
            similarity_threshold=0.8,
            lookback_days=14,
            frequency=AlertFrequency.DAILY
        )
        
        assert alert.user_id == "user123"
        assert alert.research_title == "Test Research"
        assert alert.research_abstract == "This is a test research abstract"
        assert alert.similarity_threshold == 0.8
        assert alert.lookback_days == 14
        assert alert.frequency == AlertFrequency.DAILY
        assert alert.status == AlertStatus.ACTIVE
        assert alert.next_run is not None
        assert alert.notification_count == 0
        
        # Verify alert is stored
        assert alert.id in alert_service.alerts
    
    @pytest.mark.asyncio
    async def test_get_alerts(self, alert_service):
        """Test getting alerts for a user"""
        # Create multiple alerts
        alert1 = await alert_service.create_alert(
            user_id="user123",
            research_title="Research 1",
            research_abstract="Abstract 1"
        )
        
        alert2 = await alert_service.create_alert(
            user_id="user123",
            research_title="Research 2",
            research_abstract="Abstract 2"
        )
        
        # Create alert for different user
        await alert_service.create_alert(
            user_id="user456",
            research_title="Research 3",
            research_abstract="Abstract 3"
        )
        
        # Get alerts for user123
        user_alerts = await alert_service.get_alerts("user123")
        
        assert len(user_alerts) == 2
        alert_ids = [alert.id for alert in user_alerts]
        assert alert1.id in alert_ids
        assert alert2.id in alert_ids
    
    @pytest.mark.asyncio
    async def test_get_alert(self, alert_service):
        """Test getting a specific alert"""
        alert = await alert_service.create_alert(
            user_id="user123",
            research_title="Test Research",
            research_abstract="Test abstract"
        )
        
        # Get existing alert
        retrieved_alert = await alert_service.get_alert(alert.id, "user123")
        assert retrieved_alert is not None
        assert retrieved_alert.id == alert.id
        
        # Try to get alert with wrong user
        wrong_user_alert = await alert_service.get_alert(alert.id, "user456")
        assert wrong_user_alert is None
        
        # Try to get non-existent alert
        non_existent = await alert_service.get_alert("fake_id", "user123")
        assert non_existent is None
    
    @pytest.mark.asyncio
    async def test_update_alert(self, alert_service):
        """Test updating an alert"""
        alert = await alert_service.create_alert(
            user_id="user123",
            research_title="Original Title",
            research_abstract="Original abstract"
        )
        
        # Update alert
        updated_alert = await alert_service.update_alert(
            alert_id=alert.id,
            user_id="user123",
            research_title="Updated Title",
            similarity_threshold=0.9,
            frequency=AlertFrequency.MONTHLY
        )
        
        assert updated_alert is not None
        assert updated_alert.research_title == "Updated Title"
        assert updated_alert.research_abstract == "Original abstract"  # Unchanged
        assert updated_alert.similarity_threshold == 0.9
        assert updated_alert.frequency == AlertFrequency.MONTHLY
        
        # Try to update non-existent alert
        non_existent = await alert_service.update_alert(
            alert_id="fake_id",
            user_id="user123",
            research_title="New Title"
        )
        assert non_existent is None
    
    @pytest.mark.asyncio
    async def test_delete_alert(self, alert_service):
        """Test deleting an alert"""
        alert = await alert_service.create_alert(
            user_id="user123",
            research_title="Test Research",
            research_abstract="Test abstract"
        )
        
        # Delete alert
        success = await alert_service.delete_alert(alert.id, "user123")
        assert success is True
        
        # Verify alert is marked as deleted
        deleted_alert = alert_service.alerts[alert.id]
        assert deleted_alert.status == AlertStatus.DELETED
        
        # Verify alert doesn't appear in user's alerts
        user_alerts = await alert_service.get_alerts("user123")
        assert len(user_alerts) == 0
        
        # Try to delete non-existent alert
        success = await alert_service.delete_alert("fake_id", "user123")
        assert success is False
    
    @pytest.mark.asyncio
    async def test_process_alert(self, alert_service, sample_alert_result):
        """Test processing an alert"""
        alert = await alert_service.create_alert(
            user_id="user123",
            research_title="Test Research",
            research_abstract="Test abstract"
        )
        
        # Mock the semantic alerts service
        with patch.object(alert_service.semantic_alerts, 'detect_similar_patents') as mock_detect:
            mock_detect.return_value = [sample_alert_result]
            
            notification = await alert_service.process_alert(alert)
            
            assert notification is not None
            assert notification.alert_id == alert.id
            assert len(notification.alert_results) == 1
            assert notification.alert_results[0] == sample_alert_result
            
            # Verify alert was updated
            updated_alert = alert_service.alerts[alert.id]
            assert updated_alert.last_run is not None
            assert updated_alert.next_run is not None
            assert updated_alert.notification_count == 1
    
    @pytest.mark.asyncio
    async def test_process_alert_no_results(self, alert_service):
        """Test processing an alert with no results"""
        alert = await alert_service.create_alert(
            user_id="user123",
            research_title="Test Research",
            research_abstract="Test abstract"
        )
        
        # Mock the semantic alerts service to return no results
        with patch.object(alert_service.semantic_alerts, 'detect_similar_patents') as mock_detect:
            mock_detect.return_value = []
            
            notification = await alert_service.process_alert(alert)
            
            assert notification is None
            
            # Verify alert was still updated
            updated_alert = alert_service.alerts[alert.id]
            assert updated_alert.last_run is not None
            assert updated_alert.next_run is not None
            assert updated_alert.notification_count == 0
    
    @pytest.mark.asyncio
    async def test_process_paused_alert(self, alert_service):
        """Test processing a paused alert"""
        alert = await alert_service.create_alert(
            user_id="user123",
            research_title="Test Research",
            research_abstract="Test abstract"
        )
        
        # Pause the alert
        await alert_service.update_alert(
            alert_id=alert.id,
            user_id="user123",
            status=AlertStatus.PAUSED
        )
        
        notification = await alert_service.process_alert(alert_service.alerts[alert.id])
        assert notification is None
    
    @pytest.mark.asyncio
    async def test_get_notifications(self, alert_service, sample_alert_result):
        """Test getting notifications for a user"""
        # Create alerts for different users
        alert1 = await alert_service.create_alert(
            user_id="user123",
            research_title="Research 1",
            research_abstract="Abstract 1"
        )
        
        alert2 = await alert_service.create_alert(
            user_id="user456",
            research_title="Research 2",
            research_abstract="Abstract 2"
        )
        
        # Mock processing to create notifications
        with patch.object(alert_service.semantic_alerts, 'detect_similar_patents') as mock_detect:
            mock_detect.return_value = [sample_alert_result]
            
            # Process alerts
            await alert_service.process_alert(alert1)
            await alert_service.process_alert(alert2)
        
        # Get notifications for user123
        notifications = await alert_service.get_notifications("user123")
        
        assert len(notifications) == 1
        assert notifications[0].alert_id == alert1.id
        
        # Get notifications for user456
        notifications = await alert_service.get_notifications("user456")
        
        assert len(notifications) == 1
        assert notifications[0].alert_id == alert2.id
    
    @pytest.mark.asyncio
    async def test_mark_notification_read(self, alert_service, sample_alert_result):
        """Test marking a notification as read"""
        alert = await alert_service.create_alert(
            user_id="user123",
            research_title="Test Research",
            research_abstract="Test abstract"
        )
        
        # Create notification
        with patch.object(alert_service.semantic_alerts, 'detect_similar_patents') as mock_detect:
            mock_detect.return_value = [sample_alert_result]
            notification = await alert_service.process_alert(alert)
        
        assert notification.read is False
        
        # Mark as read
        success = await alert_service.mark_notification_read(notification.id, "user123")
        assert success is True
        
        # Verify notification is marked as read
        updated_notification = alert_service.notifications[notification.id]
        assert updated_notification.read is True
        
        # Try to mark notification with wrong user
        success = await alert_service.mark_notification_read(notification.id, "user456")
        assert success is False
    
    @pytest.mark.asyncio
    async def test_get_alerts_due_for_processing(self, alert_service):
        """Test getting alerts due for processing"""
        # Create alert with next_run in the past
        alert1 = await alert_service.create_alert(
            user_id="user123",
            research_title="Past Due Alert",
            research_abstract="Abstract 1"
        )
        alert1.next_run = datetime.now() - timedelta(hours=1)
        alert_service.alerts[alert1.id] = alert1
        
        # Create alert with next_run in the future
        alert2 = await alert_service.create_alert(
            user_id="user123",
            research_title="Future Alert",
            research_abstract="Abstract 2"
        )
        alert2.next_run = datetime.now() + timedelta(hours=1)
        alert_service.alerts[alert2.id] = alert2
        
        # Create paused alert with next_run in the past
        alert3 = await alert_service.create_alert(
            user_id="user123",
            research_title="Paused Alert",
            research_abstract="Abstract 3"
        )
        alert3.next_run = datetime.now() - timedelta(hours=1)
        alert3.status = AlertStatus.PAUSED
        alert_service.alerts[alert3.id] = alert3
        
        due_alerts = await alert_service.get_alerts_due_for_processing()
        
        assert len(due_alerts) == 1
        assert due_alerts[0].id == alert1.id
    
    def test_calculate_next_run(self, alert_service):
        """Test calculating next run times"""
        base_time = datetime(2024, 1, 1, 12, 0, 0)
        
        # Test daily frequency
        next_run = alert_service._calculate_next_run(AlertFrequency.DAILY, base_time)
        expected = base_time + timedelta(days=1)
        assert next_run == expected
        
        # Test weekly frequency
        next_run = alert_service._calculate_next_run(AlertFrequency.WEEKLY, base_time)
        expected = base_time + timedelta(weeks=1)
        assert next_run == expected
        
        # Test monthly frequency
        next_run = alert_service._calculate_next_run(AlertFrequency.MONTHLY, base_time)
        expected = base_time + timedelta(days=30)
        assert next_run == expected
    
    def test_alert_to_dict(self, alert_service):
        """Test converting alert to dictionary"""
        now = datetime.now()
        alert = PatentAlert(
            id="test_id",
            user_id="user123",
            research_title="Test Title",
            research_abstract="Test Abstract",
            similarity_threshold=0.8,
            lookback_days=30,
            frequency=AlertFrequency.WEEKLY,
            status=AlertStatus.ACTIVE,
            created_at=now,
            updated_at=now,
            last_run=now,
            next_run=now + timedelta(days=7),
            notification_count=5
        )
        
        alert_dict = alert.to_dict()
        
        assert alert_dict['id'] == "test_id"
        assert alert_dict['user_id'] == "user123"
        assert alert_dict['research_title'] == "Test Title"
        assert alert_dict['frequency'] == "weekly"
        assert alert_dict['status'] == "active"
        assert alert_dict['notification_count'] == 5
        assert 'created_at' in alert_dict
        assert 'updated_at' in alert_dict
        assert 'last_run' in alert_dict
        assert 'next_run' in alert_dict
    
    def test_notification_to_dict(self, sample_alert_result):
        """Test converting notification to dictionary"""
        now = datetime.now()
        notification = AlertNotification(
            id="notif_id",
            alert_id="alert_id",
            alert_results=[sample_alert_result],
            created_at=now,
            read=True
        )
        
        notif_dict = notification.to_dict()
        
        assert notif_dict['id'] == "notif_id"
        assert notif_dict['alert_id'] == "alert_id"
        assert notif_dict['result_count'] == 1
        assert notif_dict['read'] is True
        assert 'created_at' in notif_dict
        assert 'alert_results' in notif_dict
        assert len(notif_dict['alert_results']) == 1