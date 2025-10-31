"""
Patent Alerts API Routes
Implements CRUD operations for patent alerts and notifications
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from src.services.alert_service import AlertService, AlertFrequency, AlertStatus

router = APIRouter(prefix="/api/alerts", tags=["alerts"])
logger = logging.getLogger(__name__)

# Initialize alert service
alert_service = AlertService()

# Request/Response Models
class CreateAlertRequest(BaseModel):
    research_title: str = Field(..., min_length=1, max_length=500)
    research_abstract: str = Field(..., min_length=10, max_length=5000)
    similarity_threshold: float = Field(default=0.75, ge=0.0, le=1.0)
    lookback_days: int = Field(default=30, ge=1, le=365)
    frequency: str = Field(default="weekly", pattern="^(daily|weekly|monthly)$")

class UpdateAlertRequest(BaseModel):
    research_title: Optional[str] = Field(None, min_length=1, max_length=500)
    research_abstract: Optional[str] = Field(None, min_length=10, max_length=5000)
    similarity_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)
    lookback_days: Optional[int] = Field(None, ge=1, le=365)
    frequency: Optional[str] = Field(None, pattern="^(daily|weekly|monthly)$")
    status: Optional[str] = Field(None, pattern="^(active|paused)$")

class AlertResponse(BaseModel):
    id: str
    user_id: str
    research_title: str
    research_abstract: str
    similarity_threshold: float
    lookback_days: int
    frequency: str
    status: str
    created_at: str
    updated_at: str
    last_run: Optional[str]
    next_run: Optional[str]
    notification_count: int

class NotificationResponse(BaseModel):
    id: str
    alert_id: str
    result_count: int
    created_at: str
    read: bool
    alert_results: List[Dict[str, Any]]

# Dependency to get current user (simplified for demo)
async def get_current_user() -> str:
    """Get current user ID - replace with proper authentication"""
    return "demo_user_123"

@router.post("/create", response_model=AlertResponse)
async def create_alert(
    request: CreateAlertRequest,
    user_id: str = Depends(get_current_user)
):
    """Create a new patent alert"""
    try:
        frequency_enum = AlertFrequency(request.frequency)
        
        alert = await alert_service.create_alert(
            user_id=user_id,
            research_title=request.research_title,
            research_abstract=request.research_abstract,
            similarity_threshold=request.similarity_threshold,
            lookback_days=request.lookback_days,
            frequency=frequency_enum
        )
        
        return AlertResponse(**alert.to_dict())
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid frequency: {request.frequency}")
    except Exception as e:
        logger.error(f"Error creating alert: {e}")
        raise HTTPException(status_code=500, detail="Failed to create alert")

@router.get("/list", response_model=List[AlertResponse])
async def list_alerts(user_id: str = Depends(get_current_user)):
    """Get all alerts for the current user"""
    try:
        alerts = await alert_service.get_alerts(user_id)
        return [AlertResponse(**alert.to_dict()) for alert in alerts]
        
    except Exception as e:
        logger.error(f"Error listing alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve alerts")

@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: str,
    user_id: str = Depends(get_current_user)
):
    """Get a specific alert"""
    try:
        alert = await alert_service.get_alert(alert_id, user_id)
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        return AlertResponse(**alert.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting alert {alert_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve alert")

@router.put("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: str,
    request: UpdateAlertRequest,
    user_id: str = Depends(get_current_user)
):
    """Update an existing alert"""
    try:
        # Convert string enums to enum objects
        frequency_enum = None
        if request.frequency:
            frequency_enum = AlertFrequency(request.frequency)
        
        status_enum = None
        if request.status:
            status_enum = AlertStatus(request.status)
        
        alert = await alert_service.update_alert(
            alert_id=alert_id,
            user_id=user_id,
            research_title=request.research_title,
            research_abstract=request.research_abstract,
            similarity_threshold=request.similarity_threshold,
            lookback_days=request.lookback_days,
            frequency=frequency_enum,
            status=status_enum
        )
        
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        return AlertResponse(**alert.to_dict())
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid enum value: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating alert {alert_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update alert")

@router.delete("/{alert_id}")
async def delete_alert(
    alert_id: str,
    user_id: str = Depends(get_current_user)
):
    """Delete an alert"""
    try:
        success = await alert_service.delete_alert(alert_id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        return {"message": "Alert deleted successfully", "alert_id": alert_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting alert {alert_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete alert")

@router.get("/notifications/list", response_model=List[NotificationResponse])
async def get_notifications(
    limit: int = 50,
    user_id: str = Depends(get_current_user)
):
    """Get notifications for the current user"""
    try:
        notifications = await alert_service.get_notifications(user_id, limit)
        return [NotificationResponse(**notification.to_dict()) for notification in notifications]
        
    except Exception as e:
        logger.error(f"Error getting notifications: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve notifications")

@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    user_id: str = Depends(get_current_user)
):
    """Mark a notification as read"""
    try:
        success = await alert_service.mark_notification_read(notification_id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        return {"message": "Notification marked as read", "notification_id": notification_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking notification {notification_id} as read: {e}")
        raise HTTPException(status_code=500, detail="Failed to mark notification as read")

@router.post("/{alert_id}/test")
async def test_alert(
    alert_id: str,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user)
):
    """Test an alert by running it immediately"""
    try:
        alert = await alert_service.get_alert(alert_id, user_id)
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        # Process alert in background
        background_tasks.add_task(process_single_alert, alert_id)
        
        return {
            "message": "Alert test started",
            "alert_id": alert_id,
            "status": "processing"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing alert {alert_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to test alert")

@router.get("/stats/summary")
async def get_alert_stats(user_id: str = Depends(get_current_user)):
    """Get alert statistics for the current user"""
    try:
        alerts = await alert_service.get_alerts(user_id)
        notifications = await alert_service.get_notifications(user_id)
        
        active_alerts = len([a for a in alerts if a.status == AlertStatus.ACTIVE])
        paused_alerts = len([a for a in alerts if a.status == AlertStatus.PAUSED])
        unread_notifications = len([n for n in notifications if not n.read])
        
        return {
            "total_alerts": len(alerts),
            "active_alerts": active_alerts,
            "paused_alerts": paused_alerts,
            "total_notifications": len(notifications),
            "unread_notifications": unread_notifications,
            "last_notification": notifications[0].created_at if notifications else None
        }
        
    except Exception as e:
        logger.error(f"Error getting alert stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve alert statistics")

# Background task functions
async def process_single_alert(alert_id: str):
    """Background task to process a single alert"""
    try:
        alert = alert_service.alerts.get(alert_id)
        if alert:
            await alert_service.process_alert(alert)
            logger.info(f"Processed alert {alert_id} in background")
    except Exception as e:
        logger.error(f"Error processing alert {alert_id} in background: {e}")