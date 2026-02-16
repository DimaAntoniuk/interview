"""Example workflow execution for content generation pipeline."""

import asyncio
import json

from src.llm.llm__mock import MockLLMClient
from src.steps.blog_post__step import BlogPostStep
from src.steps.email__step import EmailNewsletterStep
from src.steps.format_publish__step import FormatPublishStep
from src.steps.meta__step import MetaDescriptionStep
from src.steps.quality_check__step import QualityCheckStep
from src.steps.research__step import ResearchStep
from src.steps.social_media__step import LinkedInPostStep, TwitterPostStep
from src.workflow.workflow__executor import WorkflowExecutor
from src.workflow.workflow__state import InMemoryStateStore


async def run_content_generation_workflow() -> None:
    """Run the complete content generation workflow."""
    print("🚀 Starting Content Generation Workflow\n")
    print("=" * 70)

    # Initialize mock LLM client
    llm_client = MockLLMClient(
        response_delay_ms=50,  # Faster for demo
        stream_chunk_delay_ms=10,
        fail_probability=0.0,  # No failures for demo
    )

    # Define workflow steps with dependencies
    steps = [
        # Step 1: Research (no dependencies)
        ResearchStep(
            name="research",
            depends_on=[],
            timeout_seconds=15.0,
            llm_client=llm_client,
        ),
        # Step 2: Blog Post (depends on Research)
        BlogPostStep(
            name="blog_post",
            depends_on=["research"],
            timeout_seconds=30.0,
            llm_client=llm_client,
        ),
        # Steps 3-6: Parallel content generation (all depend on Blog Post)
        LinkedInPostStep(
            name="linkedin",
            depends_on=["blog_post"],
            timeout_seconds=20.0,
            llm_client=llm_client,
        ),
        TwitterPostStep(
            name="twitter",
            depends_on=["blog_post"],
            timeout_seconds=20.0,
            llm_client=llm_client,
        ),
        EmailNewsletterStep(
            name="email",
            depends_on=["blog_post"],
            timeout_seconds=20.0,
            llm_client=llm_client,
        ),
        MetaDescriptionStep(
            name="meta",
            depends_on=["blog_post"],
            timeout_seconds=20.0,
            llm_client=llm_client,
        ),
        # Step 7: Quality Check (depends on all content)
        QualityCheckStep(
            name="quality_check",
            depends_on=["blog_post", "linkedin", "twitter", "email", "meta"],
            timeout_seconds=10.0,
            llm_client=llm_client,
        ),
        # Step 8: Format & Publish (depends on Quality Check)
        FormatPublishStep(
            name="format_publish",
            depends_on=["quality_check"],
            timeout_seconds=5.0,
            llm_client=llm_client,
        ),
    ]

    # Initialize workflow executor
    state_store = InMemoryStateStore()
    executor = WorkflowExecutor(
        state_store=state_store,
        max_parallel_steps=4,  # Allow up to 4 steps to run in parallel
        enable_progress_events=True,
    )

    # Execute workflow
    workflow_id = "content_gen_demo_001"
    input_data = {
        "topic": "AI-Powered Marketing Automation",
        "target_audience": "B2B SaaS companies",
        "tone": "professional yet approachable",
    }

    print(f"\n📋 Workflow ID: {workflow_id}")
    print(f"📝 Topic: {input_data['topic']}")
    print(f"🎯 Target Audience: {input_data['target_audience']}\n")
    print("=" * 70)

    try:
        # Execute the workflow
        print("\n⚙️  Executing workflow steps...\n")

        state = await executor.execute_workflow(
            workflow_id=workflow_id,
            steps=steps,
            input_data=input_data,
        )

        # Display results
        print("\n" + "=" * 70)
        print("✅ WORKFLOW COMPLETED SUCCESSFULLY\n")

        print(f"⏱️  Duration: {state.duration_ms:.0f}ms")
        print(f"📊 Status: {state.status.value}")
        print(f"🔢 Completed Steps: {len(state.get_completed_steps())}/{len(steps)}")
        print(f"❌ Failed Steps: {len(state.get_failed_steps())}")

        # Show step results summary
        print("\n📈 Step Execution Summary:")
        print("-" * 70)

        for step_name, result in state.step_results.items():
            status_emoji = "✅" if result.status.value == "completed" else "❌"
            print(
                f"{status_emoji} {step_name:20} | "
                f"Status: {result.status.value:10} | "
                f"Duration: {result.duration_ms:6.0f}ms | "
                f"Attempts: {result.attempts}"
            )

        # Display sample outputs
        print("\n" + "=" * 70)
        print("📄 SAMPLE OUTPUTS\n")

        # Research findings
        if "research" in state.step_results:
            research_output = state.step_results["research"].output
            print("🔬 Research Findings:")
            print("-" * 70)
            findings = research_output.get("research_findings", "")[:300]
            print(findings + "...\n")

        # Blog post
        if "blog_post" in state.step_results:
            blog_output = state.step_results["blog_post"].output
            print("📝 Blog Post:")
            print("-" * 70)
            print(f"Title: {blog_output.get('title')}")
            print(f"Word Count: {blog_output.get('word_count')}")
            print(f"Read Time: {blog_output.get('estimated_read_time')} min")
            content = blog_output.get("content", "")[:200]
            print(f"Preview: {content}...\n")

        # LinkedIn post
        if "linkedin" in state.step_results:
            linkedin_output = state.step_results["linkedin"].output
            print("💼 LinkedIn Post:")
            print("-" * 70)
            print(linkedin_output.get("content", "")[:200] + "...\n")

        # Twitter post
        if "twitter" in state.step_results:
            twitter_output = state.step_results["twitter"].output
            print("🐦 Twitter Post:")
            print("-" * 70)
            print(twitter_output.get("content", "") + "\n")

        # Email newsletter
        if "email" in state.step_results:
            email_output = state.step_results["email"].output
            print("📧 Email Newsletter:")
            print("-" * 70)
            print(f"Subject: {email_output.get('subject')}")
            print(f"CTA: {email_output.get('cta')}\n")

        # Meta description
        if "meta" in state.step_results:
            meta_output = state.step_results["meta"].output
            print("🔍 Meta Description:")
            print("-" * 70)
            print(meta_output.get("meta_description", "") + "\n")

        # Quality check
        if "quality_check" in state.step_results:
            quality_output = state.step_results["quality_check"].output
            print("✓ Quality Check:")
            print("-" * 70)
            print(f"Status: {quality_output.get('status')}")
            print(f"Quality Score: {quality_output.get('quality_score'):.2%}\n")

        # Format & Publish
        if "format_publish" in state.step_results:
            publish_output = state.step_results["format_publish"].output
            print("🚀 Publishing Status:")
            print("-" * 70)
            print(f"Status: {publish_output.get('status')}")
            formatted = publish_output.get("formatted_content", {})
            print(f"Platforms Ready: {len(formatted)} (Blog, LinkedIn, Twitter, Email)\n")

        # Progress events
        if executor.get_progress_events():
            print("\n" + "=" * 70)
            print("📊 PROGRESS EVENTS\n")
            for event in executor.get_progress_events()[:10]:  # Show first 10
                print(f"  • {event.event_type:15} | {event.step_name:20} | {event.step_status}")

        # LLM stats
        print("\n" + "=" * 70)
        print("🤖 LLM STATISTICS\n")
        print(f"Total LLM Calls: {llm_client.get_call_count()}")
        print(f"Average Calls Per Step: {llm_client.get_call_count() / len(steps):.1f}")

        print("\n" + "=" * 70)
        print("✨ All content is ready for publication!\n")

        # Save state to JSON for inspection
        state_dict = {
            "workflow_id": state.workflow_id,
            "status": state.status.value,
            "duration_ms": state.duration_ms,
            "completed_steps": state.get_completed_steps(),
            "failed_steps": state.get_failed_steps(),
        }

        with open("workflow_result.json", "w") as f:
            json.dump(state_dict, f, indent=2)

        print("💾 Workflow state saved to: workflow_result.json\n")

    except Exception as e:
        print(f"\n❌ WORKFLOW FAILED\n")
        print(f"Error: {str(e)}\n")
        raise


async def main() -> None:
    """Main entry point."""
    await run_content_generation_workflow()


if __name__ == "__main__":
    asyncio.run(main())
