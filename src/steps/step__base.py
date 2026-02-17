"""Base class for workflow steps."""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional

from src.llm.llm__client import LLMClient


def condition_min_output_words(step_name: str, min_words: int) -> Callable[[Dict[str, Any]], bool]:
    """
    Build a condition that is met when a dependency step's output has at least min_words.

    Args:
        step_name: Name of the step whose output to count words from
        min_words: Minimum number of words required

    Returns:
        A callable(context) that returns True if condition is met
    """
    def _check(context: Dict[str, Any]) -> bool:
        step_outputs = context.get("step_outputs", {})
        if step_name not in step_outputs:
            return False
        output = step_outputs[step_name]
        if output is None:
            return False
        text = str(output).strip()
        word_count = len(text.split()) if text else 0
        return word_count >= min_words

    return _check


class Step(ABC):
    """Base class for all workflow steps."""

    def __init__(
        self,
        name: str,
        depends_on: Optional[List[str]] = None,
        timeout_seconds: float = 30.0,
        max_retries: int = 3,
        llm_client: Optional[LLMClient] = None,
        condition: Optional[Callable[[Dict[str, Any]], bool]] = None,
    ) -> None:
        """
        Initialize a workflow step.

        Args:
            name: Unique name for this step
            depends_on: List of step names this step depends on
            timeout_seconds: Maximum execution time in seconds
            max_retries: Maximum number of retry attempts
            llm_client: LLM client for AI operations
            condition: Optional callable(context) -> bool; if False, step is skipped
        """
        self.name = name
        self.depends_on = depends_on or []
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.llm_client = llm_client
        self.condition = condition

    def is_condition_met(self, context: Dict[str, Any]) -> bool:
        """
        Return whether the step's condition is satisfied (and thus the step should run).

        If no condition is set, returns True.

        Args:
            context: Execution context with input_data and step_outputs

        Returns:
            True if the step should execute, False if it should be skipped
        """
        if self.condition is None:
            return True
        return self.condition(context)

    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Any:
        """
        Execute the step with access to previous step results.

        Args:
            context: Dictionary containing:
                - input_data: Original workflow input
                - step_outputs: Dictionary of {step_name: output} from completed steps

        Returns:
            The output of this step (will be available to dependent steps)

        Raises:
            Exception: If step execution fails
        """
        pass

    def is_retryable_error(self, error: Exception) -> bool:
        """
        Determine if an error should trigger a retry.

        Override this method to customize retry logic for specific error types.

        Args:
            error: The exception that occurred

        Returns:
            True if the step should be retried, False otherwise
        """
        error_str = str(error).lower()

        # Retryable errors
        retryable_patterns = [
            "timeout",
            "connection",
            "rate limit",
            "429",
            "500",
            "502",
            "503",
            "504",
            "temporary",
            "transient",
        ]

        # Non-retryable errors
        non_retryable_patterns = [
            "authentication",
            "permission",
            "not found",
            "400",
            "401",
            "403",
            "404",
            "invalid",
        ]

        # Check non-retryable first
        if any(pattern in error_str for pattern in non_retryable_patterns):
            return False

        # Check retryable
        if any(pattern in error_str for pattern in retryable_patterns):
            return True

        # Default: don't retry
        return False

    def validate_dependencies(self, context: Dict[str, Any]) -> None:
        """
        Validate that all dependencies are satisfied.

        Args:
            context: Execution context

        Raises:
            ValueError: If required dependencies are missing
        """
        step_outputs = context.get("step_outputs", {})
        for dep in self.depends_on:
            if dep not in step_outputs:
                raise ValueError(f"Step '{self.name}' depends on '{dep}' which is not available")

    def get_dependency_output(self, context: Dict[str, Any], step_name: str) -> Any:
        """
        Get the output of a dependency step.

        Args:
            context: Execution context
            step_name: Name of the dependency step

        Returns:
            Output of the dependency step

        Raises:
            ValueError: If dependency is not found
        """
        step_outputs = context.get("step_outputs", {})
        if step_name not in step_outputs:
            raise ValueError(f"Step '{step_name}' output not found in context")
        return step_outputs[step_name]

    def __repr__(self) -> str:
        """String representation of the step."""
        deps = f", depends_on={self.depends_on}" if self.depends_on else ""
        return f"{self.__class__.__name__}(name='{self.name}'{deps})"
