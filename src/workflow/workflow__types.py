"""Type definitions for workflow orchestration."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class StepStatus(Enum):
    """Status of a workflow step."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class WorkflowStatus(Enum):
    """Status of a workflow."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class StepResult:
    """Result of a workflow step execution."""

    status: StepStatus
    output: Any
    error: Optional[Exception] = None
    duration_ms: float = 0.0
    attempts: int = 1
    started_at: Optional[float] = None
    completed_at: Optional[float] = None


@dataclass
class WorkflowState:
    """State of a workflow execution."""

    workflow_id: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    step_results: Dict[str, StepResult] = field(default_factory=dict)
    start_time: float = 0.0
    end_time: Optional[float] = None
    input_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def duration_ms(self) -> float:
        """Calculate total workflow duration in milliseconds."""
        if self.end_time is None:
            return 0.0
        return (self.end_time - self.start_time) * 1000

    def get_completed_steps(self) -> List[str]:
        """Get list of completed step names."""
        return [
            name
            for name, result in self.step_results.items()
            if result.status == StepStatus.COMPLETED
        ]

    def get_failed_steps(self) -> List[str]:
        """Get list of failed step names."""
        return [
            name for name, result in self.step_results.items() if result.status == StepStatus.FAILED
        ]

    def get_step_output(self, step_name: str) -> Any:
        """Get output of a specific step."""
        result = self.step_results.get(step_name)
        if result is None:
            return None
        return result.output


@dataclass
class ProgressEvent:
    """Event for tracking workflow progress."""

    workflow_id: str
    event_type: str  # "step_start", "step_complete", "workflow_complete", "workflow_failed"
    step_name: Optional[str] = None
    step_status: Optional[StepStatus] = None
    message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
