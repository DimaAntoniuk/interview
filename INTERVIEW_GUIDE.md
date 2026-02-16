# Interview Guide: Multi-Agent Workflow Orchestration

## Overview

This repository contains a **partially implemented** multi-agent workflow orchestration framework. Your task is to review the architecture, complete missing components, and demonstrate your understanding of async patterns, error handling, and system design.

**Time**: 1 hour
**Goal**: Show your design thinking, implementation skills, and ability to discuss tradeoffs

---

## Setup (5 minutes)

```bash
# Install dependencies
poetry install

# Verify setup
poetry run python examples/run_workflow.py

# Run tests
./test.sh

# Check types
./check_types.sh
```

**Expected Result**: The example workflow should execute successfully, showing content generation for a blog post, social media, email, etc.

---

## Part 1: Code Review & Architecture Discussion (15 minutes)

### Task
Review the existing codebase and be prepared to discuss:

1. **Architecture**
   - What are the key components? (Executor, StateStore, Steps, LLM Client)
   - How are dependencies represented and resolved?
   - How does parallelization work?

2. **Design Decisions**
   - Why separate `Step` from `WorkflowExecutor`?
   - Why use a `StateStore` abstraction?
   - What are the tradeoffs of in-memory vs persistent state?

3. **Error Handling**
   - How are retries implemented?
   - What makes an error retryable vs non-retryable?
   - What happens when a step fails?

4. **Scalability**
   - Can this handle 100+ concurrent workflows?
   - What would need to change for production?
   - What are the bottlenecks?

### Discussion Points

- **Dependency Graph**: How is the DAG built and validated?
- **Parallelization**: How does the executor determine which steps can run in parallel?
- **State Management**: When is state saved? What happens if the process crashes?
- **Progress Tracking**: How would you stream progress to a user in real-time?

---

## Part 2: Implementation Tasks (Choose 1-2 based on time)

### Task Option A: Add a Progress Listener (20 minutes)

**Goal**: Implement a real-time progress listener that streams updates via WebSocket or SSE.

**Requirements**:
- Create a `WebSocketProgressListener` class
- Implement `on_step_start`, `on_step_complete`, `on_workflow_complete` methods
- Stream progress events to connected clients
- Handle connection failures gracefully

**Files to modify/create**:
- `src/workflow/progress__listener.py` (new file)
- Update `workflow__executor.py` to use the listener

**Discussion**:
- How do you handle multiple concurrent workflows?
- What if the WebSocket connection drops mid-workflow?
- How do you ensure events are ordered correctly?

---

### Task Option B: Implement Workflow Resumability (20 minutes)

**Goal**: Enhance the `resume_workflow` method to properly handle partial failures.

**Current State**: The method exists but is not fully implemented.

**Requirements**:
- Resume from the last successful checkpoint
- Re-execute failed steps only
- Invalidate dependent steps if a parent step is re-executed
- Handle state consistency

**Files to modify**:
- `src/workflow/workflow__executor.py` (enhance `resume_workflow`)
- Add tests in `workflow__executor__spec.py`

**Discussion**:
- How do you ensure idempotency?
- What if step output changed on retry?
- How do you handle non-deterministic steps?

---

### Task Option C: Add Conditional Step Execution (20 minutes)

**Goal**: Allow steps to be executed conditionally based on previous outputs.

**Requirements**:
- Add a `condition` parameter to `Step`
- Implement condition evaluation in the executor
- Skip steps whose conditions aren't met
- Update dependency resolution to handle skipped steps

**Example**:
```python
QualityCheckStep(
    name="quality_check",
    depends_on=["blog_post"],
    condition=lambda context: context["blog_post"]["word_count"] > 500
)
```

**Files to modify**:
- `src/steps/step__base.py`
- `src/workflow/workflow__executor.py`
- Add tests

**Discussion**:
- How do you handle dependent steps when a step is skipped?
- Should skipped steps count as completed or failed?
- How does this affect the dependency graph?

---

### Task Option D: Add Timeout and Cancellation (20 minutes)

**Goal**: Implement workflow-level timeout and graceful cancellation.

