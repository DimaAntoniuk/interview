"""Mock LLM client for testing without real API keys."""

import asyncio
import random
from typing import AsyncIterator

from src.llm.llm__client import LLMClient, LLMMessage, LLMResponse


class MockLLMClient(LLMClient):
    """Mock LLM client that generates realistic responses based on prompts."""

    def __init__(
        self,
        response_delay_ms: int = 100,
        stream_chunk_delay_ms: int = 20,
        fail_probability: float = 0.0,
    ) -> None:
        """
        Initialize mock LLM client.

        Args:
            response_delay_ms: Delay in milliseconds before returning response
            stream_chunk_delay_ms: Delay in milliseconds between stream chunks
            fail_probability: Probability of random failure (0.0 to 1.0)
        """
        self.response_delay_ms = response_delay_ms
        self.stream_chunk_delay_ms = stream_chunk_delay_ms
        self.fail_probability = fail_probability
        self._call_count = 0

    async def complete(self, messages: list[LLMMessage], max_tokens: int = 1000) -> LLMResponse:
        """Generate a mock completion."""
        await asyncio.sleep(self.response_delay_ms / 1000.0)
        self._call_count += 1

        if random.random() < self.fail_probability:
            raise Exception("Mock LLM failure (random)")

        content = self._generate_response(messages)
        input_tokens = sum(self.count_tokens(msg.content) for msg in messages)
        output_tokens = self.count_tokens(content)

        return LLMResponse(
            content=content,
            model="mock-gpt-4",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )

    async def stream(
        self, messages: list[LLMMessage], max_tokens: int = 1000
    ) -> AsyncIterator[str]:
        """Stream a mock completion."""
        self._call_count += 1

        if random.random() < self.fail_probability:
            raise Exception("Mock LLM failure (random)")

        content = self._generate_response(messages)
        words = content.split()

        for i, word in enumerate(words):
            await asyncio.sleep(self.stream_chunk_delay_ms / 1000.0)
            if i == len(words) - 1:
                yield word
            else:
                yield word + " "

    def count_tokens(self, text: str) -> int:
        """Approximate token count (rough estimate: 1 token ≈ 4 characters)."""
        return len(text) // 4

    def _generate_response(self, messages: list[LLMMessage]) -> str:
        """Generate contextual response based on the prompt."""
        last_message = messages[-1].content.lower() if messages else ""

        # Research step responses
        if "research" in last_message or "gather information" in last_message:
            return self._generate_research_response(last_message)

        # Blog post responses
        if "blog post" in last_message or "article" in last_message:
            return self._generate_blog_post_response(last_message)

        # Social media responses
        if "linkedin" in last_message:
            return self._generate_linkedin_response(last_message)
        if "twitter" in last_message or "tweet" in last_message:
            return self._generate_twitter_response(last_message)

        # Email newsletter responses
        if "email" in last_message or "newsletter" in last_message:
            return self._generate_email_response(last_message)

        # Meta description responses
        if "meta description" in last_message or "seo" in last_message:
            return self._generate_meta_description_response(last_message)

        # Quality check responses
        if "quality" in last_message or "review" in last_message or "check" in last_message:
            return self._generate_quality_check_response(last_message)

        # Format & publish responses
        if "format" in last_message or "publish" in last_message:
            return self._generate_format_response(last_message)

        # Default response
        return "This is a mock response from the LLM client."

    def _generate_research_response(self, prompt: str) -> str:
        """Generate research findings."""
        topic = self._extract_topic(prompt)
        return f"""# Research Findings: {topic}

## Key Insights
1. **Market Overview**: The {topic} market is experiencing significant growth with a projected CAGR of 25% over the next five years.

2. **Trends**: Key trends include increased adoption of AI-powered solutions, emphasis on data privacy, and growing demand for real-time analytics.

3. **Challenges**: Main challenges include regulatory compliance, integration complexity, and talent shortage.

4. **Opportunities**: Emerging opportunities in automation, personalization, and predictive analytics.

## Statistics
- 73% of organizations are investing in {topic} technologies
- Average ROI improvement of 40% reported by early adopters
- Market size expected to reach $15B by 2028

## Expert Quotes
"The future of {topic} lies in seamless integration with existing workflows" - Industry Expert

## Competitor Analysis
Leading players include established tech giants and innovative startups, each offering unique value propositions.
"""

    def _generate_blog_post_response(self, prompt: str) -> str:
        """Generate blog post content."""
        topic = self._extract_topic(prompt)
        return f"""# The Future of {topic}: A Comprehensive Guide

In today's rapidly evolving digital landscape, {topic} has emerged as a critical factor for business success. Organizations that embrace these innovations are seeing remarkable improvements in efficiency, customer satisfaction, and competitive advantage.

## Understanding {topic}

At its core, {topic} represents a fundamental shift in how we approach modern challenges. By leveraging cutting-edge technologies and data-driven insights, businesses can unlock new opportunities and drive meaningful outcomes.

## Key Benefits

**1. Enhanced Efficiency**
Implementing {topic} strategies can reduce operational costs by up to 30% while improving output quality. Automated workflows and intelligent systems handle routine tasks, freeing teams to focus on strategic initiatives.

**2. Better Decision Making**
With real-time analytics and predictive capabilities, leaders gain unprecedented visibility into business operations. This data-driven approach enables faster, more informed decisions.

**3. Competitive Advantage**
Organizations that successfully adopt {topic} gain significant market advantages. They can respond more quickly to customer needs, innovate faster, and deliver superior experiences.

## Implementation Best Practices

**Start Small, Think Big**
Begin with pilot projects that demonstrate clear value. Use these wins to build momentum and secure broader organizational buy-in.

**Focus on Integration**
Ensure new {topic} solutions integrate seamlessly with existing systems. A cohesive technology ecosystem maximizes value and minimizes disruption.

**Invest in Training**
Success requires skilled teams. Provide comprehensive training and ongoing support to ensure adoption and proficiency.

## Looking Ahead

The future of {topic} is bright, with emerging innovations promising even greater capabilities. Organizations that invest now will be well-positioned to capitalize on these advancements.

## Conclusion

{topic} is no longer optional—it's essential for staying competitive in today's market. By understanding its potential and implementing thoughtful strategies, businesses can achieve remarkable results and position themselves for long-term success.
"""

    def _generate_linkedin_response(self, prompt: str) -> str:
        """Generate LinkedIn post."""
        topic = self._extract_topic(prompt)
        return f"""🚀 The Future of {topic} is Here

I've been diving deep into {topic} lately, and the possibilities are incredible.

Here are 3 key insights that stood out:

1️⃣ Organizations implementing {topic} see 40% ROI improvements
2️⃣ The market is projected to reach $15B by 2028
3️⃣ 73% of companies are already investing in these technologies

The question isn't IF you should adopt {topic}, but WHEN.

What's your experience with {topic}? Drop your thoughts in the comments! 👇

#Innovation #Technology #{topic.replace(' ', '')} #DigitalTransformation #BusinessGrowth
"""

    def _generate_twitter_response(self, prompt: str) -> str:
        """Generate Twitter post."""
        topic = self._extract_topic(prompt)
        return f"""The {topic} revolution is here! 🚀

Companies adopting early are seeing:
✅ 40% ROI boost
✅ 30% cost reduction
✅ 10x faster insights

Don't get left behind.

#{topic.replace(' ', '')} #Innovation #Tech"""

    def _generate_email_response(self, prompt: str) -> str:
        """Generate email newsletter."""
        topic = self._extract_topic(prompt)
        return f"""Subject: Your Guide to {topic} Success

Hi there,

We're excited to share our latest insights on {topic}—a game-changing approach that's transforming how businesses operate.

**What You'll Learn:**

• Why {topic} matters now more than ever
• Real-world success stories and measurable results
• Practical steps to get started today
• Expert predictions for the future

**Key Takeaway:**
Organizations implementing {topic} strategies are seeing 40% improvements in ROI and 30% reductions in operational costs. These aren't small gains—they're transformative results.

**Take Action:**
Ready to explore what {topic} can do for your organization? Read our full blog post for a comprehensive guide with actionable insights.

[Read Full Article →]

**What's Next?**
Next week, we'll dive deeper into implementation strategies and share a step-by-step framework you can apply immediately.

Have questions about {topic}? Hit reply—we'd love to hear from you!

Best regards,
The Team

P.S. Don't miss our upcoming webinar on {topic} best practices. [Register here →]
"""

    def _generate_meta_description_response(self, prompt: str) -> str:
        """Generate meta description."""
        topic = self._extract_topic(prompt)
        return f"""Discover how {topic} is transforming business operations. Learn key strategies, benefits, and implementation best practices to drive 40% ROI improvements and gain competitive advantage."""

    def _generate_quality_check_response(self, prompt: str) -> str:
        """Generate quality check results."""
        return """# Quality Check Results

## Overall Assessment: ✅ APPROVED

### Tone & Voice Analysis
- **Professional**: ✅ Appropriate business tone maintained
- **Brand Voice**: ✅ Aligns with brand guidelines
- **Audience**: ✅ Language suitable for target audience

### Content Quality
- **Accuracy**: ✅ Information appears credible and well-researched
- **Clarity**: ✅ Clear, concise messaging
- **Value**: ✅ Provides actionable insights

### Technical Quality
- **Grammar**: ✅ No errors detected
- **Structure**: ✅ Well-organized with clear hierarchy
- **Formatting**: ✅ Proper use of headers and formatting

### SEO & Engagement
- **Keywords**: ✅ Relevant keywords naturally integrated
- **Readability**: ✅ Score 70/100 (Good)
- **Call-to-Action**: ✅ Clear next steps provided

### Recommendations
1. Consider adding 1-2 more statistics for credibility
2. Could enhance with a customer testimonial
3. Add internal links where relevant

**Status**: Ready for publication
"""

    def _generate_format_response(self, prompt: str) -> str:
        """Generate formatting results."""
        return """# Formatting Complete ✅

All content has been successfully formatted for target platforms:

## Blog Post
- ✅ HTML formatted with proper heading hierarchy
- ✅ Images optimized and alt text added
- ✅ Internal links inserted
- ✅ Meta tags configured

## LinkedIn Post
- ✅ Character count optimized (within limits)
- ✅ Hashtags added (8 relevant tags)
- ✅ Emojis strategically placed
- ✅ Image prepared (1200x628px)

## Twitter Post
- ✅ Character count: 267/280
- ✅ Hashtags optimized for reach
- ✅ Thread format prepared (if needed)

## Email Newsletter
- ✅ HTML email template applied
- ✅ Mobile-responsive design
- ✅ Preview text optimized
- ✅ Unsubscribe link added
- ✅ A/B test variants prepared

## Publishing Status
All content ready for scheduling/immediate publication.
"""

    def _extract_topic(self, text: str) -> str:
        """Extract topic from prompt text."""
        text_lower = text.lower()
        common_phrases = [
            "topic:",
            "about",
            "regarding",
            "on the subject of",
            "concerning",
        ]

        for phrase in common_phrases:
            if phrase in text_lower:
                parts = text_lower.split(phrase, 1)
                if len(parts) > 1:
                    topic = parts[1].strip().split()[0:5]
                    return " ".join(topic).strip('",.')

        # Default topic if extraction fails
        return "AI and Machine Learning"

    def reset_call_count(self) -> None:
        """Reset the call counter (useful for testing)."""
        self._call_count = 0

    def get_call_count(self) -> int:
        """Get the number of times the LLM was called."""
        return self._call_count
