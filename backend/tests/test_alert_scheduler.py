"""
Unit tests for AlertScheduler
"""

import pytest
import asyncio
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock

from src.services.alert_scheduler import AlertScheduler
from src.services.alert_service import AlertService, PatentAlert, AlertFrequency, AlertStatus
from src.agents.semantic_alerts import AlertResult

@pytest.fixture
def mock_alert_service():
    """Create mock AlertService"""
    return Mock(spec=AlertService)

@pytest.fixture
def alert_scheduler(mock_alert_service):
    """Create AlertScheduler with mock service"""
    return AlertScheduler(mock_alert_service, check_interval=1)  # 1 second for testing

@pytest.fixture
def sample_alert():
    """Create sample PatentAlert"""
    now = datetime.now()
    return PatentAlert(
        id="alert_123",
        user_id="user_123",
        research_title="Test Research",
        research_abstract="Test abstract",
        similarity_threshold=0.8,
        lookback_days=30,
        frequency=AlertFrequency.WEEKLY,
        status=AlertStatus.ACTIVE,
        created_at=now,
        updated_at=now,
        next_run=now - timedelta(hours=1)  # Due for processing
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

class TestAlertScheduler:
    """Test cases for AlertScheduler"""
    
    def test_scheduler_initialization(self, mock_alert_service):
        """Test scheduler initialization"""
        scheduler = AlertScheduler(mock_alert_service, check_interval=300)
        
        assert scheduler.alert_service == mock_alert_service
        assert scheduler.check_interval == 300
        assert scheduler.running is False
        assert scheduler.scheduler_thread is None
    
    def test_start_scheduler(self, alert_scheduler):
        """Test starting the scheduler"""
        assert alert_scheduler.running is False
        
        alert_scheduler.start()
        
        assert alert_scheduler.running is True
        assert alert_scheduler.scheduler_thread is not None
        assert alert_scheduler.scheduler_thread.is_alive()
        
        # Clean up
        alert_scheduler.stop()
    
    def test_start_scheduler_already_running(self, alert_scheduler):
        """Test starting scheduler when already running"""
        alert_scheduler.start()
        
        # Try to start again
        with patch('logging.Logger.warning') as mock_warning:
            alert_scheduler.start()
            mock_warning.assert_called_once()
        
        # Clean up
        alert_scheduler.stop()
    
    def test_stop_scheduler(self, alert_scheduler):
        """Test stopping the scheduler"""
        alert_scheduler.start()
        assert alert_scheduler.running is True
        
        alert_scheduler.stop()
        
        assert alert_scheduler.running is False
        # Thread should finish within timeout
        time.sleep(0.1)  # Give thread time to finish
    
    def test_stop_scheduler_not_running(self, alert_scheduler):
        """Test stopping scheduler when not running"""
        assert alert_scheduler.running is False
        
        with patch('logging.Logger.warning') as mock_warning:
            alert_scheduler.stop()
            mock_warning.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_due_alerts_no_alerts(self, alert_scheduler):
        """Test processing when no alerts are due"""
        alert_scheduler.alert_service.get_alerts_due_for_processing = AsyncMock(return_value=[])
        
        await alert_scheduler._process_due_alerts()
        
        alert_scheduler.alert_service.get_alerts_due_for_processing.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_due_alerts_with_alerts(self, alert_scheduler, sample_alert, sample_alert_result):
        """Test processing when alerts are due"""
        from src.services.alert_service import AlertNotification
        
        notification = AlertNotification(
            id="notif_123",
            alert_id=sample_alert.id,
            alert_results=[sample_alert_result],
            created_at=datetime.now()
        )
        
        alert_scheduler.alert_service.get_alerts_due_for_processing = AsyncMock(return_value=[sample_alert])
        alert_scheduler.alert_service.process_alert = AsyncMock(return_value=notification)
        
        await alert_scheduler._process_due_alerts()
        
        alert_scheduler.alert_service.get_alerts_due_for_processing.assert_called_once()
        alert_scheduler.alert_service.process_alert.assert_called_once_with(sample_alert)
    
    @pytest.mark.asyncio
    async def test_process_due_alerts_with_multiple_alerts(self, alert_scheduler, sample_alert):
        """Test processing multiple alerts in batches"""
        # Create multiple alerts
        alerts = []
        for i in range(7):  # More than batch size (5)
            alert = PatentAlert(
                id=f"alert_{i}",
                user_id="user_123",
                research_title=f"Research {i}",
                research_abstract="Test abstract",
                similarity_threshold=0.8,
                lookback_days=30,
                frequency=AlertFrequency.WEEKLY,
                status=AlertStatus.ACTIVE,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                next_run=datetime.now() - timedelta(hours=1)
            )
            alerts.append(alert)
        
        alert_scheduler.alert_service.get_alerts_due_for_processing = AsyncMock(return_value=alerts)
        alert_scheduler.alert_service.process_alert = AsyncMock(return_value=None)
        
        await alert_scheduler._process_due_alerts()
        
        # Should process all 7 alerts
        assert alert_scheduler.alert_service.process_alert.call_count == 7
    
    @pytest.mark.asyncio
    async def test_process_alert_batch_success(self, alert_scheduler, sample_alert):
        """Test processing a batch of alerts successfully"""
        alerts = [sample_alert]
        alert_scheduler.alert_service.process_alert = AsyncMock(return_value=None)
        
        await alert_scheduler._process_alert_batch(alerts)
        
        alert_scheduler.alert_service.process_alert.assert_called_once_with(sample_alert)
    
    @pytest.mark.asyncio
    async def test_process_alert_batch_with_exception(self, alert_scheduler, sample_alert):
        """Test processing a batch when one alert fails"""
        alerts = [sample_alert]
        alert_scheduler.alert_service.process_alert = AsyncMock(side_effect=Exception("Processing error"))
        
        # Should not raise exception, just log it
        await alert_scheduler._process_alert_batch(alerts)
        
        alert_scheduler.alert_service.process_alert.assert_called_once_with(sample_alert)
    
    @pytest.mark.asyncio
    async def test_process_all_alerts_now(self, alert_scheduler, sample_alert):
        """Test manually processing all active alerts"""
        # Mock the alerts dictionary
        alert_scheduler.alert_service.alerts = {
            sample_alert.id: sample_alert
        }
        
        alert_scheduler.alert_service.get_alerts_due_for_processing = AsyncMock(return_value=[sample_alert])
        alert_scheduler.alert_service.process_alert = AsyncMock(return_value=None)
        
        await alert_scheduler.process_all_alerts_now()
        
        alert_scheduler.alert_service.get_alerts_due_for_processing.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_all_alerts_now_no_active_alerts(self, alert_scheduler):
        """Test manually processing when no active alerts exist"""
        # Mock empty alerts dictionary
        alert_scheduler.alert_service.alerts = {}
        
        await alert_scheduler.process_all_alerts_now()
        
        # Should not call processing methods
        alert_scheduler.alert_service.get_alerts_due_for_processing.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_process_due_alerts_exception_handling(self, alert_scheduler):
        """Test exception handling in _process_due_alerts"""
        alert_scheduler.alert_service.get_alerts_due_for_processing = AsyncMock(
            side_effect=Exception("Service error")
        )
        
        # Should not raise exception, just log it
        await alert_scheduler._process_due_alerts()
        
        alert_scheduler.alert_service.get_alerts_due_for_processing.assert_called_once()
    
    def test_scheduler_integration(self, mock_alert_service):
        """Test scheduler integration with short intervals"""
        scheduler = AlertScheduler(mock_alert_service, check_interval=0.1)  # Very short interval
        mock_alert_service.get_alerts_due_for_processing = AsyncMock(return_value=[])
        
        scheduler.start()
        
        # Let it run for a short time
        time.sleep(0.3)
        
        scheduler.stop()
        
        # Should have called the service multiple times
        assert mock_alert_service.get_alerts_due_for_processing.call_count >= 2

class TestAlertSchedulerGlobalFunctions:
    """Test global scheduler functions"""
    
    def test_get_alert_scheduler_singleton(self):
        """Test that get_alert_scheduler returns singleton"""
        from src.services.alert_scheduler import get_alert_scheduler, _scheduler_instance
        
        # Clear global instance
        import src.services.alert_scheduler
        src.services.alert_scheduler._scheduler_instance = None
        
        scheduler1 = get_alert_scheduler()
        scheduler2 = get_alert_scheduler()
        
        assert scheduler1 is scheduler2
        assert scheduler1 is not None
    
    def test_start_stop_alert_scheduler(self):
        """Test starting and stopping global scheduler"""
        from src.services.alert_scheduler import start_alert_scheduler, stop_alert_scheduler
        
        # Clear global instance
        import src.services.alert_scheduler
        src.services.alert_scheduler._scheduler_instance = None
        
        start_alert_scheduler()
        
        # Should create and start scheduler
        scheduler = src.services.alert_scheduler._scheduler_instance
        assert scheduler is not None
        assert scheduler.running is True
        
        stop_alert_scheduler()
        
        # Should stop and clear scheduler
        assert src.services.alert_scheduler._scheduler_instance is None
    
    @patch('src.services.alert_scheduler.AlertService')
    def test_get_alert_scheduler_with_service(self, mock_service_class):
        """Test get_alert_scheduler with provided service"""
        from src.services.alert_scheduler import get_alert_scheduler
        
        # Clear global instance
        import src.services.alert_scheduler
        src.services.alert_scheduler._scheduler_instance = None
        
        mock_service = Mock()
        scheduler = get_alert_scheduler(mock_service)
        
        assert scheduler.alert_service is mock_service
        # Should not create new service
        mock_service_class.assert_not_called()