**Requirements**:
- Add `workflow_timeout_seconds` parameter to executor
- Cancel running steps when timeout is reached
- Implement `cancel_workflow` method
- Gracefully stop execution and save state

**Files to modify**:
- `src/workflow/workflow__executor.py`
- Update workflow types if needed
- Add tests

**Discussion**:
- How do you cancel a running async task?
- What happens to steps in progress when cancelled?
- Should you retry on timeout?

---

## Part 3: System Design Discussion (15 minutes)

### Scenario 1: Scaling to 10,000 Concurrent Workflows

**Question**: How would you modify this architecture to handle 10,000 concurrent workflows?

**Discussion Points**:
- Distributed execution (Celery, Temporal, Airflow)
- Message queues for coordination
- Persistent state storage (PostgreSQL, Redis)
- Worker pools and resource management
- Cost optimization (LLM API calls)

---

### Scenario 2: Production Monitoring

**Question**: What metrics and logs would you add for production?

**Discussion Points**:
- Success/failure rate per step
- Step duration percentiles (p50, p95, p99)
- Queue depth and wait time
- Error types and frequencies
- Cost per workflow
- Distributed tracing (OpenTelemetry)

---

### Scenario 3: Workflow Versioning

**Question**: How do you handle workflow definition changes while workflows are running?

**Discussion Points**:
- Versioning strategy
- Backward compatibility
- Migration path for running workflows
- Schema evolution

---

### Scenario 4: Human-in-the-Loop

**Question**: How would you implement a "pause for approval" step?

**Discussion Points**:
- Workflow suspension
- State persistence
- Resuming after hours/days
- Timeout for approvals
- Who can approve?

---

## Part 4: Code Walkthrough (10 minutes)

Walk through your implementation:

1. **What did you build?**
   - High-level overview
   - Key design decisions

2. **How does it work?**
   - Code walkthrough
   - Integration points

3. **What tradeoffs did you make?**
   - Performance vs simplicity
   - Memory vs disk
   - Flexibility vs constraints

4. **What would you do differently with more time?**
   - Nice-to-have features
   - Technical debt
   - Alternative approaches

---

## Evaluation Criteria

### Architecture & Design (40%)
- Clear understanding of existing architecture
- Thoughtful design decisions
- Proper separation of concerns
- Scalability considerations

### Implementation (30%)
- Clean, readable code
- Proper async patterns
- Error handling
- Type hints and documentation

### Problem Solving (20%)
- Identifies edge cases
- Proposes solutions
- Asks clarifying questions
- Discusses alternatives

### Communication (10%)
- Explains decisions clearly
- Articulates tradeoffs
- Responds to challenges
- Collaborative approach

---

## Tips for Success

1. **Ask Questions**: Clarify requirements before diving in
2. **Think Out Loud**: Share your thought process
3. **Start Simple**: Get a working solution first, then enhance
4. **Use AI Tools**: You're encouraged to use Claude/ChatGPT/Copilot for boilerplate
5. **Focus on Design**: Spend more time on "why" than "how"
6. **Test Your Code**: Run tests frequently to catch issues early
7. **Manage Time**: Don't get stuck on one thing—move on and come back

---

## Common Pitfalls to Avoid

- ❌ Not reading the existing code carefully
- ❌ Overcomplicating the solution
- ❌ Ignoring error handling
- ❌ Poor type hints or no documentation
- ❌ Not testing the implementation
- ❌ Not discussing tradeoffs
- ❌ Getting stuck on syntax instead of design

---

## Resources

- **LlamaIndex Workflows**: https://docs.llamaindex.ai/en/stable/module_guides/workflow/
- **Python asyncio**: https://docs.python.org/3/library/asyncio.html
- **Temporal (workflow engine)**: https://temporal.io/
- **Celery (task queue)**: https://docs.celeryq.dev/

---

## After the Interview

You'll be evaluated on:

1. **Technical Skills**: Code quality, architecture, async patterns
2. **System Design**: Scalability, observability, production concerns
3. **Communication**: Explaining decisions, articulating tradeoffs
4. **Problem Solving**: Handling edge cases, asking questions
5. **AI/LLM Knowledge**: Understanding of LLM patterns, cost optimization

Good luck! 🚀
