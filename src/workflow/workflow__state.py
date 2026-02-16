"""State management for workflow execution."""

from abc import ABC, abstractmethod
from typing import Dict, Optional

from src.workflow.workflow__types import WorkflowState


class StateStore(ABC):
    """Abstract interface for workflow state persistence."""

    @abstractmethod
    async def save_state(self, state: WorkflowState) -> None:
        """Save workflow state."""
        pass

    @abstractmethod
    async def load_state(self, workflow_id: str) -> Optional[WorkflowState]:
        """Load workflow state by ID."""
        pass

    @abstractmethod
    async def delete_state(self, workflow_id: str) -> None:
        """Delete workflow state."""
        pass

    @abstractmethod
    async def list_workflows(self) -> list[str]:
        """List all workflow IDs."""
        pass


class InMemoryStateStore(StateStore):
    """In-memory implementation of StateStore for testing and development."""

    def __init__(self) -> None:
        self._states: Dict[str, WorkflowState] = {}

    async def save_state(self, state: WorkflowState) -> None:
        """Save workflow state to memory."""
        self._states[state.workflow_id] = state

    async def load_state(self, workflow_id: str) -> Optional[WorkflowState]:
        """Load workflow state from memory."""
        return self._states.get(workflow_id)

    async def delete_state(self, workflow_id: str) -> None:
        """Delete workflow state from memory."""
        self._states.pop(workflow_id, None)

    async def list_workflows(self) -> list[str]:
        """List all workflow IDs in memory."""
        return list(self._states.keys())

    def clear(self) -> None:
        """Clear all workflow states (for testing)."""
        self._states.clear()
