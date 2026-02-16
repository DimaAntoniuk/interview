"""Email newsletter generation step."""

from typing import Any, Dict

from src.llm.llm__client import LLMMessage
from src.steps.step__base import Step


class EmailNewsletterStep(Step):
    """Generate email newsletter based on blog post."""

    async def execute(self, context: Dict[str, Any]) -> Any:
        """
        Generate email newsletter.

        Args:
            context: Must contain 'blog_post' step output

        Returns:
            Dictionary with email newsletter content
        """
        self.validate_dependencies(context)

        if not self.llm_client:
            raise ValueError("EmailNewsletterStep requires an LLM client")

        blog_output = self.get_dependency_output(context, "blog_post")
        blog_title = blog_output.get("title", "")
        blog_content = blog_output.get("content", "")

        messages = [
            LLMMessage(
                role="system",
                content="You are an email marketing expert. Create engaging newsletters.",
            ),
            LLMMessage(
                role="user",
                content=f"Create an email newsletter based on this blog post:\n\n"
                f"Title: {blog_title}\n\n{blog_content[:1500]}\n\n"
                f"Include subject line, preview text, and a clear call-to-action.",
            ),
        ]

        response = await self.llm_client.complete(messages, max_tokens=1500)

        return {
            "subject": f"Your Guide to {blog_title.split(':')[0]}",
            "preview_text": "Discover the latest insights and strategies...",
            "content": response.content,
            "cta": "Read Full Article",
            "cta_url": "/blog/latest",
        }
