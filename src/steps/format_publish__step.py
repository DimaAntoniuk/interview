"""Format and publish step for preparing content for publication."""

from typing import Any, Dict

from src.llm.llm__client import LLMMessage
from src.steps.step__base import Step


class FormatPublishStep(Step):
    """Format all content for different platforms and prepare for publication."""

    async def execute(self, context: Dict[str, Any]) -> Any:
        """
        Format and prepare content for publication.

        Args:
            context: Must contain quality_check step output and all content steps

        Returns:
            Dictionary with formatted content ready for publication
        """
        self.validate_dependencies(context)

        if not self.llm_client:
            raise ValueError("FormatPublishStep requires an LLM client")

        quality_check = self.get_dependency_output(context, "quality_check")

        if quality_check.get("status") != "approved":
            raise ValueError("Content did not pass quality check")

        step_outputs = context.get("step_outputs", {})

        messages = [
            LLMMessage(
                role="system",
                content="You are a content formatting expert. Prepare content for publication.",
            ),
            LLMMessage(
                role="user",
                content="Format the approved content for publication across all platforms. "
                "Provide a summary of formatting tasks completed.",
            ),
        ]

        response = await self.llm_client.complete(messages, max_tokens=800)

        return {
            "status": "ready_for_publication",
            "formatted_content": {
                "blog": {
                    "html": step_outputs.get("blog_post", {}).get("content", ""),
                    "status": "formatted",
                },
                "linkedin": {
                    "text": step_outputs.get("linkedin", {}).get("content", ""),
                    "status": "formatted",
                },
                "twitter": {
                    "text": step_outputs.get("twitter", {}).get("content", ""),
                    "status": "formatted",
                },
                "email": {
                    "html": step_outputs.get("email", {}).get("content", ""),
                    "subject": step_outputs.get("email", {}).get("subject", ""),
                    "status": "formatted",
                },
            },
            "publishing_summary": response.content,
            "scheduled_time": None,  # Can be set for scheduled publishing
        }
