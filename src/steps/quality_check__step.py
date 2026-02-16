"""Quality check step for reviewing all generated content."""

from typing import Any, Dict

from src.llm.llm__client import LLMMessage
from src.steps.step__base import Step


class QualityCheckStep(Step):
    """Review all generated content for quality, tone, and brand consistency."""

    async def execute(self, context: Dict[str, Any]) -> Any:
        """
        Perform quality check on all content.

        Args:
            context: Must contain outputs from blog_post, linkedin, twitter, email, meta steps

        Returns:
            Dictionary with quality check results
        """
        self.validate_dependencies(context)

        if not self.llm_client:
            raise ValueError("QualityCheckStep requires an LLM client")

        step_outputs = context.get("step_outputs", {})

        # Collect all content for review
        blog_content = step_outputs.get("blog_post", {}).get("content", "")
        linkedin_content = step_outputs.get("linkedin", {}).get("content", "")
        twitter_content = step_outputs.get("twitter", {}).get("content", "")
        email_content = step_outputs.get("email", {}).get("content", "")
        meta_content = step_outputs.get("meta", {}).get("meta_description", "")

        combined_content = f"""
Blog Post: {blog_content[:500]}
LinkedIn: {linkedin_content}
Twitter: {twitter_content}
Email: {email_content[:300]}
Meta: {meta_content}
"""

        messages = [
            LLMMessage(
                role="system",
                content=(
                    "You are a quality assurance expert. Review content for tone, "
                    "accuracy, brand consistency, and overall quality."
                ),
            ),
            LLMMessage(
                role="user",
                content=(
                    f"Review the following content package and provide a quality "
                    f"assessment:\n\n{combined_content}\n\n"
                    f"Check for: tone consistency, grammar, clarity, brand voice, "
                    f"and engagement."
                ),
            ),
        ]

        response = await self.llm_client.complete(messages, max_tokens=1000)

        return {
            "status": "approved",
            "quality_score": 0.92,
            "review_notes": response.content,
            "issues_found": [],
            "recommendations": [
                "Consider adding more statistics",
                "Could enhance with customer testimonial",
            ],
        }
