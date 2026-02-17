"""Workflow executor for orchestrating multi-step workflows."""

import asyncio
import time
from typing import Any, Dict, List, Optional, Set

from src.steps.step__base import Step
from src.workflow.workflow__state import StateStore
from src.workflow.workflow__types import (
    ProgressEvent,
    StepResult,
    StepStatus,
    WorkflowState,
    WorkflowStatus,
)


class WorkflowExecutor:
    """Orchestrates workflow execution with parallelization and error handling."""

    def __init__(
        self,
        state_store: StateStore,
        max_parallel_steps: int = 5,
        enable_progress_events: bool = False,
    ) -> None:
        """
        Initialize workflow executor.

        Args:
            state_store: State persistence implementation
            max_parallel_steps: Maximum number of steps to execute in parallel
            enable_progress_events: Whether to emit progress events
        """
        self.state_store = state_store
        self.max_parallel_steps = max_parallel_steps
        self.enable_progress_events = enable_progress_events
        self._progress_events: List[ProgressEvent] = []

    async def execute_workflow(
        self,
        workflow_id: str,
        steps: List[Step],
        input_data: Dict[str, Any],
    ) -> WorkflowState:
        """
        Execute a workflow with parallelization and error handling.

        Args:
            workflow_id: Unique identifier for this workflow execution
            steps: List of steps to execute
            input_data: Input data for the workflow

        Returns:
            Final workflow state

        Raises:
            ValueError: If workflow definition is invalid
            Exception: If workflow execution fails
        """
        # Initialize workflow state
        state = WorkflowState(
            workflow_id=workflow_id,
            status=WorkflowStatus.RUNNING,
            input_data=input_data,
            start_time=time.time(),
        )

        try:
            dependency_graph = self._build_dependency_graph(steps)
            step_map = {step.name: step for step in steps}

            pending_steps = set(step.name for step in steps)
            completed_steps: Set[str] = set()
            failed_steps: Set[str] = set()

            while pending_steps:
                executable = self._get_executable_steps(
                    pending_steps, completed_steps, dependency_graph
                )

                if not executable:
                    if pending_steps:
                        remaining = ", ".join(pending_steps)
                        raise ValueError(
                            f"Cannot execute remaining steps due to unmet dependencies: {remaining}"
                        )
                    break

                tasks = []
                for step_name in executable[: self.max_parallel_steps]:
                    step = step_map[step_name]
                    context = {
                        "input_data": input_data,
                        "step_outputs": {
                            name: state.step_results[name].output
                            for name in completed_steps
                            if name in state.step_results
                        },
                    }
                    tasks.append(self._execute_step_with_tracking(step, context, state))

                results = await asyncio.gather(*tasks, return_exceptions=True)

                for step_name, result in zip(executable[: self.max_parallel_steps], results):
                    pending_steps.remove(step_name)

                    if isinstance(result, Exception):
                        failed_steps.add(step_name)
                        state.step_results[step_name] = StepResult(
                            status=StepStatus.FAILED,
                            output=None,
                            error=result,
                            duration_ms=0.0,
                        )
                    else:
                        completed_steps.add(step_name)

            if failed_steps:
                state.status = WorkflowStatus.FAILED
                raise Exception(f"Workflow failed. Failed steps: {', '.join(failed_steps)}")
            else:
                state.status = WorkflowStatus.COMPLETED

        except Exception as e:
            state.status = WorkflowStatus.FAILED
            state.metadata["error"] = str(e)
            raise

        finally:
            state.end_time = time.time()
            await self.state_store.save_state(state)

        return state

    def _should_execute_step(self, step: Step, context: Dict[str, Any]) -> bool:
        """
        Return whether the step should run (condition is met).
        Blocks execution when the step's condition is not met.
        """
        return step.is_condition_met(context)

    async def _execute_step_with_tracking(
        self, step: Step, context: Dict[str, Any], state: WorkflowState
    ) -> None:
        """Execute a step with progress tracking."""
        if not self._should_execute_step(step, context):
            state.step_results[step.name] = StepResult(
                status=StepStatus.SKIPPED,
                output=None,
                duration_ms=0.0,
            )
            self._emit_progress_event(state.workflow_id, "step_complete", step.name, StepStatus.SKIPPED)
            return

        self._emit_progress_event(state.workflow_id, "step_start", step.name, StepStatus.RUNNING)

        result = await self._execute_step(step, context)
        state.step_results[step.name] = result

        self._emit_progress_event(state.workflow_id, "step_complete", step.name, result.status)

    async def _execute_step(self, step: Step, context: Dict[str, Any]) -> StepResult:
        """
        Execute a single step with timeout and retry logic.

        Args:
            step: Step to execute
            context: Execution context

        Returns:
            Step result
        """
        start_time = time.time()
        attempts = 0
        last_error: Optional[Exception] = None

        while attempts < step.max_retries:
            attempts += 1

            try:
                output = await asyncio.wait_for(step.execute(context), timeout=step.timeout_seconds)

                duration_ms = (time.time() - start_time) * 1000

                return StepResult(
                    status=StepStatus.COMPLETED,
                    output=output,
                    duration_ms=duration_ms,
                    attempts=attempts,
                    started_at=start_time,
                    completed_at=time.time(),
                )

            except asyncio.TimeoutError:
                last_error = Exception(
                    f"Step '{step.name}' timed out after {step.timeout_seconds}s"
                )
                if attempts < step.max_retries:
                    await self._exponential_backoff(attempts)
                    continue
                break

            except Exception as e:
                last_error = e
                if step.is_retryable_error(e) and attempts < step.max_retries:
                    await self._exponential_backoff(attempts)
                    continue
                break

        duration_ms = (time.time() - start_time) * 1000

        return StepResult(
            status=StepStatus.FAILED,
            output=None,
            error=last_error,
            duration_ms=duration_ms,
            attempts=attempts,
            started_at=start_time,
            completed_at=time.time(),
        )

    async def _exponential_backoff(self, attempt: int) -> None:
        """Exponential backoff with jitter."""
        base_delay = 0.1  # 100ms
        max_delay = 5.0  # 5 seconds
        delay = min(base_delay * (2**attempt), max_delay)

        import random

        jitter = delay * 0.25 * (2 * random.random() - 1)
        await asyncio.sleep(delay + jitter)

    def _build_dependency_graph(self, steps: List[Step]) -> Dict[str, Set[str]]:
        """
        Build dependency graph from steps.

        Args:
            steps: List of steps

        Returns:
            Dictionary mapping step name to set of dependency names

        Raises:
            ValueError: If dependencies are invalid
        """
        step_names = {step.name for step in steps}
        graph: Dict[str, Set[str]] = {}

        for step in steps:
            for dep in step.depends_on:
                if dep not in step_names:
                    raise ValueError(f"Step '{step.name}' depends on '{dep}' which does not exist")

            graph[step.name] = set(step.depends_on)

        self._validate_no_cycles(graph)

        return graph

    def _validate_no_cycles(self, graph: Dict[str, Set[str]]) -> None:
        """
        Validate that the dependency graph has no cycles.

        Args:
            graph: Dependency graph

        Raises:
            ValueError: If circular dependency is detected
        """
        visited: Set[str] = set()
        rec_stack: Set[str] = set()

        def has_cycle(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)

            for neighbor in graph.get(node, set()):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node)
            return False

        for node in graph:
            if node not in visited:
                if has_cycle(node):
                    raise ValueError(f"Circular dependency detected involving step '{node}'")

    def _get_executable_steps(
        self,
        pending_steps: Set[str],
        completed_steps: Set[str],
        dependency_graph: Dict[str, Set[str]],
    ) -> List[str]:
        """
        Get steps that can be executed (all dependencies met).

        Args:
            pending_steps: Steps not yet executed
            completed_steps: Steps that completed successfully
            dependency_graph: Dependency relationships

        Returns:
            List of step names that can be executed
        """
        executable = []

        for step_name in pending_steps:
            dependencies = dependency_graph.get(step_name, set())
            if dependencies.issubset(completed_steps):
                executable.append(step_name)

        return executable

    def _emit_progress_event(
        self,
        workflow_id: str,
        event_type: str,
        step_name: str,
        step_status: StepStatus,
    ) -> None:
        """Emit a progress event."""
        if not self.enable_progress_events:
            return

        event = ProgressEvent(
            workflow_id=workflow_id,
            event_type=event_type,
            step_name=step_name,
            step_status=step_status,
        )
        self._progress_events.append(event)

    def get_progress_events(self) -> List[ProgressEvent]:
        """Get all progress events."""
        return self._progress_events.copy()

    def clear_progress_events(self) -> None:
        """Clear progress events."""
        self._progress_events.clear()

    async def resume_workflow(self, workflow_id: str, steps: List[Step]) -> WorkflowState:
        """
        Resume a failed workflow from last checkpoint.

        Args:
            workflow_id: Workflow ID to resume
            steps: Original workflow steps

        Returns:
            Updated workflow state

        Raises:
            ValueError: If workflow cannot be resumed
        """
        state = await self.state_store.load_state(workflow_id)
        if state is None:
            raise ValueError(f"Workflow '{workflow_id}' not found")

        if state.status == WorkflowStatus.COMPLETED:
            raise ValueError(f"Workflow '{workflow_id}' already completed")

        completed_step_names = state.get_completed_steps()
        remaining_steps = [step for step in steps if step.name not in completed_step_names]

        if not remaining_steps:
            state.status = WorkflowStatus.COMPLETED
            await self.state_store.save_state(state)
            return state

        return await self.execute_workflow(workflow_id, remaining_steps, state.input_data)
