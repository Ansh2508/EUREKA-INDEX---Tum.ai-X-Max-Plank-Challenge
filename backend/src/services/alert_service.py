"""
Alert Service for managing patent alerts and notifications.
Refactored from existing semantic_alerts.py agent.
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json
import uuid
import logging
from dataclasses import dataclass, asdict
from enum import Enum

from src.agents.semantic_alerts import SemanticPatentAlerts, AlertResult

logger = logging.getLogger(__name__)

class AlertStatus(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    DELETED = "deleted"

class AlertFrequency(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

@dataclass
class PatentAlert:
    id: str
    user_id: str
    research_title: str
    research_abstract: str
    similarity_threshold: float
    lookback_days: int
    frequency: AlertFrequency
    status: AlertStatus
    created_at: datetime
    updated_at: datetime
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    notification_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['frequency'] = self.frequency.value
        data['status'] = self.status.value
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        if self.last_run:
            data['last_run'] = self.last_run.isoformat()
        if self.next_run:
            data['next_run'] = self.next_run.isoformat()
        return data

@dataclass
class AlertNotification:
    id: str
    alert_id: str
    alert_results: List[AlertResult]
    created_at: datetime
    read: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'alert_id': self.alert_id,
            'alert_results': [asdict(result) for result in self.alert_results],
            'created_at': self.created_at.isoformat(),
            'read': self.read,
            'result_count': len(self.alert_results)
        }

class AlertService:
    """Service for managing patent alerts and notifications"""
    
    def __init__(self):
        self.semantic_alerts = SemanticPatentAlerts()
        # In-memory storage for demo - replace with database in production
        self.alerts: Dict[str, PatentAlert] = {}
        self.notifications: Dict[str, AlertNotification] = {}
        
    async def create_alert(
        self,
        user_id: str,
        research_title: str,
        research_abstract: str,
        similarity_threshold: float = 0.75,
        lookback_days: int = 30,
        frequency: AlertFrequency = AlertFrequency.WEEKLY
    ) -> PatentAlert:
        """Create a new patent alert"""
        try:
            alert_id = str(uuid.uuid4())
            now = datetime.now()
            
            alert = PatentAlert(
                id=alert_id,
                user_id=user_id,
                research_title=research_title,
                research_abstract=research_abstract,
                similarity_threshold=similarity_threshold,
                lookback_days=lookback_days,
                frequency=frequency,
                status=AlertStatus.ACTIVE,
                created_at=now,
                updated_at=now,
                next_run=self._calculate_next_run(frequency, now)
            )
            
            self.alerts[alert_id] = alert
            logger.info(f"Created alert {alert_id} for user {user_id}")
            
            return alert
            
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
            raise
    
    async def get_alerts(self, user_id: str) -> List[PatentAlert]:
        """Get all alerts for a user"""
        try:
            user_alerts = [
                alert for alert in self.alerts.values() 
                if alert.user_id == user_id and alert.status != AlertStatus.DELETED
            ]
            return sorted(user_alerts, key=lambda x: x.created_at, reverse=True)
            
        except Exception as e:
            logger.error(f"Error getting alerts for user {user_id}: {e}")
            raise
    
    async def get_alert(self, alert_id: str, user_id: str) -> Optional[PatentAlert]:
        """Get a specific alert"""
        try:
            alert = self.alerts.get(alert_id)
            if alert and alert.user_id == user_id and alert.status != AlertStatus.DELETED:
                return alert
            return None
            
        except Exception as e:
            logger.error(f"Error getting alert {alert_id}: {e}")
            raise
    
    async def update_alert(
        self,
        alert_id: str,
        user_id: str,
        research_title: Optional[str] = None,
        research_abstract: Optional[str] = None,
        similarity_threshold: Optional[float] = None,
        lookback_days: Optional[int] = None,
        frequency: Optional[AlertFrequency] = None,
        status: Optional[AlertStatus] = None
    ) -> Optional[PatentAlert]:
        """Update an existing alert"""
        try:
            alert = await self.get_alert(alert_id, user_id)
            if not alert:
                return None
            
            # Update fields if provided
            if research_title is not None:
                alert.research_title = research_title
            if research_abstract is not None:
                alert.research_abstract = research_abstract
            if similarity_threshold is not None:
                alert.similarity_threshold = similarity_threshold
            if lookback_days is not None:
                alert.lookback_days = lookback_days
            if frequency is not None:
                alert.frequency = frequency
                alert.next_run = self._calculate_next_run(frequency, datetime.now())
            if status is not None:
                alert.status = status
            
            alert.updated_at = datetime.now()
            self.alerts[alert_id] = alert
            
            logger.info(f"Updated alert {alert_id}")
            return alert
            
        except Exception as e:
            logger.error(f"Error updating alert {alert_id}: {e}")
            raise
    
    async def delete_alert(self, alert_id: str, user_id: str) -> bool:
        """Delete an alert (soft delete)"""
        try:
            alert = await self.get_alert(alert_id, user_id)
            if not alert:
                return False
            
            alert.status = AlertStatus.DELETED
            alert.updated_at = datetime.now()
            self.alerts[alert_id] = alert
            
            logger.info(f"Deleted alert {alert_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting alert {alert_id}: {e}")
            raise
    
    async def process_alert(self, alert: PatentAlert) -> Optional[AlertNotification]:
        """Process a single alert and check for new similar patents"""
        try:
            if alert.status != AlertStatus.ACTIVE:
                return None
            
            # Use semantic alerts to find similar patents
            alert_results = await self.semantic_alerts.detect_similar_patents(
                research_abstract=alert.research_abstract,
                research_title=alert.research_title,
                similarity_threshold=alert.similarity_threshold,
                lookback_days=alert.lookback_days
            )
            
            # Only create notification if there are results
            if alert_results:
                notification_id = str(uuid.uuid4())
                notification = AlertNotification(
                    id=notification_id,
                    alert_id=alert.id,
                    alert_results=alert_results,
                    created_at=datetime.now()
                )
                
                self.notifications[notification_id] = notification
                
                # Update alert
                alert.last_run = datetime.now()
                alert.next_run = self._calculate_next_run(alert.frequency, alert.last_run)
                alert.notification_count += 1
                alert.updated_at = datetime.now()
                self.alerts[alert.id] = alert
                
                logger.info(f"Processed alert {alert.id}, found {len(alert_results)} results")
                return notification
            
            else:
                # Update alert even if no results
                alert.last_run = datetime.now()
                alert.next_run = self._calculate_next_run(alert.frequency, alert.last_run)
                alert.updated_at = datetime.now()
                self.alerts[alert.id] = alert
                
                logger.info(f"Processed alert {alert.id}, no new results")
                return None
                
        except Exception as e:
            logger.error(f"Error processing alert {alert.id}: {e}")
            
            # Update alert even if processing failed
            alert.last_run = datetime.now()
            alert.next_run = self._calculate_next_run(alert.frequency, alert.last_run)
            alert.updated_at = datetime.now()
            self.alerts[alert.id] = alert
            
            # Return None instead of raising - graceful error handling
            return None
    
    async def get_notifications(self, user_id: str, limit: int = 50) -> List[AlertNotification]:
        """Get notifications for a user's alerts"""
        try:
            user_alert_ids = {
                alert.id for alert in self.alerts.values() 
                if alert.user_id == user_id
            }
            
            user_notifications = [
                notification for notification in self.notifications.values()
                if notification.alert_id in user_alert_ids
            ]
            
            # Sort by creation date, most recent first
            user_notifications.sort(key=lambda x: x.created_at, reverse=True)
            
            return user_notifications[:limit]
            
        except Exception as e:
            logger.error(f"Error getting notifications for user {user_id}: {e}")
            raise
    
    async def mark_notification_read(self, notification_id: str, user_id: str) -> bool:
        """Mark a notification as read"""
        try:
            notification = self.notifications.get(notification_id)
            if not notification:
                return False
            
            # Verify user owns the alert
            alert = self.alerts.get(notification.alert_id)
            if not alert or alert.user_id != user_id:
                return False
            
            notification.read = True
            self.notifications[notification_id] = notification
            
            return True
            
        except Exception as e:
            logger.error(f"Error marking notification {notification_id} as read: {e}")
            raise
    
    async def get_alerts_due_for_processing(self) -> List[PatentAlert]:
        """Get alerts that are due for processing"""
        try:
            now = datetime.now()
            due_alerts = [
                alert for alert in self.alerts.values()
                if (alert.status == AlertStatus.ACTIVE and 
                    alert.next_run and 
                    alert.next_run <= now)
            ]
            
            return due_alerts
            
        except Exception as e:
            logger.error(f"Error getting alerts due for processing: {e}")
            raise
    
    def _calculate_next_run(self, frequency: AlertFrequency, from_time: datetime) -> datetime:
        """Calculate next run time based on frequency"""
        if frequency == AlertFrequency.DAILY:
            return from_time + timedelta(days=1)
        elif frequency == AlertFrequency.WEEKLY:
            return from_time + timedelta(weeks=1)
        elif frequency == AlertFrequency.MONTHLY:
            return from_time + timedelta(days=30)
        else:
            return from_time + timedelta(weeks=1)  # Default to weekly