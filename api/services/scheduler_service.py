"""
Event Scheduler Service for ICS DTEND Triggers.

This module provides a background scheduler that monitors ICS calendar events
and triggers the orchestrator agent when events reach their end time (DTEND).

Key Features:
- Tolerance window for time precision (avoids missing exact moments)
- Duplicate execution prevention via triggered events registry
- Persistent state for service restart resilience
- Dynamic ICS file reload support
"""

import asyncio
from typing import Set, List, Dict, Any, Optional

from utils import logger, load_config, get_config, IcsRepository, TimestampHelper, JsonRepository


class EventSchedulerService:
    """
    Background scheduler that monitors ICS events and triggers the orchestrator
    when events end (DTEND matches current time within tolerance).
    
    Attributes:
        poll_interval: How often to check for ending events (seconds)
        trigger_window: Total window size (±half on each side of DTEND)
    """
    
    def __init__(self):
        """Initialize the scheduler service."""
        load_config()
        self._config = get_config()
        self._scheduler_config = self._config.SCHEDULER
        
        # Configuration
        self.poll_interval = self._scheduler_config.POLL_INTERVAL_SECONDS
        self.trigger_window = self._scheduler_config.TRIGGER_WINDOW_SECONDS
        self.enabled = self._scheduler_config.ENABLED
        
        # State & Repositories
        self.state_repo = JsonRepository(self._scheduler_config.PERSIST_FILE)
        self._triggered_events: Set[str] = set()
        self._task: Optional[asyncio.Task] = None
        self._running = False
        
        # Repositories (lazy init)
        self._ics_repo: Optional[IcsRepository] = None
        self._agent_service = None
        
        # Load persisted state
        self._load_state()
    
    def _get_ics_repo(self) -> IcsRepository:
        """Lazy initialization of ICS repository."""
        if self._ics_repo is None:
            self._ics_repo = IcsRepository(self._config.PATHS.ICS)
        return self._ics_repo
    
    def _get_agent_service(self):
        """Lazy initialization of agent service to avoid circular imports."""
        if self._agent_service is None:
            from api.services.agent_service import AgentService
            self._agent_service = AgentService()
        return self._agent_service
    
    def _load_state(self) -> None:
        """Load triggered events from persistent storage."""
        try:
            state = self.state_repo.read(default={})
            self._triggered_events = set(state.get("triggered_event_ids", []))
            if self._triggered_events:
                logger.info(f"Scheduler: Loaded {len(self._triggered_events)} triggered events from storage")
        except Exception as e:
            logger.warning(f"Scheduler: Failed to load triggered events: {e}")
            self._triggered_events = set()
    
    def _save_state(self) -> None:
        """Save current state to persistent storage."""
        try:
            self.state_repo.save({
                "triggered_event_ids": list(self._triggered_events),
                "last_updated": TimestampHelper.now_paris().isoformat()
            })
        except Exception as e:
            logger.error(f"Scheduler: Failed to save state: {e}")
    
    def _get_events_to_trigger(self) -> List[Dict[str, Any]]:
        """
        Get events whose DTEND is within the trigger window and haven't been triggered yet.
        """
        try:
            # Use IcsRepository's built-in filtering
            ending_events = self._get_ics_repo().get_ending_events(self.trigger_window)
            
            # Filter out already triggered events
            return [e for e in ending_events if e.get("id") not in self._triggered_events]
                    
        except FileNotFoundError:
            logger.warning("Scheduler: ICS file not found")
        except Exception as e:
            logger.error(f"Scheduler: Error reading events: {e}")
        
        return []
    
    async def _trigger_agent(self, event: Dict[str, Any]) -> None:
        """
        Trigger the orchestrator agent for an ending event.
        """
        event_id = event.get("id")
        summary = event.get("summary", "Unknown Event")
        
        logger.info(f"Scheduler: Triggering agent for event '{summary}' (ID: {event_id})")
        
        try:
            task = self._config.LLM_MODULES.ORCHESTRATOR.DEFAULT_TASK
            agent_service = self._get_agent_service()
            
            # Run agent in executor to not block the event loop
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: agent_service.run_task(task)
            )
            
            logger.info(f"Scheduler: Agent completed for event '{summary}'. Status: {result.status}")
            
            # Mark as triggered after successful execution
            self._triggered_events.add(event_id)
            self._save_state()
            
        except Exception as e:
            logger.error(f"Scheduler: Failed to trigger agent for event '{summary}': {e}")
    
    async def _scheduler_loop(self) -> None:
        """Main scheduler loop that checks for events to trigger."""
        logger.info(f"Scheduler: Starting loop (poll: {self.poll_interval}s, window: {self.trigger_window}s)")
        
        while self._running:
            try:
                events = self._get_events_to_trigger()
                
                if events:
                    logger.info(f"Scheduler: Found {len(events)} event(s) to trigger")
                    for event in events:
                        await self._trigger_agent(event)
                
                await asyncio.sleep(self.poll_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Scheduler: Error in loop: {e}")
                await asyncio.sleep(self.poll_interval)
    
    async def start(self) -> None:
        """Start the scheduler background task."""
        if not self.enabled:
            logger.info("Scheduler: Disabled in configuration")
            return
        
        if not self._running:
            self._running = True
            self._task = asyncio.create_task(self._scheduler_loop())
            logger.info("Scheduler: Started")
    
    async def stop(self) -> None:
        """Stop the scheduler background task."""
        if self._running:
            self._running = False
            if self._task:
                self._task.cancel()
                try:
                    await self._task
                except asyncio.CancelledError:
                    pass
                self._task = None
            
            self._save_state()
            logger.info("Scheduler: Stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current scheduler status."""
        return {
            "enabled": self.enabled,
            "running": self._running,
            "poll_interval_seconds": self.poll_interval,
            "trigger_window_seconds": self.trigger_window,
            "triggered_events_count": len(self._triggered_events),
        }
    
    def clear_triggered_events(self) -> int:
        """Clear all triggered events registry."""
        count = len(self._triggered_events)
        self._triggered_events.clear()
        self._save_state()
        logger.info(f"Scheduler: Cleared {count} triggered events")
        return count


# Singleton instance
_scheduler_instance: Optional[EventSchedulerService] = None


def get_scheduler() -> EventSchedulerService:
    """Get the singleton scheduler instance."""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = EventSchedulerService()
    return _scheduler_instance
