"""
Background scheduler service for processing patent alerts
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List
import threading
import time

from src.services.alert_service import AlertService, PatentAlert

logger = logging.getLogger(__name__)

class AlertScheduler:
    """Background scheduler for processing patent alerts"""
    
    def __init__(self, alert_service: AlertService, check_interval: int = 300):
        """
        Initialize the alert scheduler
        
        Args:
            alert_service: AlertService instance
            check_interval: How often to check for due alerts (seconds)
        """
        self.alert_service = alert_service
        self.check_interval = check_interval
        self.running = False
        self.scheduler_thread = None
        
    def start(self):
        """Start the background scheduler"""
        if self.running:
            logger.warning("Alert scheduler is already running")
            return
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        logger.info(f"Alert scheduler started with {self.check_interval}s check interval")
    
    def stop(self):
        """Stop the background scheduler"""
        if not self.running:
            logger.warning("Alert scheduler is not running")
            return
        
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=10)
        logger.info("Alert scheduler stopped")
    
    def _run_scheduler(self):
        """Main scheduler loop (runs in background thread)"""
        logger.info("Alert scheduler loop started")
        
        while self.running:
            try:
                # Run the async processing in the thread
                asyncio.run(self._process_due_alerts())
                
                # Sleep for the check interval
                time.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                # Continue running even if there's an error
                time.sleep(self.check_interval)
        
        logger.info("Alert scheduler loop ended")
    
    async def _process_due_alerts(self):
        """Process all alerts that are due for execution"""
        try:
            due_alerts = await self.alert_service.get_alerts_due_for_processing()
            
            if not due_alerts:
                logger.debug("No alerts due for processing")
                return
            
            logger.info(f"Processing {len(due_alerts)} due alerts")
            
            # Process alerts in batches to avoid overwhelming the system
            batch_size = 5
            for i in range(0, len(due_alerts), batch_size):
                batch = due_alerts[i:i + batch_size]
                await self._process_alert_batch(batch)
                
                # Small delay between batches
                await asyncio.sleep(1)
            
            logger.info(f"Completed processing {len(due_alerts)} alerts")
            
        except Exception as e:
            logger.error(f"Error processing due alerts: {e}")
    
    async def _process_alert_batch(self, alerts: List[PatentAlert]):
        """Process a batch of alerts concurrently"""
        try:
            tasks = [
                self.alert_service.process_alert(alert)
                for alert in alerts
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Log results
            for i, result in enumerate(results):
                alert = alerts[i]
                if isinstance(result, Exception):
                    logger.error(f"Failed to process alert {alert.id}: {result}")
                elif result:
                    logger.info(f"Alert {alert.id} generated {len(result.alert_results)} notifications")
                else:
                    logger.debug(f"Alert {alert.id} processed with no new results")
                    
        except Exception as e:
            logger.error(f"Error processing alert batch: {e}")
    
    async def process_all_alerts_now(self):
        """Manually trigger processing of all active alerts (for testing)"""
        try:
            all_alerts = []
            for alert in self.alert_service.alerts.values():
                if alert.status.value == "active":
                    all_alerts.append(alert)
            
            if not all_alerts:
                logger.info("No active alerts to process")
                return
            
            logger.info(f"Manually processing {len(all_alerts)} active alerts")
            await self._process_due_alerts()
            
        except Exception as e:
            logger.error(f"Error in manual alert processing: {e}")
            raise

# Global scheduler instance
_scheduler_instance = None

def get_alert_scheduler(alert_service: AlertService = None) -> AlertScheduler:
    """Get the global alert scheduler instance"""
    global _scheduler_instance
    
    if _scheduler_instance is None:
        if alert_service is None:
            from src.services.alert_service import AlertService
            alert_service = AlertService()
        
        _scheduler_instance = AlertScheduler(alert_service)
    
    return _scheduler_instance

def start_alert_scheduler(alert_service: AlertService = None):
    """Start the global alert scheduler"""
    scheduler = get_alert_scheduler(alert_service)
    scheduler.start()

def stop_alert_scheduler():
    """Stop the global alert scheduler"""
    global _scheduler_instance
    if _scheduler_instance:
        _scheduler_instance.stop()
        _scheduler_instance = None