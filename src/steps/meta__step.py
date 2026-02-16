"""Meta description generation step."""

from typing import Any, Dict

from src.llm.llm__client import LLMMessage
from src.steps.step__base import Step


class MetaDescriptionStep(Step):
    """Generate SEO meta description based on blog post."""

    async def execute(self, context: Dict[str, Any]) -> Any:
        """
        Generate meta description.

        Args:
            context: Must contain 'blog_post' step output

        Returns:
            Dictionary with meta description content
        """
        self.validate_dependencies(context)

        if not self.llm_client:
            raise ValueError("MetaDescriptionStep requires an LLM client")

        blog_output = self.get_dependency_output(context, "blog_post")
        blog_title = blog_output.get("title", "")
        blog_content = blog_output.get("content", "")

        messages = [
            LLMMessage(
                role="system",
                content="You are an SEO expert. "
                "Create compelling meta descriptions under 160 characters.",
            ),
            LLMMessage(
                role="user",
                content=f"Create a meta description for this blog post:\n\n"
                f"Title: {blog_title}\n\n{blog_content[:500]}\n\n"
                f"Keep it under 160 characters and make it compelling for search results.",
            ),
        ]

        response = await self.llm_client.complete(messages, max_tokens=100)

        meta_description = response.content[:160]  # Enforce limit

        return {
            "meta_description": meta_description,
            "character_count": len(meta_description),
            "keywords": ["AI", "innovation", "technology", "business"],
        }
