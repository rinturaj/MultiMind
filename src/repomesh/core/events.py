"""
Event bus for inter-agent communication.

This module provides an event bus for publishing and subscribing to events
across the system, enabling loose coupling between components.
"""

import asyncio
from collections import defaultdict
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
from uuid import UUID

from repomesh.core.models import Event, EventType


class EventBus:
    """Event bus for publishing and subscribing to events."""

    def __init__(self, max_history: int = 1000) -> None:
        """Initialize the event bus.

        Args:
            max_history: Maximum number of events to keep in history
        """
        self.subscribers: Dict[EventType, List[Callable]] = defaultdict(list)
        self.history: List[Event] = []
        self.max_history = max_history
        self._lock = asyncio.Lock()

    async def publish(self, event: Event) -> None:
        """Publish an event to all subscribers.

        Args:
            event: Event to publish
        """
        async with self._lock:
            # Add to history
            self.history.append(event)
            if len(self.history) > self.max_history:
                self.history.pop(0)

        # Notify subscribers
        if event.type in self.subscribers:
            tasks = []
            for handler in self.subscribers[event.type]:
                # Create task for each handler
                if asyncio.iscoroutinefunction(handler):
                    tasks.append(asyncio.create_task(handler(event)))
                else:
                    # Wrap sync handlers
                    tasks.append(asyncio.create_task(self._run_sync_handler(handler, event)))

            # Wait for all handlers to complete
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)

    async def _run_sync_handler(self, handler: Callable, event: Event) -> None:
        """Run a synchronous handler in the event loop.

        Args:
            handler: Synchronous handler function
            event: Event to pass to handler
        """
        try:
            handler(event)
        except Exception:
            # Silently ignore handler errors to prevent cascading failures
            pass

    def subscribe(self, event_type: EventType, handler: Callable) -> None:
        """Subscribe to an event type.

        Args:
            event_type: Type of event to subscribe to
            handler: Handler function to call when event is published
        """
        if handler not in self.subscribers[event_type]:
            self.subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: EventType, handler: Callable) -> None:
        """Unsubscribe from an event type.

        Args:
            event_type: Type of event to unsubscribe from
            handler: Handler function to remove
        """
        if handler in self.subscribers[event_type]:
            self.subscribers[event_type].remove(handler)

    def get_history(
        self,
        event_type: Optional[EventType] = None,
        repo_id: Optional[UUID] = None,
        task_id: Optional[UUID] = None,
        source: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Event]:
        """Get event history with optional filtering.

        Args:
            event_type: Optional event type filter
            repo_id: Optional repository ID filter
            task_id: Optional task ID filter
            source: Optional source filter
            limit: Optional limit on number of events

        Returns:
            List of events matching filters
        """
        filtered_events = self.history.copy()

        # Apply filters
        if event_type:
            filtered_events = [e for e in filtered_events if e.type == event_type]

        if repo_id:
            filtered_events = [e for e in filtered_events if e.repo_id == repo_id]

        if task_id:
            filtered_events = [e for e in filtered_events if e.task_id == task_id]

        if source:
            filtered_events = [e for e in filtered_events if e.source == source]

        # Apply limit
        if limit:
            filtered_events = filtered_events[-limit:]

        return filtered_events

    def clear_history(self) -> None:
        """Clear event history."""
        self.history.clear()

    def get_subscriber_count(self, event_type: EventType) -> int:
        """Get number of subscribers for an event type.

        Args:
            event_type: Event type to check

        Returns:
            Number of subscribers
        """
        return len(self.subscribers.get(event_type, []))

    def get_all_event_types(self) -> List[EventType]:
        """Get all event types that have subscribers.

        Returns:
            List of event types with subscribers
        """
        return list(self.subscribers.keys())

    async def publish_repo_registered(
        self,
        repo_id: UUID,
        repo_name: str,
        source: str = "repo_manager",
    ) -> None:
        """Publish a repository registered event.

        Args:
            repo_id: Repository ID
            repo_name: Repository name
            source: Event source
        """
        await self.publish(
            Event(
                type=EventType.REPO_REGISTERED,
                source=source,
                payload={"repo_name": repo_name},
                repo_id=repo_id,
                task_id=None,
            )
        )

    async def publish_task_created(
        self,
        task_id: UUID,
        repo_id: UUID,
        agent_type: str,
        source: str = "orchestrator",
    ) -> None:
        """Publish a task created event.

        Args:
            task_id: Task ID
            repo_id: Repository ID
            agent_type: Agent type
            source: Event source
        """
        await self.publish(
            Event(
                type=EventType.TASK_CREATED,
                source=source,
                payload={"agent_type": agent_type},
                repo_id=repo_id,
                task_id=task_id,
            )
        )

    async def publish_task_completed(
        self,
        task_id: UUID,
        repo_id: UUID,
        result: Dict[str, Any],
        source: str = "agent",
    ) -> None:
        """Publish a task completed event.

        Args:
            task_id: Task ID
            repo_id: Repository ID
            result: Task result
            source: Event source
        """
        await self.publish(
            Event(
                type=EventType.TASK_COMPLETED,
                source=source,
                payload={"result": result},
                repo_id=repo_id,
                task_id=task_id,
            )
        )

    async def publish_task_failed(
        self,
        task_id: UUID,
        repo_id: UUID,
        error: str,
        source: str = "agent",
    ) -> None:
        """Publish a task failed event.

        Args:
            task_id: Task ID
            repo_id: Repository ID
            error: Error message
            source: Event source
        """
        await self.publish(
            Event(
                type=EventType.TASK_FAILED,
                source=source,
                payload={"error": error},
                repo_id=repo_id,
                task_id=task_id,
            )
        )

    async def publish_agent_started(
        self,
        agent_type: str,
        repo_id: UUID,
        source: str = "agent",
    ) -> None:
        """Publish an agent started event.

        Args:
            agent_type: Agent type
            repo_id: Repository ID
            source: Event source
        """
        await self.publish(
            Event(
                type=EventType.AGENT_STARTED,
                source=source,
                payload={"agent_type": agent_type},
                repo_id=repo_id,
                task_id=None,
            )
        )

    async def publish_agent_completed(
        self,
        agent_type: str,
        repo_id: UUID,
        result: Dict[str, Any],
        source: str = "agent",
    ) -> None:
        """Publish an agent completed event.

        Args:
            agent_type: Agent type
            repo_id: Repository ID
            result: Agent result
            source: Event source
        """
        await self.publish(
            Event(
                type=EventType.AGENT_COMPLETED,
                source=source,
                payload={"agent_type": agent_type, "result": result},
                repo_id=repo_id,
                task_id=None,
            )
        )

# Made with Bob
