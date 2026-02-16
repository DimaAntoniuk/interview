"""Blog post generation step."""

from typing import Any, Dict

from src.llm.llm__client import LLMMessage
from src.steps.step__base import Step


class BlogPostStep(Step):
    """Generate a comprehensive blog post based on research findings."""

    async def execute(self, context: Dict[str, Any]) -> Any:
        """
        Generate blog post content.

        Args:
            context: Must contain 'research' step output

        Returns:
            Dictionary with blog post content
        """
        self.validate_dependencies(context)

        if not self.llm_client:
            raise ValueError("BlogPostStep requires an LLM client")

        research_output = self.get_dependency_output(context, "research")
        topic = research_output.get("topic", "Unknown Topic")
        research_findings = research_output.get("research_findings", "")

        messages = [
            LLMMessage(
                role="system",
                content="You are an expert content writer. "
                "Create engaging, informative blog posts.",
            ),
            LLMMessage(
                role="user",
                content=f"Write a comprehensive blog post about {topic}. "
                f"Use the following research:\n\n{research_findings}\n\n"
                f"Make it engaging, well-structured, and actionable.",
            ),
        ]

        response = await self.llm_client.complete(messages, max_tokens=3000)

        return {
            "title": f"The Future of {topic}: A Comprehensive Guide",
            "content": response.content,
            "word_count": len(response.content.split()),
            "estimated_read_time": len(response.content.split()) // 200,  # minutes
        }
