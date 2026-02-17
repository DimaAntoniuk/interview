"""Tests for workflow executor."""

import asyncio
import unittest
from typing import Any, Dict

from src.steps.step__base import Step, condition_min_output_words
from src.workflow.workflow__executor import WorkflowExecutor
from src.workflow.workflow__state import InMemoryStateStore
from src.workflow.workflow__types import StepStatus, WorkflowStatus


class MockStep(Step):
    """Mock step for testing."""

    def __init__(
        self,
        name: str,
        depends_on: list[str] | None = None,
        output: Any = None,
        should_fail: bool = False,
        delay_ms: int = 10,
        condition: Any = None,
    ) -> None:
        super().__init__(name, depends_on, timeout_seconds=5.0, condition=condition)
        self.output_value = output or f"output_{name}"
        self.should_fail = should_fail
        self.delay_ms = delay_ms
        self.execution_count = 0

    async def execute(self, context: Dict[str, Any]) -> Any:
        """Execute mock step."""
        self.execution_count += 1
        await asyncio.sleep(self.delay_ms / 1000.0)

        if self.should_fail:
            raise Exception(f"Mock step {self.name} failed")

        return self.output_value


class TestWorkflowExecutor(unittest.TestCase):
    """Test cases for WorkflowExecutor."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.state_store = InMemoryStateStore()
        self.executor = WorkflowExecutor(
            state_store=self.state_store,
            max_parallel_steps=5,
            enable_progress_events=True,
        )

    async def test_simple_workflow(self) -> None:
        """Test execution of a simple linear workflow."""
        steps = [
            MockStep(name="step1", output="output1"),
            MockStep(name="step2", depends_on=["step1"], output="output2"),
            MockStep(name="step3", depends_on=["step2"], output="output3"),
        ]

        state = await self.executor.execute_workflow(
            workflow_id="test_simple",
            steps=steps,
            input_data={"test": "data"},
        )

        self.assertEqual(state.status, WorkflowStatus.COMPLETED)
        self.assertEqual(len(state.step_results), 3)
        self.assertEqual(state.step_results["step1"].status, StepStatus.COMPLETED)
        self.assertEqual(state.step_results["step1"].output, "output1")

    async def test_parallel_execution(self) -> None:
        """Test that independent steps execute in parallel."""
        steps = [
            MockStep(name="step1", output="output1"),
            MockStep(name="step2", depends_on=["step1"], output="output2", delay_ms=100),
            MockStep(name="step3", depends_on=["step1"], output="output3", delay_ms=100),
            MockStep(name="step4", depends_on=["step1"], output="output4", delay_ms=100),
        ]

        import time

        start = time.time()

        state = await self.executor.execute_workflow(
            workflow_id="test_parallel",
            steps=steps,
            input_data={},
        )

        duration = time.time() - start

        self.assertEqual(state.status, WorkflowStatus.COMPLETED)
        # Steps 2, 3, 4 should run in parallel, so total time should be ~100ms, not 300ms
        self.assertLess(duration, 0.25)  # Allow some overhead

    async def test_step_failure(self) -> None:
        """Test workflow handling when a step fails."""
        steps = [
            MockStep(name="step1", output="output1"),
            MockStep(name="step2", depends_on=["step1"], should_fail=True),
            MockStep(name="step3", depends_on=["step2"], output="output3"),
        ]

        with self.assertRaises(Exception) as ctx:
            await self.executor.execute_workflow(
                workflow_id="test_failure",
                steps=steps,
                input_data={},
            )

        self.assertIn("Failed steps", str(ctx.exception))

        # Load state and verify
        state = await self.state_store.load_state("test_failure")
        assert state is not None
        self.assertEqual(state.status, WorkflowStatus.FAILED)
        self.assertEqual(state.step_results["step1"].status, StepStatus.COMPLETED)
        self.assertEqual(state.step_results["step2"].status, StepStatus.FAILED)
        # Step 3 should not have executed
        self.assertNotIn("step3", state.step_results)

    async def test_circular_dependency_detection(self) -> None:
        """Test detection of circular dependencies."""
        steps = [
            MockStep(name="step1", depends_on=["step2"]),
            MockStep(name="step2", depends_on=["step1"]),
        ]

        with self.assertRaises(ValueError) as ctx:
            await self.executor.execute_workflow(
                workflow_id="test_circular",
                steps=steps,
                input_data={},
            )

        self.assertIn("Circular dependency", str(ctx.exception))

    async def test_missing_dependency(self) -> None:
        """Test handling of missing dependencies."""
        steps = [
            MockStep(name="step1", depends_on=["nonexistent"]),
        ]

        with self.assertRaises(ValueError) as ctx:
            await self.executor.execute_workflow(
                workflow_id="test_missing",
                steps=steps,
                input_data={},
            )

        self.assertIn("does not exist", str(ctx.exception))

    async def test_retry_logic(self) -> None:
        """Test retry logic for transient failures."""

        class RetryableStep(Step):
            def __init__(self) -> None:
                super().__init__(name="retry_step", max_retries=3)
                self.attempt = 0

            async def execute(self, context: Dict[str, Any]) -> Any:
                self.attempt += 1
                if self.attempt < 3:
                    raise Exception("Temporary failure")
                return "success"

            def is_retryable_error(self, error: Exception) -> bool:
                return "Temporary" in str(error)

        steps = [RetryableStep()]

        state = await self.executor.execute_workflow(
            workflow_id="test_retry",
            steps=steps,
            input_data={},
        )

        self.assertEqual(state.status, WorkflowStatus.COMPLETED)
        self.assertEqual(state.step_results["retry_step"].status, StepStatus.COMPLETED)
        self.assertEqual(state.step_results["retry_step"].attempts, 3)

    async def test_progress_events(self) -> None:
        """Test progress event emission."""
        steps = [
            MockStep(name="step1"),
            MockStep(name="step2", depends_on=["step1"]),
        ]

        await self.executor.execute_workflow(
            workflow_id="test_progress",
            steps=steps,
            input_data={},
        )

        events = self.executor.get_progress_events()
        self.assertGreater(len(events), 0)

        # Should have start and complete events for each step
        step1_events = [e for e in events if e.step_name == "step1"]
        self.assertEqual(len(step1_events), 2)  # start and complete

    async def test_context_passing(self) -> None:
        """Test that step outputs are passed through context."""

        class ContextCheckStep(Step):
            def __init__(self, name: str, depends_on: list[str] | None = None) -> None:
                super().__init__(name, depends_on)

            async def execute(self, context: Dict[str, Any]) -> Any:
                if self.depends_on:
                    # Verify we can access dependency outputs
                    dep_output = self.get_dependency_output(context, self.depends_on[0])
                    return f"processed_{dep_output}"
                return "initial_value"

        steps = [
            ContextCheckStep(name="step1"),
            ContextCheckStep(name="step2", depends_on=["step1"]),
        ]

        state = await self.executor.execute_workflow(
            workflow_id="test_context",
            steps=steps,
            input_data={},
        )

        self.assertEqual(state.step_results["step1"].output, "initial_value")
        self.assertEqual(state.step_results["step2"].output, "processed_initial_value")

    async def test_conditional_step_skipped_when_condition_not_met(self) -> None:
        """Test that a step with condition is skipped when condition is not met."""
        steps = [
            MockStep(name="step1", output="short"),  # 1 word
            MockStep(
                name="step2",
                depends_on=["step1"],
                output="output2",
                condition=condition_min_output_words("step1", min_words=5),
            ),
        ]

        state = await self.executor.execute_workflow(
            workflow_id="test_conditional_skip",
            steps=steps,
            input_data={},
        )

        self.assertEqual(state.status, WorkflowStatus.COMPLETED)
        self.assertEqual(state.step_results["step1"].status, StepStatus.COMPLETED)
        self.assertEqual(state.step_results["step2"].status, StepStatus.SKIPPED)
        self.assertIsNone(state.step_results["step2"].output)
        self.assertEqual(steps[1].execution_count, 0)

    async def test_conditional_step_runs_when_condition_met(self) -> None:
        """Test that a step with condition runs when condition is met."""
        steps = [
            MockStep(name="step1", output="one two three four five six"),  # 6 words
            MockStep(
                name="step2",
                depends_on=["step1"],
                output="output2",
                condition=condition_min_output_words("step1", min_words=5),
            ),
        ]

        state = await self.executor.execute_workflow(
            workflow_id="test_conditional_run",
            steps=steps,
            input_data={},
        )

        self.assertEqual(state.status, WorkflowStatus.COMPLETED)
        self.assertEqual(state.step_results["step1"].status, StepStatus.COMPLETED)
        self.assertEqual(state.step_results["step2"].status, StepStatus.COMPLETED)
        self.assertEqual(state.step_results["step2"].output, "output2")
        self.assertEqual(steps[1].execution_count, 1)

    async def test_skipped_step_unblocks_dependents(self) -> None:
        """Test that dependents of a skipped step can still run (dependency resolution)."""
        steps = [
            MockStep(name="step1", output="x"),  # 1 word
            MockStep(
                name="step2",
                depends_on=["step1"],
                output="skipped",
                condition=condition_min_output_words("step1", min_words=10),
            ),
            MockStep(name="step3", depends_on=["step2"], output="after_skip"),
        ]

        state = await self.executor.execute_workflow(
            workflow_id="test_skip_deps",
            steps=steps,
            input_data={},
        )

        self.assertEqual(state.status, WorkflowStatus.COMPLETED)
        self.assertEqual(state.step_results["step2"].status, StepStatus.SKIPPED)
        self.assertEqual(state.step_results["step3"].status, StepStatus.COMPLETED)
        self.assertEqual(state.step_results["step3"].output, "after_skip")


if __name__ == "__main__":
    unittest.main()
