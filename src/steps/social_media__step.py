"""Social media post generation steps."""

from typing import Any, Dict

from src.llm.llm__client import LLMMessage
from src.steps.step__base import Step


class LinkedInPostStep(Step):
    """Generate LinkedIn post based on blog post."""

    async def execute(self, context: Dict[str, Any]) -> Any:
        """
        Generate LinkedIn post.

        Args:
            context: Must contain 'blog_post' step output

        Returns:
            Dictionary with LinkedIn post content
        """
        self.validate_dependencies(context)

        if not self.llm_client:
            raise ValueError("LinkedInPostStep requires an LLM client")

        blog_output = self.get_dependency_output(context, "blog_post")
        blog_content = blog_output.get("content", "")

        messages = [
            LLMMessage(
                role="system",
                content="You are a LinkedIn content expert. "
                "Create engaging professional posts.",
            ),
            LLMMessage(
                role="user",
                content=(
                    f"Create a LinkedIn post based on this blog content:\n\n"
                    f"{blog_content[:1000]}\n\n"
                    f"Make it professional, engaging, and include relevant hashtags."
                ),
            ),
        ]

        response = await self.llm_client.complete(messages, max_tokens=500)

        return {
            "platform": "linkedin",
            "content": response.content,
            "hashtags": ["#Innovation", "#Technology", "#BusinessGrowth"],
            "character_count": len(response.content),
        }


class TwitterPostStep(Step):
    """Generate Twitter post based on blog post."""

    async def execute(self, context: Dict[str, Any]) -> Any:
        """
        Generate Twitter post.

        Args:
            context: Must contain 'blog_post' step output

        Returns:
            Dictionary with Twitter post content
        """
        self.validate_dependencies(context)

        if not self.llm_client:
            raise ValueError("TwitterPostStep requires an LLM client")

        blog_output = self.get_dependency_output(context, "blog_post")
        blog_content = blog_output.get("content", "")

        messages = [
            LLMMessage(
                role="system",
                content="You are a Twitter content expert. Create concise, impactful tweets.",
            ),
            LLMMessage(
                role="user",
                content=f"Create a Twitter post (max 280 chars) based on this content:\n\n"
                f"{blog_content[:500]}\n\n"
                f"Make it engaging and include hashtags.",
            ),
        ]

        response = await self.llm_client.complete(messages, max_tokens=200)

        return {
            "platform": "twitter",
            "content": response.content,
            "hashtags": ["#Tech", "#Innovation"],
            "character_count": len(response.content),
        }
