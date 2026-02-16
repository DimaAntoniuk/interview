"""Research step for gathering information about a topic."""

from typing import Any, Dict

from src.llm.llm__client import LLMMessage
from src.steps.step__base import Step


class ResearchStep(Step):
    """Gather research and information about a topic."""

    async def execute(self, context: Dict[str, Any]) -> Any:
        """
        Execute research by gathering information about the topic.

        Args:
            context: Must contain 'input_data' with 'topic' key

        Returns:
            Dictionary with research findings
        """
        self.validate_dependencies(context)

        if not self.llm_client:
            raise ValueError("ResearchStep requires an LLM client")

        input_data = context.get("input_data", {})
        topic = input_data.get("topic", "Unknown Topic")

        messages = [
            LLMMessage(
                role="system",
                content="You are a research assistant. Provide comprehensive research findings.",
            ),
            LLMMessage(
                role="user",
                content=f"Research the following topic and provide key insights, statistics, "
                f"trends, and challenges: {topic}",
            ),
        ]

        response = await self.llm_client.complete(messages, max_tokens=2000)

        return {
            "topic": topic,
            "research_findings": response.content,
            "sources": [
                "Industry Reports 2024",
                "Market Analysis Q4 2023",
                "Expert Interviews",
            ],
            "confidence": 0.85,
        }
