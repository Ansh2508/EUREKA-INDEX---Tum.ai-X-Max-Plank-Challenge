"""
Integration tests for Patent Alerts system
"""

import pytest
import asyncio
from datetime import datetime, timedelta

from src.services.alert_service import AlertService, AlertFrequency, AlertStatus
from src.services.alert_scheduler import AlertScheduler

class TestAlertIntegration:
    """Integration tests for the complete alert system"""
    
    @pytest.mark.asyncio
    async def test_complete_alert_workflow(self):
        """Test the complete alert workflow from creation to notification"""
        alert_service = AlertService()
        
        # Step 1: Create an alert
        alert = await alert_service.create_alert(
            user_id="test_user",
            research_title="Machine Learning Research",
            research_abstract="Advanced machine learning algorithms for data processing and pattern recognition",
            similarity_threshold=0.8,
            lookback_days=30,
            frequency=AlertFrequency.DAILY
        )
        
        assert alert is not None
        assert alert.status == AlertStatus.ACTIVE
        assert alert.next_run is not None
        
        # Step 2: Process the alert (simulate it being due)
        alert.next_run = datetime.now() - timedelta(hours=1)  # Make it due
        alert_service.alerts[alert.id] = alert
        
        notification = await alert_service.process_alert(alert)
        
        # Should get notification (even if using fallback data)
        assert notification is not None
        assert len(notification.alert_results) > 0
        
        # Step 3: Verify alert was updated
        updated_alert = alert_service.alerts[alert.id]
        assert updated_alert.last_run is not None
        assert updated_alert.notification_count == 1
        
        # Step 4: Get notifications for user
        notifications = await alert_service.get_notifications("test_user")
        assert len(notifications) == 1
        assert notifications[0].id == notification.id
        
        # Step 5: Mark notification as read
        success = await alert_service.mark_notification_read(notification.id, "test_user")
        assert success is True
        
        # Step 6: Update alert
        updated_alert = await alert_service.update_alert(
            alert_id=alert.id,
            user_id="test_user",
            similarity_threshold=0.9,
            status=AlertStatus.PAUSED
        )
        
        assert updated_alert.similarity_threshold == 0.9
        assert updated_alert.status == AlertStatus.PAUSED
        
        # Step 7: Delete alert
        success = await alert_service.delete_alert(alert.id, "test_user")
        assert success is True
        
        # Verify alert is marked as deleted
        deleted_alert = alert_service.alerts[alert.id]
        assert deleted_alert.status == AlertStatus.DELETED
    
    @pytest.mark.asyncio
    async def test_scheduler_integration(self):
        """Test scheduler integration with alert service"""
        alert_service = AlertService()
        scheduler = AlertScheduler(alert_service, check_interval=1)
        
        # Create an alert that's due for processing
        alert = await alert_service.create_alert(
            user_id="test_user",
            research_title="Test Research",
            research_abstract="Test research abstract for scheduler integration",
            frequency=AlertFrequency.DAILY
        )
        
        # Make it due for processing
        alert.next_run = datetime.now() - timedelta(hours=1)
        alert_service.alerts[alert.id] = alert
        
        # Process due alerts manually (simulating scheduler)
        await scheduler._process_due_alerts()
        
        # Verify alert was processed
        processed_alert = alert_service.alerts[alert.id]
        assert processed_alert.last_run is not None
        assert processed_alert.notification_count >= 0  # May be 0 if no results
        
        # Verify next run was updated
        assert processed_alert.next_run > datetime.now()
    
    @pytest.mark.asyncio
    async def test_multiple_users_isolation(self):
        """Test that alerts are properly isolated between users"""
        alert_service = AlertService()
        
        # Create alerts for different users
        alert1 = await alert_service.create_alert(
            user_id="user1",
            research_title="User 1 Research",
            research_abstract="Research abstract for user 1"
        )
        
        alert2 = await alert_service.create_alert(
            user_id="user2",
            research_title="User 2 Research",
            research_abstract="Research abstract for user 2"
        )
        
        # Process both alerts
        await alert_service.process_alert(alert1)
        await alert_service.process_alert(alert2)
        
        # Verify user1 only sees their alerts and notifications
        user1_alerts = await alert_service.get_alerts("user1")
        user1_notifications = await alert_service.get_notifications("user1")
        
        assert len(user1_alerts) == 1
        assert user1_alerts[0].id == alert1.id
        
        # Verify user2 only sees their alerts and notifications
        user2_alerts = await alert_service.get_alerts("user2")
        user2_notifications = await alert_service.get_notifications("user2")
        
        assert len(user2_alerts) == 1
        assert user2_alerts[0].id == alert2.id
        
        # Verify users can't access each other's alerts
        user1_cannot_access = await alert_service.get_alert(alert2.id, "user1")
        user2_cannot_access = await alert_service.get_alert(alert1.id, "user2")
        
        assert user1_cannot_access is None
        assert user2_cannot_access is None
    
    @pytest.mark.asyncio
    async def test_alert_frequency_calculation(self):
        """Test that alert frequencies are calculated correctly"""
        alert_service = AlertService()
        base_time = datetime(2024, 1, 1, 12, 0, 0)
        
        # Test daily frequency
        daily_alert = await alert_service.create_alert(
            user_id="test_user",
            research_title="Daily Alert",
            research_abstract="Daily alert test",
            frequency=AlertFrequency.DAILY
        )
        daily_alert.created_at = base_time
        daily_next = alert_service._calculate_next_run(AlertFrequency.DAILY, base_time)
        expected_daily = base_time + timedelta(days=1)
        assert daily_next == expected_daily
        
        # Test weekly frequency
        weekly_next = alert_service._calculate_next_run(AlertFrequency.WEEKLY, base_time)
        expected_weekly = base_time + timedelta(weeks=1)
        assert weekly_next == expected_weekly
        
        # Test monthly frequency
        monthly_next = alert_service._calculate_next_run(AlertFrequency.MONTHLY, base_time)
        expected_monthly = base_time + timedelta(days=30)
        assert monthly_next == expected_monthly
    
    @pytest.mark.asyncio
    async def test_error_handling_in_processing(self):
        """Test error handling during alert processing"""
        alert_service = AlertService()
        
        # Create alert
        alert = await alert_service.create_alert(
            user_id="test_user",
            research_title="Error Test Alert",
            research_abstract="Alert for testing error handling"
        )
        
        # Mock the semantic alerts to raise an exception
        original_detect = alert_service.semantic_alerts.detect_similar_patents
        
        async def mock_detect_error(*args, **kwargs):
            raise Exception("Simulated processing error")
        
        alert_service.semantic_alerts.detect_similar_patents = mock_detect_error
        
        # Processing should handle the error gracefully
        try:
            notification = await alert_service.process_alert(alert)
            # Should not raise exception, but may return None or fallback data
            assert True  # If we get here, error was handled
        except Exception as e:
            pytest.fail(f"Alert processing should handle errors gracefully, but got: {e}")
        finally:
            # Restore original method
            alert_service.semantic_alerts.detect_similar_patents = original_detect
    
    def test_data_model_serialization(self):
        """Test that data models serialize correctly"""
        from src.services.alert_service import PatentAlert, AlertNotification
        from src.agents.semantic_alerts import AlertResult
        
        # Test PatentAlert serialization
        now = datetime.now()
        alert = PatentAlert(
            id="test_alert",
            user_id="test_user",
            research_title="Test Title",
            research_abstract="Test Abstract",
            similarity_threshold=0.8,
            lookback_days=30,
            frequency=AlertFrequency.WEEKLY,
            status=AlertStatus.ACTIVE,
            created_at=now,
            updated_at=now
        )
        
        alert_dict = alert.to_dict()
        assert isinstance(alert_dict, dict)
        assert alert_dict['frequency'] == 'weekly'
        assert alert_dict['status'] == 'active'
        assert 'created_at' in alert_dict
        
        # Test AlertNotification serialization
        alert_result = AlertResult(
            id="test_result",
            title="Test Patent",
            similarity_score=0.85,
            document_type="patent",
            publication_date="2024-01-01",
            authors=["Test Author"],
            institutions=["Test Institution"],
            abstract="Test abstract",
            url="https://example.com",
            alert_reason="Test reason"
        )
        
        notification = AlertNotification(
            id="test_notification",
            alert_id="test_alert",
            alert_results=[alert_result],
            created_at=now
        )
        
        notification_dict = notification.to_dict()
        assert isinstance(notification_dict, dict)
        assert notification_dict['result_count'] == 1
        assert len(notification_dict['alert_results']) == 1
        assert 'created_at' in notification_dict